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
        users={"secret_key_code1":"xurenlu","secret_key_code2":"user2"}
        code=env["QUERY_STRING"]
        if not users.has_key(code):
            return ('403 Error',[('Content-Type','text/plain')],['403 Invalid code'])

        return self.app(env,start_response)


def main(args_in, app_name="api"):
    import sys
    socketfile=os.path.join(FCGI_SOCKET_DIR, 'floudface-fcgi-%s.socket' % app_name )
    app=PHPRPC_WSGIApplication()
    import api_search
    api_search._prepare_scws()
    for method in get_public_methods(api_search):
        app.add(method)
    app  = AuthMiddleWare(app)

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
