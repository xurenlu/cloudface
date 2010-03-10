#!/home/renlu/bin/bin/python
#coding:utf-8
__usage__ = "%prog -n <num>"
__version__ = "1.0.0"
__author__ = "162cm <xurenlu@gmail.com>"
__doc__='''
+ 概要 +

- **使用方法**:
    整个搜索API分为三分部,分别是:
    - **简单数据库相关API**
    - **通用数据库相关API**
    - **文本处理相关API**

    所有的函数调用都返回一个Dict,一般是{"code":200}类似的,如果有数据一般用dict["data"]来返回.dict["code"]是200时,表求请求正常完成.在请求不成功时(dict["code"]!=200时),在下面的文档指出的返回值之外,所有函数都附加返回一个uuid,代表当前请求的uuid,这个出错的请求也会记录在服务器端的日志系统中,可以将这个uuid替交给在线支持系统以获得技术支持.


++简单数据库++
    数据库里的一条记录称为一个文档.简单数据库里的一条纪录非常简单,就是一段文本.每一个文档都有一个标识符,在后面的函数里一般是**dockey**;
    简单数据包含 **api_simple_index**(dbpath,dockey,text),**api_simple_init**(dbpath),**api_simple_search**(dbpath,keyword,offset,size),**api_simple_search_count**(dbpath,keyword)四个函数; 

++ 通用数据库++
    通用数据库里的一条纪录(文档)是一个Hash,Python中就是一个Dict,php中就是一个数组.通用数据库相关有**api_generic_index**(dbpath,dockey,data),**api_generic_init**(dbpath,def_dict),**api_generic_search**(dbpath,queries,offset,size),**api_generic_search_count**(dbpath,queries)这四个函数

++ 文本处理相关API++
    包括分词和取关键词接口,分别是**api_getkeywords**(string,limit,attr)和**api_segment**(string);

'''

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
    '''分词,返回大数组,单个数据又是(词,词性,idf)组成的数组

    **example**:
    @startcode
    for c in api_segment("我们是好朋友"):
        print c[0],":",c[1],":",c[2]
    @endcode
    **result**:
    @startcode
    我们 : r : 4.42000007629
    是 : v : 0.0
    好朋友 : nz : 7.96999979019
    @endcode
    '''
    return _scws.get_res(string)

def api_getkeywords(string,limit=5,attr='~v'):
    """return keywords of  text
    得到某段文本的关键词

    - **string** : 要取关键词的文本
    - **limit** :整型,要取的关键词的个数,默认为5
    - **attr** :取哪种词性的关键词,一般可设置为n,代表名词,或~v 

    **example**
    @startcode
    for c in module.api_getkeywords(txt,5,"~v"):
            print c[0],":",c[1],":",c[2],":",c[3]
    @endcode
    **result**
    @startcode
    Python : e : 18 : 80.629196167
    语言 : n : 11 : 53.3499946594
    Machine : e : 9 : 43.7829780579
    Virtual : e : 9 : 43.7829780579
    Guido : e : 7 : 28.1651611328
    @endcode
    """
    return _scws.get_tops(string,limit,attr)

def api_generic_init(dbpath,def_dict):
    """
    init a xapian database,save the information to a yaml;
    初始化一个通用的搜索数据库;
    - **dbpath** : 数据库名字,由字母和数字组成
    - **def_dict**: 一个hash结构,具体结构如下所示例的:

    @startcode
    {"author":{"prefix":"A","segment":True},
    "pubdate":{"prefix":"P","segment":False},
    "content":{"prefix":"C","segment":True},
    }
    @endcode

    """
    ymlfile=open(DB_PREFIX+dbpath+".yml","w+")
    try:
        yaml.dump(def_dict,ymlfile)
        db = xapian.WritableDatabase(DB_PREFIX+dbpath, xapian.DB_CREATE_OR_OPEN)
        return {"code":200}
    except:
        return {'code':500,"msg":"unkown error"}

def api_simple_init(dbpath):
    '''
    init a simple search xapian database that store only doc_id and text field;
    初始化一个简单搜索的数据库
    - **dbpath**:数据库名字
    '''
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
    '''
    get the counts of the documents in the database
    返回数据库中文档数

    - **dbpath**:数据库名字

    '''
    try:
        db=_get_rdb(dbpath)
    except:
        return {'code':500,'msg':"failed to open the database"}
    return {'code':200,'data':db.get_doccount()}

def api_get_document(dbpath):
    '''
    待完成中...
    '''
    return {'code':200,'data':'to be finished'}

