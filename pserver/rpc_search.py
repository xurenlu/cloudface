#!/home/renlu/bin/bin/python
#coding:utf-8
__usage__ = "%prog -n <num>"
__version__ = "$Id: server.py 28 2008-11-03 21:05:15Z matt@ansonia01.com $"
__author__ = "Matt Kangas <matt@daylife.com>"
import sys,os
#from phprpc import PHPRPC_Server # 引入 PHPRPC Server
#from phprpc.phprpc import PHPRPC_WSGIApplication, UrlMapMiddleware, PHPRPC_Server
import datetime
#from pymmseg import mmseg
#import xappy
#from flup.server.fcgi import WSGIServer
import optparse
import yaml
import xapian
import _scws

#FCGI_LISTEN_ADDRESS = ('localhost', 9000)
FCGI_SOCKET_DIR = '/tmp'
FCGI_SOCKET_UMASK = 0111
DB_PREFIX="./"

#mmseg.dict_load_defaults()

'''
#create_index( "./datadir/", ["text"], ["author","desc","text","categoryid"], ["categoryid"])
#index_data("./datadir/", "book3", { "author":"xurenlu", "desc":"这是一本好书", "text":"故事发生在20年以前", "categoryid":123 },["desc","text"])
#index_data("./datadir/", "book2", { "author":"xurenlu", "desc":"好书不多见", "text":"故事很不错哟12块钱", "categoryid":12},["desc","text"])
report=search_result_report("./datadir/","故事")
print(report)
sout=(search("./datadir/","故事",0,10))
print(sout)
for item in sout:
    for key in item.data:
        print key,":",item.data[key][0]
'''
def _get_socket_path(name, server_number):
    """return socket file path for fastcgi"""
    return os.path.join(FCGI_SOCKET_DIR, 'fcgi-%s-%s.socket' % (name, server_number))

def _get_rdb(dbpath):
    """return readonly database object"""
    return xapian.Database(DB_PREFIX+dbpath)
def _get_wdb(dbpath):
    """return a writable database """
    return xapian.WritableDatabase(DB_PREFIX+dbpath,xapian.DB_OPEN)
def _prepare_scws():
    _scws.scws_new()
    _scws.scws_set_charset("UTF8")
    _scws.scws_set_xdb("/etc/scws/dict.utf8.xdb")
    _scws.scws_set_rule("/etc/scws/rules.utf8.ini")

def _free_scws():
    '''释放分词词库等;'''
    _scws.scws_free()

def cnseg(string):
    """分词,返回用空格分开的词语组"""
    d=_scws.get_res(string)
    return " ".join([c[0] for c in d])

def segment(string):
    '''分词,返回大数组,单个数据又是(词,词性,idf)组成的数组'''
    return _scws.get_res(string)

#print cnseg("哈哈，我是一只小小鸟")
#sys.exit()
def create_index(dbpath,fulltext_fields_v,store_fields_v,index_fields_v):
    """Create a new index, and set up its field structure.
    """
    if isinstance(fulltext_fields_v,dict):
        fulltext_fields=fulltext_fields_v.values()
    elif isinstance(fulltext_fields_v,list):
        fulltext_fields=fulltext_fields_v

    if isinstance(store_fields_v,dict):
        store_fields=store_fields_v.values()
    elif isinstance(store_fields_v,list):
        store_fields=store_fields_v
       
    if isinstance(index_fields_v,dict):
        index_fields=index_fields_v.values()
    elif isinstance(store_fields_v,list):
        index_fields=index_fields_v

    try:
        iconn = xappy.IndexerConnection(dbpath)
        for f in fulltext_fields:
            iconn.add_field_action(f,xappy.FieldActions.INDEX_FREETEXT)
        for f in store_fields:
            iconn.add_field_action(f, xappy.FieldActions.STORE_CONTENT)
        for f in index_fields:
            iconn.add_field_action(f, xappy.FieldActions.INDEX_EXACT)
        iconn.close()
        return True
    except:
        return None

def simple_create_index(dbpath):
    return create_index(dbpath,["text"],["text"],[])

def index_data(dbpath,key,data,need_seg_fields_v):
    """Index a data."""
    if isinstance( need_seg_fields_v,dict):
        need_seg_fields=need_seg_fields_v.values()
    elif isinstance( need_seg_fields_v,list):
        need_seg_fields=need_seg_fields_v

    try:
        iconn=xappy.IndexerConnection(dbpath)
        doc = xappy.UnprocessedDocument()
        for field in data:
            if field in need_seg_fields:
                doc.fields.append(xappy.Field(field, cnseg(str(data[field]))))
            else:
                doc.fields.append(xappy.Field(field, str(data[field])))
        doc.id=key
        iconn.add(doc)
        iconn.close()
        return {"code":200,"keys":data.keys()}
    except Exception,e:
        return {"code":500,"msg":str(e)} 

