#!/home/renlu/bin/bin/python
#coding:utf-8
__usage__ = "%prog -n <num>"
__version__ = "1.0.0"
__author__ = "162cm <xurenlu@gmail.com>"

import sys,os,re,uuid,cgi
sys.path.append('/usr/local/lib/python2.6/dist-packages/phprpc-3.0.0-py2.6.egg/')
#sys.path.append('/home/renlu/download/phprpc/py24/')
from phprpc.phprpc import PHPRPC_WSGIApplication
from phprpc.phprpc import PHPRPC_Client
import datetime
from flup.server.fcgi import WSGIServer
from phprpc.phprpc import phpformat 
from beaker.middleware import  SessionMiddleware
import optparse
import yaml
import xapian
import _scws
import storage
#FCGI_LISTEN_ADDRESS = ('localhost', 9000)
FCGI_SOCKET_DIR = '/tmp'
FCGI_SOCKET_UMASK = 0111
DB_PREFIX="./"

class AuthMiddleWare(object):
    '''this middleware to support simple user authentication
    I save the (secret_code,username) maps in a variable,
    and I will save it in database later ,and that's much more better 
    '''
    def __init__(self,app):
        self.app=app
    def __call__(self,env,start_response=None):
        try:
            qs=env["QUERY_STRING"]
            code="-"
        except:
            qs= "-"
            code="-"
        qs_array=cgi.urlparse.parse_qs(qs)
        try:
            code = qs_array["code"][0]
        except:
            pass
        env["cloudface.session"]={"code":code} #phpformat.serialize({"count":1000}) 
        return self.app(env,start_response)


global dbpath_reg
dbpath_reg = re.compile("^[0-9a-zA-Z]+$")

def proxy_wrapper(func_name):
    """gen new func ,and put a arg as the last argument"""
    def inner(session,*args):
        global dbpath_reg
        try:
            realargs=[ i for i in args] 
            code = session['code']
            #开始鉴权
            dbh=storage.Dbh(prepare_sql="set names utf8")
            dbh.load_yaml("./etc/db.yaml")
            dbh.connect()
        except Exception,e:
            return {"code":510,"msg":" error: db init :"+str(e)}
        try:
            auth=storage.authenticate(dbh,code)
        except:
            return {"code":511,"msg":"error in authenticaate"}
        try:
            if auth == None:
                #查不到该code的信息,返回403
                return {'code':403,'msg':"secret code invalid"}
            if auth["status"] != "normal":
                return {'code':401,'msg':"your code status is "+ auth['status']}
            auth["dbpath"]="-"
        except Exception,e:
            return {"code":501,"msg":str(e)}
        except:
            return {"code":500}
        
        
        current_len=len(args)
        #把session传过去
        try:
            client = PHPRPC_Client('http://cloudapi.info/b8/api.php')  
            clientProxy = client.useService()  
            #comment={'ip':'127.0.0.1','urls':['http://localhost/'],'text':'我们都是中国人'}
            ret=client.api_execute(func_name,args)
            #ret=func(*realargs)
        except Exception,e:
            print "error 102:" + str(e)
            pass
        try:
            if not ret.has_key("code"):
                ret['code']=200
            if not ret.has_key("msg"):
                ret["msg"]="-"
            ret["uuid"]=str(uuid.uuid4())
        except Exception,e:
            ret={"code":509,"msg":"server side progrmming error.API must return a dict  which have a 'code' item. or :"+str(e),"uuid":str(uuid.uuid4())}
        try:
            if ret["code"]!=200:
                storage.log(dbh,auth["code"],auth['user_id'],auth["dbpath"], func_name, ret['code'],ret['msg'],ret["uuid"])
            else:
                storage.log(dbh,auth["code"],auth['user_id'],auth["dbpath"], func_name, ret['code'],ret['msg'],ret["uuid"])
                #接口调用正常的情况下,只做一个计数;
                storage.increment(dbh,auth["user_id"],auth["dbpath"],func_name)
        except Exception,e:
            #print "error occured:",e
            pass
        #ret["code"],ret["msg"]
        #except Exception,e:
        #    print  "error",dir(e),e.message
        return ret
    return inner


def main(args_in, app_name="api"):
    import sys
    socketfile=os.path.join(FCGI_SOCKET_DIR, 'cloudface-proxy-%s.socket' % app_name )
    app=PHPRPC_WSGIApplication("utf-8",False,"cloudface.session")
    proxy_methods=['api_learn_spam','api_learn_ham','api_unlearn_spam','api_unlearn_ham','api_classify','api_test_comment']
    for method in proxy_methods:
        app.add(proxy_wrapper(method),method)
    app = AuthMiddleWare(app)
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
