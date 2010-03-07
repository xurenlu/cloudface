#!/usr/bin/python
#coding:utf8
import sys,os,imp,logging,re
sys.path.append("../server/")
def prepare_taskfile(taskfile):
    """Attempt to load the taskfile as a module.
    """
    path = os.path.dirname(taskfile)
    taskmodulename = os.path.splitext(os.path.basename(taskfile))[0]
    logging.info("Loading task file %s from %s", taskmodulename, path)
    fp, pathname, description = imp.find_module(taskmodulename, [path])
    try:
        return imp.load_module(taskmodulename, fp, pathname, description)
    finally:
        if fp: 
            fp.close()

def main():
    file=sys.argv[1]
    module=prepare_taskfile(file)
    module._prepare_scws()
    #for c in module.api_segment("我们是好朋友"):
    #    print c[0],":",c[1],":",c[2]
    #txt=open("./demo").read()
    #for c in module.api_getkeywords(txt,5,"~v"):
    #    print c[0],":",c[1],":",c[2],":",c[3]
    methods=[]
    reg=re.compile("^api_",re.I)
    for attr in dir(module):
        if reg.match(attr):
            code=getattr(module,attr).func_code
            vars=code.co_varnames[:code.co_argcount]
            methods.append((attr,vars,getattr(module,attr).__doc__))
    print "+ "+module.__name__ + " +"
    for method in methods:
        _s=",".join(method[1])
        print "++ %s" % method[0] + "(" + _s + ") ++ "
        try:
            print method[2] + "\n"
        except:
            print "\n"
    return methods

if __name__ == '__main__':
    
    main()
