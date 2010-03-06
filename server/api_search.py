#!/home/renlu/bin/bin/python
#coding:utf-8
__usage__ = "%prog -n <num>"
__version__ = "1.0.0"
__author__ = "162cm <xurenlu@gmail.com>"

import sys,os
sys.path.append("/usr/local/lib/python2.6/dist-packages/phprpc-3.0.0-py2.6.egg/phprpc")
from phprpc import PHPRPC_WSGIApplication
import datetime
from flup.server.fcgi import WSGIServer
import optparse
import yaml
import xapian
import _scws

#FCGI_LISTEN_ADDRESS = ('localhost', 9000)
DB_PREFIX="./"


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

def api_segment(string):
    return _scws.get_res(string)

def api_getkeywords(string,limit,attr='~v'):
    """return keywords of  text"""
    return _scws.get_tops(string,limit,attr)

def api_generic_init(dbpath,def_dict):
    """init a xapian database,save the information to a yaml;"""
    ymlfile=open(DB_PREFIX+dbpath+".yml","w+")
    try:
        yaml.dump(def_dict,ymlfile)
        db = xapian.WritableDatabase(DB_PREFIX+dbpath, xapian.DB_CREATE_OR_OPEN)
        return {"code":200}
    except:
        return {'code':500,"msg":"unkown error"}

def api_simple_init(dbpath):
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

def api_get_documents_count(dbpath):
    '''get the counts of the documents in the database'''
    try:
        db=_get_rdb(dbpath)
    except:
        return {'code':500,'msg':"failed to open the database"}
    return {'code':200,'data':db.get_doccount()}

def api_get_document(dbpath):
    ''' to do'''
    return {'code':200,'data':'to be finished'}

def api_simple_index(dbpath,dockey,text):
    '''简单地把text分词,然后做为Text域放进去'''
    i=0
    stemmer = xapian.Stem("english") # english stemmer
    terms=segment(text)
    doc = xapian.Document()
    for t in terms:
        i = i +1
        print stemmer(t[0])
        if len(t[0]) > 1 :
            doc.add_posting( "T"+stemmer(t[0]).lower(),i)
        else:
            doc.add_posting( stemmer(t[0]).lower(),i)


    article_id_term = "UNIQUE_ID"+dockey
    doc.add_term(article_id_term)
    doc.set_data(dockey)
    db=_get_wdb(dbpath)
    print "replacing document:",article_id_term
    doc_new_id=db.replace_document(article_id_term,doc)
    return {"code":200,"doc_id":doc_new_id}

def api_generic_index(dbpath,dockey,data):
    '''index a data ,segment needed fields automatically'''
    desc=_load_dbdesc(dbpath)

    i=0
    stemmer = xapian.Stem("english") # english stemmer
    doc = xapian.Document()

    for d in data:
        if desc[d]["segment"]:
            terms=segment(data[d])
            for t in terms:
                i=i+1
                if len(t[0])>1:
                    doc.add_posting(desc[d]["prefix"]+stemmer(t[0]).lower(),i)
                else:
                    doc.add_posting(stemmer(t[0]).lower(),i)
        else:
            doc.add_term(desc[d]["prefix"]+str(data[d]).lower())
        #print "key:",k,"\tvalue:",v

    article_id_term = "UNIQUE_ID"+stemmer(dockey)
    doc.set_data(dockey)
    db=_get_wdb(dbpath)
    doc_new_id=db.replace_document(article_id_term,doc)
    return {"code":200,"data":doc_new_id}

def _query_match(dbpath,query,offset,size):
    '''
    simple search时 需要分词但不需要前加缀
    通用search时,需要提前加分词 在这一步加前缀'''
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
        q.append("text:"+stemmer(t[0]))
    query_string = ' '.join(q)
    query = qp.parse_query(query_string)
    return xapian.Query(xapian.Query.OP_OR,query,xapian.Query("T"+keyword))
    return query

def api_simple_search(dbpath,keyword,offset=0,size=10):
    '''search simple database'''
    query=_simplesearch_get_query(dbpath,keyword)
    print query
    matches=_query_match(dbpath,query,offset,size)

    # Display the results.
    print "%i results found." % matches.get_matches_estimated()
    print "Results 1-%i:" % matches.size()
    docids=[]
    for m in matches:
        docids.append({"data":m.document.get_data(),"doc_id":m.docid})
        #print "%i: %i%% docid=%i [%s]" % (m.rank + 1, m.percent, m.docid, m.document.get_data())
    return {"code":200,"data":docids,"size":matches.size(),"query":str(query)}


def api_simple_search_count(dbpath,keyword):
    '''return the result count of simple search'''
    query=_simplesearch_get_query(dbpath,keyword)
    matches=_query_match(dbpath,keyword,0,10)
    return {"code":200,"data":matches.get_matches_estimated(),"query":str(query)}

def _get_genericsearch_query(dbpath,queries):
    ''' get query object of generic search'''
    qp = xapian.QueryParser()
    dbdesc=_load_dbdesc(dbpath)
    stemmer = xapian.Stem("english") # english stemmer
    for field in dbdesc:
        qp.add_prefix(field,dbdesc[field]['prefix'])
        #add prefix 
	qs=""
    unsegments=[]
    for q in queries:
        if dbdesc[q]["segment"]:
            terms=segment(queries[q])
            for t in terms:
                qs= qs +  q + ":" + t[0] + " "
        else:
            unsegments.append(q)
            #qs = q + ":" + queries[q] + " "
    query = qp.parse_query(qs)
    for uq in unsegments:
        query=xapian.Query(xapian.Query.OP_OR,query,xapian.Query(dbdesc[uq]["prefix"]+queries[uq]))
    return query

def api_generic_search(dbpath,queries,offset=0,size=10):
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
    return {"code":200,"data":docids,"size":matches.size(),"query":str(query)}


def api_generic_search_count(dbpath,queries):
    """get search count of a database """
    query=_get_genericsearch_query(dbpath,queries)
    matches = _query_match(dbpath,query,offset,size)
    return {"code":200,"data":matches.get_matches_estimated(),"query":str(query)}
    
def api_remove_document(dbpath,docid):
    ''' remove document from database'''
    try:
        wdb=_get_wdb(dbpath)
    except:
        return {'code':400,"msg":"database not  wrtiable or not exists etc."}

    try:
        wdb.delete_document(docid)
        return {"code":200}
    except:
        return {"code":500,"msg":"nothing removed"}

def api_get_methods(module=None):
    ''' return methods that  begins with 'api' '''
    import sys
    import re
    if module == None:
        module = sys.modules[__name__]
    attrs=dir(module)
    api_re=re.compile("^api_")
    apis=[]
    for attr in attrs:
        if api_re.match(attr) and callable(getattr(module,attr)):
            apis.append(getattr(module,attr))
        #if callable(sys.modules[__name__]) 
    return apis 