def batch_index(dbpath,datas_v,need_seg_fields_v):
    """batch index  datas.
    when you use batch index,you should specific the key field in data['id'] datas_v
    """
    if isinstance( need_seg_fields_v,dict):
        need_seg_fields=need_seg_fields_v.values()
    elif isinstance( need_seg_fields_v,list):
        need_seg_fields=need_seg_fields_v

    if isinstance(datas_v,dict):
        datas=datas_v.values()
    elif isinstance(datas_v,list):
        datas=datas_v
    try:
        iconn=xappy.IndexerConnection(dbpath)
        for data in datas:
            doc = xappy.UnprocessedDocument()
            for field in data:
                if field in need_seg_fields:
                    doc.fields.append(xappy.Field(field, cnseg(str(data[field]))))
                else:
                    doc.fields.append(xappy.Field(field, str(data[field])))
            doc.id=data["id"]
            iconn.add(doc)
        iconn.close()
        return {"code":200,"keys":data.keys()}
    except Exception,e:
        return {"code":500,"msg":str(e)} 
    
def simple_index_data(dbpath,key,text):
    return index_data(dbpath,key,{"text":text},["text"])
def count(dbpath):
    sconn = xappy.IndexerConnection(dbpath)
    temp=sconn.get_doccount()
    sconn.close()
    return temp

def search_result_report(dbpath,search):
    """search from database"""
    sconn =  xappy.SearchConnection(dbpath)
    q = sconn.query_parse(search, default_op=sconn.OP_AND)
    results = sconn.search(q,0,0)
    temp ={
            "startrank":results.startrank,
            "endrank":results.endrank,
            "more_matches":results.more_matches,
            "matches_lower_bound":results.matches_lower_bound,
            "matches_upper_bound":results.matches_upper_bound,
            "matches_estimated":results.matches_estimated,
            "estimate_is_exact":results.estimate_is_exact
            }
    sconn.close()
    return temp
def search(dbpath,search,start,limit):
    sconn =  xappy.SearchConnection(dbpath)
    q = sconn.query_parse(search, default_op=sconn.OP_AND)
    #q = sconn.query_parse(search, default_op=sconn.OP_OR)
    results = sconn.search(q,start,limit)
    sconn.close()
    return [result.id for result in results]
def get_document(dbpath,id):
    iconn=xappy.IndexerConnection(dbpath)
    try:
        temp=iconn.get_document(id)
    except:
        return -1
    iconn.close()
    ret={}
    for key in temp.data:
       ret[key]=temp.data[key][0] 
    return {
            "id":temp.id,
            "data":ret
            }
def simple_get_document(dbpath,id):
    val=get_document(dbpath,id)
    return {"id":val["id"],"text":val["data"]["text"]}
def del_document(dbpath,id):
    iconn=xappy.IndexerConnection(dbpath)
    temp=iconn.delete(id)
    iconn.close()
    return temp
#server = PHPRPC_Server("localhost",8090)






def db_init(dbpath,def_dict):
    """init a xapian database,save the information to a yaml;"""
    ymlfile=open(DB_PREFIX+dbpath+".yml","w+")
    try:
        yaml.dump(def_dict,ymlfile)
        db = xapian.WritableDatabase(DB_PREFIX+dbpath, xapian.DB_CREATE_OR_OPEN)
        return {"code":200}
    except:
        return {'code':500,"msg":"unkown error"}

def db_initsimple(dbpath):
    '''init a simple search xapian database that store only doc_id and text field;'''
    ymlfile=open(DB_PREFIX+dbpath+".yml","w+")
    try:
        def_dict=  {"doc_id":{"prefix":"I", "field":"doc_id", "segment":False},
        "text":{"prefix":"T", "field":"text", "segment":True}}
        yaml.dump(def_dict,ymlfile)
        db = xapian.WritableDatabase(DB_PREFIX+dbpath, xapian.DB_CREATE_OR_OPEN)
        return {"code":200}
    except:
        return {'code':500,"msg":"unkown error"}

def db_get_doccount(dbpath):
    '''get the counts of the documents in the database'''
    try:
        db=_get_rdb(dbpath)
    except:
        return {'code':500,'msg':"failed to open the database"}
    return {'code':200,'data':db.get_doccount()}

def db_get_document(dbpath):
    pass
def db_simpleindex(dbpath,id,text):
    '''简单地把text分词,然后做为Text域放进去'''
    i=0
    stemmer = xapian.Stem("english") # english stemmer
    terms=segment(text)
    doc = xapian.Document()
    for t in terms:
        i = i +1
        print stemmer(t[0])
        if len(t[0]) > 1 :
            doc.add_posting( "Z"+stemmer(t[0]).lower(),i)
        else:
            doc.add_posting( stemmer(t[0]).lower(),i)


    article_id_term = 'I'+str(id)
    doc.add_term(article_id_term)
    doc.set_data(id)
    db=_get_wdb(dbpath)
    db.replace_document(article_id_term,doc)
    return {"code":200}

