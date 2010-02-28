#!/home/renlu/bin/bin/python
#coding:utf-8
__usage__ = "%prog -n <num>"
__version__ = "1.0.0"
__author__ = "162cm <xurenlu@gmail.com>"

import sys,os
print sys.path
sys.path.append("/usr/local/lib/python2.6/dist-packages/phprpc-3.0.0-py2.6.egg/phprpc")
#from phprpc import PHPRPC_Server # 引入 PHPRPC Server
from phprpc import PHPRPC_WSGIApplication
#, UrlMapMiddleware, PHPRPC_Server
import datetime
#from pymmseg import mmseg
#import xappy
from flup.server.fcgi import WSGIServer
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
    '''预先准备好分词需要的词库,规则文件'''
    _scws.scws_new()
    _scws.scws_set_charset("UTF8")
    _scws.scws_set_xdb("/etc/scws/dict.utf8.xdb")
    _scws.scws_set_rule("/etc/scws/rules.utf8.ini")

def _free_scws():
    '''释放分词词库等;'''
    _scws.scws_free()

def _load_dbdesc(dbpath):
    """load yaml info to dict"""
    desc=yaml.load(open(DB_PREFIX+dbpath+".yml"))
    return desc

def cnseg(string):
    """分词,返回用空格分开的词语组"""
    d=_scws.get_res(string)
    return " ".join([c[0] for c in d])

def segment(string):
    '''分词,返回大数组,单个数据又是(词,词性,idf)组成的数组'''
    return _scws.get_res(string)

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
        def_dict=  {"doc_id":{"prefix":"I","segment":False},
        "text":{"prefix":"T","segment":True}}
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
    ''' to do'''
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
    #doc.add_term(article_id_term)
    doc.set_data(id)
    db=_get_wdb(dbpath)
    db.replace_document(article_id_term,doc)
    return {"code":200}

def db_generic_index(dbpath,dockey,data):
    '''index a data ,segment needed fields automatically'''
    desc=_load_dbdesc(dbpath)

    i=0
    stemmer = xapian.Stem("english") # english stemmer
    doc = xapian.Document()

    for d in data:
        if desc[d]["segment"]:
            print data[d]
            terms=segment(data[d])
            print "go"
            for t in terms:
                i=i+1
                if len(t[0])>1:
                    doc.add_posting(desc[d]["prefix"]+stemmer(t[0]).lower(),i)
                else:
                    doc.add_posting(stemmer(t[0]).lower(),i)
        else:
            doc.add_term(desc[d]["prefix"]+str(data[d]).lower())
        #print "key:",k,"\tvalue:",v

    article_id_term = "I"+stemmer(dockey)
    doc.set_data(dockey)
    db=_get_wdb(dbpath)
    db.replace_document(article_id_term,doc)
    return {"code":200}

def _query_match(dbpath,query,offset,size):
    '''
    simple search时 需要分词但不需要前加缀
    通用search时,需要提前加分词 在这一步加前缀'''
    '''
    qp = xapian.QueryParser()
    dbdesc=_load_dbdesc()

    for field in dbdesc:
        qp.add_prefix(field,dbdesc[field]['prefix'])
        #add prefix 

    if segment:
        terms=segment(keyword)
        stemmer = xapian.Stem("english") # english stemmer
        q=[]
        for t in terms:
            q.append(stemmer(t[0]))
        query_string = ' '.join(q)
    else:
        query_string = keyword


    dbdesc=_load_dbdesc(dbpath)
    for field in dbdesc:
        qp.add_prefix(field,dbdesc[field]["prefix"])
    #qp.set_stemming_strategy(xapian.QueryParser.STEM_SOME)
    qp.set_database(db)
    print "query_string:",query_string
    query = qp.parse_query(query_string)
    '''
    db=_get_rdb(dbpath)
    enquire = xapian.Enquire(db)
    enquire.set_query(query)
    matches = enquire.get_mset(offset, size)
    return matches


def _simplesearch_get_query(dbpath,keyword):
    qp=xapian.QueryParser()
    dbdesc=_load_dbdesc(dbpath)
    for field in dbdesc:
        qp.add_prefix(field,dbdesc[field]['prefix'])
        #add prefix 
    terms=segment(keyword)
    stemmer = xapian.Stem("english") # english stemmer
    q=[]
    for t in terms:
        q.append(stemmer(t[0]))
    query_string = ' '.join(q)
    query = qp.parse_query(query_string)
    return query

def db_simplesearch(dbpath,keyword,offset=0,size=10):
    '''search simple database'''
    query=_simplesearch_get_query(dbpath,keyword)
    matches=_query_match(dbpath,query,offset,size)

    # Display the results.
    print "%i results found." % matches.get_matches_estimated()
    print "Results 1-%i:" % matches.size()
    docids=[]
    for m in matches:
        docids.append({"data":m.document.get_data(),"doc_id":m.docid})
        #print "%i: %i%% docid=%i [%s]" % (m.rank + 1, m.percent, m.docid, m.document.get_data())
    return {"code":200,"data":docids,"size":matches.size()}


def db_simplesearch_count(dbpath,keyword):
    '''return the result count of simple search'''
    query=_simplesearch_get_query(dbpath,keyword)
    matches=_query_match(dbpath,keyword,0,10)
    return matches.get_matches_estimated()

