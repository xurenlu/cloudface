#! /usr/bin/python
#coding:utf-8
__usage__ = "%prog -n <num>"
__version__ = "1.0.0"
__author__ = "162cm <xurenlu@gmail.com>"

import sys,os,re,uuid,cgi
from phprpc.phprpc import PHPRPC_WSGIApplication
import datetime
from flup.server.fcgi import WSGIServer
#from fcgi import WSGIServer
from phprpc.phprpc import phpformat 
import optparse
import yaml
import xapian
import _scws
import storage
#FCGI_LISTEN_ADDRESS = ('localhost', 9000)
FCGI_SOCKET_DIR = '/tmp'
FCGI_SOCKET_UMASK = 0111
DB_PREFIX="./"


def get_public_methods(module=None):
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
        #print env
        #print env["cloudface.session"]
        #print env
        return self.app(env,start_response)


global dbpath_reg
dbpath_reg = re.compile("^[0-9a-zA-Z]+$")

def function_wrapper(func,func_name):
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
            return {"code":510,"msg":" error: db init"+str(e)}
        try:
            auth=storage.authenticate(dbh,code)
        except:
            return {"code":511,"msg":"error in authenticaate"}
        try:
            if auth == None:
                #查不到该code的信息,返回403
                return {'code':403,'msg':"secret code invalid"}
            if auth.has_key("status"):
                if auth["status"] != "normal":
                    return {'code':401,'msg':"your code status is "+ auth['status']}
            try:
                if func.func_code.co_varnames[0] == "dbpath" :
                    if  not args[0] == auth["dbpath"]:
                        return {'code':402,'msg':"this code is not for this database"}
                    if dbpath_reg.match(args[0]) == None:
                        return {'code':406,'msg':"dbpath must match regexp: /0-9a-zA-Z+/"}
            except:
                pass
            else:
                auth["dbpath"]="-"
        except Exception,e:
            #print "error occured while authenticating:",e
            return {"code":501,"msg":str(e)}
        except:
            #print "error occured while authenticating."
            return {"code":500}
        #print "function ",func_name," called"
        #print "received args,",args
        #print "session",session
        #print "realfunc 's first argument",func.func_code.co_varnames[0]
        
        
        current_len=len(args)
        #print "args len:",current_len
        #print 'realfunction arg.len',func.func_code.co_argcount
        #把session传过去
        if func.func_code.co_argcount == len(args)+1 :
            if len(args) > 0:
                realargs.insert(len(args),session)
            else:
                realargs.insert(0,session)

        #print "realargs:",realargs

        try:
            ret=func(*realargs)
        except Exception,e:
            #print "function ",func_name," failed"
            pass
        try:
            if not ret.has_key("code"):
                ret['code']=200
            if not ret.has_key("msg"):
                ret["msg"]="-"
            ret["uuid"]=str(uuid.uuid4())
        except:
            ret={"code":509,"msg":"server side progrmming error.API must return a dict  which have a 'code' item.","uuid":str(uuid.uuid4())}
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
    socketfile=os.path.join(FCGI_SOCKET_DIR, 'cloudface-fcgi-%s.socket' % app_name )
    if os.path.exists(socketfile):
        print "socket file exists"
        sys.exit(0)
    app=PHPRPC_WSGIApplication("utf-8",False,"cloudface.session")
    import api_search
    api_search._prepare_scws()
    for method in get_public_methods(api_search):
        print "method " + str(method) + " added" 
        app.add(function_wrapper(method,method.__name__),method.__name__)
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