def _simplesearch_match(dbpath,keyword,offset,size):
    terms=segment(keyword)
    stemmer = xapian.Stem("english") # english stemmer
    q=[]
    for t in terms:
        q.append(stemmer(t[0]))

    db=_get_rdb(dbpath)
    enquire = xapian.Enquire(db)
    query_string = ' '.join(q)
    # Parse the query string to produce a Xapian::Query object.
    qp = xapian.QueryParser()
    qp.set_stemmer(stemmer)
    qp.set_database(db)
    qp.set_stemming_strategy(xapian.QueryParser.STEM_SOME)
    query = qp.parse_query(query_string)
    enquire.set_query(query)
    matches = enquire.get_mset(offset, size)
    return matches

def db_simplesearch(dbpath,keyword,offset=0,size=10):
    matches=_simplesearch_match(dbpath,keyword,offset,size)

    # Display the results.
    print "%i results found." % matches.get_matches_estimated()
    print "Results 1-%i:" % matches.size()
    docids=[]
    for m in matches:
        docids.append({"data":m.document.get_data(),"doc_no":m.docid})
        #print "%i: %i%% docid=%i [%s]" % (m.rank + 1, m.percent, m.docid, m.document.get_data())
    return {"code":200,"data":docids,"size":matches.size()}

def db_simplesearch_count(dbpath,keyword):
    matches=_simplesearch_match(dbpath,keyword,0,10)
    return matches.get_matches_estimated()

def db_index(dbpath,dockey,data):
    '''index a data ,segment needed fields automatically'''
    

def main(args_in, app_name="api"):
    p = optparse.OptionParser(description=__doc__, version=__version__)
    p.set_usage(__usage__)
    p.add_option("-v", action="store_true", dest="verbose", help="verbose logging")
    p.add_option("-n", type="int", dest="server_num", help="Server instance number")
    opt, args = p.parse_args(args_in)

    if not opt.server_num:
        opt.server_num=1

#    db_init("test",[ {"prefix":"A", "field":"author", "segment":False}, {"prefix":"S", "field":"subject", "segment":False}, {"prefix":"I", "field":"id", "segment":False } ])

    _prepare_scws()
    db_initsimple("simple1")
    db_simpleindex("simple1","z0",'我们是好朋友 I love china')
    db_simpleindex("simple1","z1",'到我们来自美国 ,你来自哪里?')
    db_simpleindex("simple1","z2",'哈我们喜欢中美你来自哪里?')
    db_simpleindex("simple1","z3",'w你来我们这里吧')
    db_simpleindex("simple1","z4",'哈哈,我们这里是最好的公园')
    db_simpleindex("simple1","z5",'屁我们都要去法国')
    db_simpleindex("simple1","z6",'考虑我们一起走')
    db_simpleindex("simple1","z7",'我们才是好的')
    db_simpleindex("simple1","z8",'就是我们怎么了啊?')
    db_simpleindex("simple1","z9",'我们')
    db_simpleindex("simple1","z10",'我们最喜欢这个')
    db_simpleindex("simple1","z11",'一样我们也是好样的')
    db_simpleindex("simple1","z12",'一起我们哈哈')
    db_simplesearch_count("simple1","我们")
    db_simplesearch_count("simple1","他们")
    print db_simplesearch_count("simple1","I")
    print db_simplesearch_count("simple1","他们")
    db_simplesearch("simple1","我们China",2,10)
    db=_get_rdb("simple1")
    for c in db.allterms():
        print "new term",c.term
    print dir(db)
    print db_get_doccount("test")
    print db_simplesearch_count("simple1","我们")
    print db_simplesearch("simple1","我们",2,5)
    print db.get_document(2).get_data()
    _free_scws()

    #socketfile = _get_socket_path(app_name, opt.server_num)
    #app=PHPRPC_WSGIApplication()
#    app.add(cnseg)
#    app.add(create_index)
#    app.add(search)
#    app.add(search_result_report)
#    app.add(count)
#    app.add(index_data)
#    app.add(batch_index)
#    app.add(get_document)
#    app.add(del_document)
#    app.add(simple_get_document)
#    app.add(simple_create_index)
#    app.add(simple_index_data)
    #app.debug = True
    #app.start()

#    try:
#        WSGIServer(app,
#               bindAddress = socketfile,
#               umask = FCGI_SOCKET_UMASK,
#               multiplexed = True,
#               ).run()
#    except Exception,e:
#        print 'run app error:"',e
#    finally:
#        # Clean up server socket file
#        if os.path.exists(socketfile):
#            os.unlink(socketfile)

if __name__ == '__main__':
    main(sys.argv[1:])
