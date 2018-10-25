from collections import OrderedDict
import functools
import memcache
import json
import pprint

mc = memcache.Client(['127.0.0.1:11211'], debug=0)

def pprint_od(od,indent=0):
    retval = '{'
    for k,v in od.items():
        retval += '"%s":' % (k,)
        if type(v) is OrderedDict:
           retval += '%s,\n' % (pprint_od(v,indent+len(k)+5),)
        else:
           retval += '%s,\n' % (pprint.pformat(v))
        retval += ' '*indent
    l = retval.rstrip().rstrip('\n')
    return l+'}'

def single_field(func,field):
    class new_func:
       def __call__(self,*args):
           retval = []
           for d in func(*args):
               retval.append(d[field])
           return retval
    return new_func()

def memcached(func,timeout=240):
    class new_func:
       def __call__(self,*args):
           retval = mc.get(str(hash(func))+str(hash(args)))
           if not retval:
              retval = func(*args)
              mc.set(str(hash(func))+str(hash(args)),json.dumps(retval),time=timeout)
           else:
              retval = json.loads(retval)
           return retval
    return new_func()

def memcached_bin(func):
    class new_func:
       def __call__(self,*args):
           retval = mc.get(str(hash(func)+hash(args)))
           if not retval:
              retval = func(*args)
              mc.set(str(hash(func)+hash(args)),retval,time=3600)
           return retval
    return new_func()



def with_args(func,args):
    class new_func:
       def __call__(self):
           return func(*args)
    return new_func()

def with_multi_args(func,defargs):
    class new_func:
       def __call__(self,*args):
           return func(*(defargs+list(args)))
    return new_func()

def joined(*funcs):
    class new_func_dict:
       def __call__(self):
           return dict(functools.reduce(lambda x,y: list(x)+list(y),
                             map(lambda x: x().items(), funcs)))
    return new_func_dict()

def multifunc(**kwargs):
    class new_func:
       def __call__(self,k):
           return kwargs[k]()
    return new_func()

def listify(func):
    class new_func:
       def __call__(self,*args):
           return func(args)[0]
    return new_func()