def _get_genericsearch_query(dbpath,queries):
    ''' get query object of generic search'''
    qp = xapian.QueryParser()
    dbdesc=_load_dbdesc(dbpath)
    stemmer = xapian.Stem("english") # english stemmer
    for field in dbdesc:
        qp.add_prefix(field,dbdesc[field]['prefix'])
        #add prefix 
	qs=""
    for q in queries:
        if dbdesc[q]["segment"]:
            terms=segment(queries[q])
            for t in terms:
                qs= qs +  q + ":" + t[0] + " "
        else:
            qs = q + ":" + queries[q] + " "
    
    query = qp.parse_query(qs)
    return query

def db_generic_search(dbpath,queries,offset=0,size=10):
    """search a database"""
    query=_get_genericsearch_query(dbpath,queries)
    matches = _query_match(dbpath,query,offset,size)
    # Display the results.
    print "%i results found." % matches.get_matches_estimated()
    print "Results 1-%i:" % matches.size()
    docids=[]
    for m in matches:
        docids.append({"data":m.document.get_data(),"doc_id":m.docid})
        #print "%i: %i%% docid=%i [%s]" % (m.rank + 1, m.percent, m.docid, m.document.get_data())
    return {"code":200,"data":docids,"size":matches.size()}


def db_generic_search_count():
    """get search count of a database """
    query=_get_genericsearch_query(dbpath,queries)
    matches = _query_match(dbpath,query,offset,size)
    return matches.get_matches_estimated()
    

def main(args_in, app_name="api"):
    p = optparse.OptionParser(description=__doc__, version=__version__)
    p.set_usage(__usage__)
    p.add_option("-v", action="store_true", dest="verbose", help="verbose logging")
    p.add_option("-n", type="int", dest="server_num", help="Server instance number")
    opt, args = p.parse_args(args_in)

    if not opt.server_num:
        opt.server_num=1

#    db_init("test",[ {"prefix":"A", "field":"author", "segment":False}, {"prefix":"S", "field":"subject", "segment":False}, {"prefix":"I", "field":"id", "segment":False } ])
    #_prepare_scws()
    import sys
    #db_initsimple('simple1')
    #print _load_dbdesc("simple1")
    #value={"author":"renlu.xu","date":"2009-02-32","email":"xurenlu@gmail.com","url":"http://www.sohu.com/","title":"中国和美国谈判了","content":"前天国家主席胡家明访问了美国东部地区"}
    #key="doc_1"
    #db_init("simple2",{"author":{"prefix":"A","segment":False},"date":{"prefix":"D","segment":False},"email":{"prefix":"E","segment":False},"url":{"prefix":"U","segment":False},"title":{"prefix":"T","segment":True},"content":{"prefix":"C","segment":True}})
    #print db_index("simple2",key,value)

    #db_initsimple("simple1")
    #db_simpleindex("simple1","z0",'我们是好朋友 I love china')
    #db_simpleindex("simple1","z1",'到我们来自美国 ,你来自哪里?')
    #db_simpleindex("simple1","z2",'哈我们喜欢中美你来自哪里?')
    #db_simpleindex("simple1","z3",'w你来我们这里吧')
    #db_simpleindex("simple1","z4",'哈哈,我们这里是最好的公园')
    #db_simpleindex("simple1","z5",'屁我们都要去法国')
    #db_simpleindex("simple1","z6",'考虑我们一起走')
    #db_simpleindex("simple1","z7",'我们才是好的')
    #db_simpleindex("simple1","z8",'就是我们怎么了啊?')
    #db_simpleindex("simple1","z9",'我们')
    #db_simpleindex("simple1","z10",'我们最喜欢这个')
    #db_simpleindex("simple1","z11",'一样我们也是好样的')
    #db_simpleindex("simple1","z12",'一起我们哈哈')
    #db_simplesearch_count("simple1","我们")
    #db_simplesearch_count("simple1","他们")
    #print db_simplesearch_count("simple1","I")
    #print db_simplesearch_count("simple1","他们")
    #print db_generic_search("simple1",{"text":"我们佛教徒不吃肉"})
    #sys.exit(0)
    #db_simplesearch("simple1","'text:我们'",0,10)
    #sys.exit(0)
    #db=_get_rdb("simple1")
    #for c in db.allterms():
    #    print "new term",c.term
    #print dir(db)
    #print db_get_doccount("test")
    #print db_simplesearch_count("simple1","我们")
    #print db_simplesearch("simple1","我们",2,5)
    #print db.get_document(2).get_data()
    #_free_scws()

    socketfile = _get_socket_path(app_name, opt.server_num)
    app=PHPRPC_WSGIApplication()
    print dir(app)
    app.add(cnseg)
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

    try:
        WSGIServer(app,
               bindAddress = socketfile,
               umask = FCGI_SOCKET_UMASK,
               multiplexed = True,
               ).run()
    except Exception,e:
        print 'run app error:"',e
    finally:
        # Clean up server socket file
        if os.path.exists(socketfile):
            os.unlink(socketfile)

if __name__ == '__main__':
    main(sys.argv[1:])