def api_simple_index(dbpath,dockey,text):
    '''
    简单地把text分词,然后做为Text域放进去

    - **dbpath**:数据库名字
    - **dockey**:文档标识符
    - **text**:要索引的文本
    '''
    i=0
    stemmer = xapian.Stem("english") # english stemmer
    terms=segment(text)
    doc = xapian.Document()
    for t in terms:
        i = i +1
        #print stemmer(t[0])
        if len(t[0]) > 1 :
            doc.add_posting( "T"+stemmer(t[0]).lower(),i)
        else:
            doc.add_posting( stemmer(t[0]).lower(),i)


    article_id_term = "UNIQUE_ID"+dockey
    doc.add_term(article_id_term)
    doc.set_data(dockey)
    db=_get_wdb(dbpath)
    #print "replacing document:",article_id_term
    doc_new_id=db.replace_document(article_id_term,doc)
    return {"code":200,"doc_id":doc_new_id}

def api_generic_index(dbpath,dockey,data):
    '''
    index a data ,segment needed fields automatically
    索引一个数据结构,一个Hash结构
    
    - **dbpath** : 数据库名
    - **dockey** : 文档的标识键
    - **data** :要索引的数据
    '''
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
    通用search时,需要提前加分词 在这一步加前缀
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
        q.append("text:"+stemmer(t[0]))
    query_string = ' '.join(q)
    query = qp.parse_query(query_string)
    return xapian.Query(xapian.Query.OP_OR,query,xapian.Query("T"+keyword))
    return query

def api_simple_search(dbpath,keyword,offset=0,size=10):
    '''
    search simple database
    简单数据库的索引

    - **dbpath**: 数据库路径
    - **keyword**:要搜的关键词
    - **offset**: 
    - **size**:
    '''
    query=_simplesearch_get_query(dbpath,keyword)
    print query
    matches=_query_match(dbpath,query,offset,size)

    # Display the results.
    #print "%i results found." % matches.get_matches_estimated()
    #print "Results 1-%i:" % matches.size()
    docids=[]
    for m in matches:
        docids.append({"data":m.document.get_data(),"doc_id":m.docid})
        #print "%i: %i%% docid=%i [%s]" % (m.rank + 1, m.percent, m.docid, m.document.get_data())
    return {"code":200,"data":docids,"size":matches.size(),"query":str(query)}


def api_simple_search_count(dbpath,keyword):
    '''
    return the result count of simple search
    返回简单搜索的结果总数

    - **dbpath**: 数据库名
    - **keyword**: 关键词
    '''
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
    parsed_queries=[]
    unsegments=[]
    for q in queries:
        if dbdesc[q]["segment"]:
            terms=segment(queries[q])
	        qs=""
            for t in terms:
                qs= qs +  q + ":" + t[0] + " "
            parsed_queries.append(qp.parse_query(qs))
        else:
            unsegments.append(q)
            #qs = q + ":" + queries[q] + " "
    query = xapian.Query()
    for uq in unsegments:
        query=xapian.Query(xapian.Query.OP_AND,query,xapian.Query(dbdesc[uq]["prefix"]+queries[uq]))
    for q parsed_queries :
        query=xapian.Query(xapian.Query.OP_AND,query,q)
    return query

def api_generic_search(dbpath,queries,offset=0,size=10):
    """
    search a database
    搜索数据库,使用通用搜索

    - **dbpath**:数据库名
    - **queries**:搜索条件,是一个hash,例如:
    @startcode
    {
        "author":"renlu",
        "email":"hello@world.com",
        "id":18
    }
    @endcode
    - **offset**:
    - **size**:要返回的查询结果数
    """
    query=_get_genericsearch_query(dbpath,queries)
    matches = _query_match(dbpath,query,offset,size)
    # Display the results.
#    print "%i results found." % matches.get_matches_estimated()
#    print "Results 1-%i:" % matches.size()
    docids=[]
    for m in matches:
        docids.append({"data":m.document.get_data(),"doc_id":m.docid})
        #print "%i: %i%% docid=%i [%s]" % (m.rank + 1, m.percent, m.docid, m.document.get_data())
    return {"code":200,"data":docids,"size":matches.size(),"query":str(query)}


def api_generic_search_count(dbpath,queries):
    """
    get search count of a database 
    获得通用搜索的结果数

    - **dbpath**:数据库名
    - **queries**:查询条件,参见 **api_generic_search** 中的**queries**参数
    """
    query=_get_genericsearch_query(dbpath,queries)
    matches = _query_match(dbpath,query,offset,size)
    return {"code":200,"data":matches.get_matches_estimated(),"query":str(query)}
    
def api_remove_document(dbpath,docid):
    '''
    remove document from database
    从数据库中删除一个文档

    - **dbpath**:数据库名
    - **docid**:文档的id,这个id应该是索引文档时索引函数返回的整数
    '''
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
    '''
    return methods that  begins with 'api'
    查询模块中以api开头的函数和变量名

    - **module**:要查询的模块,默认是None.默认是None时,函数内部会使用当前模块
    '''
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

