"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""

from urlparse import urlparse
from proxy import Proxy, select_time, Auto_Proxy
from util import Ref, AtomRef
from copy import copy
from exception import NotFoundDispatcher
import sys, types


def get_host():
    return host

def start_controller(controllerType):
    global packageName
    packageName = controllerType
    global controller
    controller = __import__(packageName+'.'+packageName, globals(), locals(), ['Actor', 'launch', 'new_dispatcher', 'ParallelWrapper', 'new_group'], -1)
    global timeController
    timeController = __import__(packageName+'.'+packageName+'Delay', globals(), locals(), ['later', 'sleep', 'interval'], -1)


def tracer(func,atom):
    """Tracer the call messages"""
    def on_call(*args):
        atom.notify(args[0])
        return func(*args)
    return on_call

def tracer2(func,atom):
    """Tracer the response messages"""
    def on_call(*args):
        atom.notify(args[1])
        return func(*args)
    return on_call

class Host(object):
    _sync = {'spawn_id':'1', 'set_tracer':'1', 'lookup':'1' }
    _async = ['shutdown', 'hello']
    _ref = ['spawn_id', 'lookup' ]
    _prallel = []
    
    def __init__(self, transport=()):
        self.name = 'local'
        self.objects = {}
        self.locks = {}
        self.dispatcher = self
        self.tasks = {}
        self.TRACE = False
        self.load_transport(transport)
        self.host = self
        
    def load_transport(self, transport):
        if transport != ():
                try:
                    self.dispatcher = controller.new_dispatcher(self, transport)
                except NotFoundDispatcher:
                    raise NotFoundDispatcher()
        self.aref = 'atom://' + self.dispatcher.name + '/controller/Host/0'
        self.name = self.dispatcher.name
        
     
    def spawn_id(self, oid, module, kclass, params=[]):
        module_ = self.my_import(module)
        
        #instance object save to obj variable
        obj = getattr(module_, kclass)(*params)
        obj.keep_alive = keep_alive
#         setattr(kclass, 'keep_alive', types.MethodType(keep_alive(), kclass))
#         add_method = types.MethodType(keep_alive, obj, kclass)
#         obj = add_method
        #aref object
        aref = 'atom://' + self.name + '/' + module + '/' + kclass + '/' + oid
        #Now we need registry object to Pyactive object. But also it's necessary create new Pyactive instance.
        a = controller.Actor()
        
        #Registry object to Pyactive
        a.registry_object(obj)
        
        #Insert aref to Pyactive object
        a.set_aref(aref)
        a.host = self
        obj.id = oid
        obj._atom = a
        refList = obj.__class__._ref
#        refList = list(methodsWithDecorator(getattr(module_, kclass), 'ref'))
        
        if self.TRACE:
            a.send2 = tracer2(a.send2, self.tracer)
        
        if len(refList) != 0:
            a.ref_on()
        
        if self.TRACE:
            a.receive = tracer(a.receive, self.tracer)

        parallelList = obj.__class__._parallel
        syncList = obj.__class__._sync.keys() 
        asyncList = obj.__class__._async
        a.sync_parallel = set(syncList)&set(parallelList)
        a.async_parallel = set(asyncList)&set(parallelList)
#        a.parallelList = list(methodsWithDecorator(getattr(module_, kclass), 'parallel'))
        lock = a.init_parallel()
        self.locks[aref] = lock
        #Finally run object because it's ready now
        a.run()
        
        #Now registry new object in Host, because need check duplicates 
        self.register(aref, a)
        
        obj.proxy = Auto_Proxy(obj, aref)
        client = self.load_client(a.channel, aref, aref)
        return client
        
        
    def register(self, aref, obj):
        aurl = urlparse(aref)
        #change next if for method is_local, when we have the Dispatcher
        if self.is_local(aurl.netloc):
            if self.objects.has_key(aurl.path):
                raise Exception('duplicated')
            else:
                self.objects[aurl.path] = obj
        else:
            raise Exception('registering remote host atoms not allowed')

    def set_tracer(self, proxy):
        self.TRACE = True
        self.tracer = proxy
        return True    
    

    def hello(self):
        print 'I am Host'        
        
    def is_local(self, location):
        return location == self.name  
    
    def load_client(self, channel, aref, _from):
    
        scheme, host, module, kclass, oid, = self.parse_aref(aref)
        
        if module != 'controller':
            module_ = self.my_import(module)
            kclass_ = getattr(module_, kclass)
        else:
            kclass_ = self.__class__
        client = controller.Actor()
        client.out = channel
        client.target = host
        client.set_aref(aref)
        client.asyncList = copy(kclass_._async)
        client.refList = copy(kclass_._ref)
        client.syncList = copy(kclass_._sync)
#        client.asyncList = list(methodsWithDecorator(kclass_, 'async'))
#        client.refList = list(methodsWithDecorator(kclass_, 'ref'))
#        client.syncList = methodsWithSync(kclass_, 'sync') 
 
        client.host = self
        select_time(packageName)
        if _from in self.locks.keys():
            lock = self.locks[_from]
            proxy = Proxy(client, _from, lock)
        else:
            proxy = Proxy(client, _from, None)

        return proxy

    def _shutdown(self):
        
        for atom in self.objects.values():
            if atom.aref != self.aref:
                atom.stop()
        self.objects = {}
        aurl = urlparse(self.aref)
        self.objects[aurl.path] = self.atom
        
        
    #@async
    def shutdown(self):
        self._shutdown()
        if self.dispatcher != self:
            self.dispatcher._stop()
        self.atom.stop()
        
    def parse_aref(self, aref):
        aurl = urlparse(aref)
        module, kclass, oid = aurl.path[1:].split('/')
        return (aurl.scheme, aurl.netloc, module, kclass, oid) 
    

    def _lookup(self, aref, _from):
        aurl = urlparse(aref)
        if self.dispatcher.is_local(aurl.netloc):
            if not self.objects.has_key(aurl.path):
                raise Exception('not found')
            else:
                obj = self.objects[aurl.path]
                client = self.load_client(obj.channel, aref, _from)
                return client
        else:
            client = self.load_client(self.dispatcher.channel, aref, _from)
            return client

    def lookup(self, aref):
        aurl = urlparse(aref)
        if self.dispatcher.is_local(aurl.netloc):
            if not self.objects.has_key(aurl.path):
                raise Exception('not found')
            else:
                obj = self.objects[aurl.path]
                client = self.load_client(obj.channel, aref, controller.get_current())
                return client
        else:
            client = self.load_client(self.dispatcher.channel, aref, controller.get_current())
            return client

    def _dumps(self, param):
        if isinstance(param, Ref):
            return AtomRef(param.get_aref())
        elif isinstance(param, list):
            return [self._dumps(elem) for elem in param]
        else:
            return param


    def _loads(self, param):
        if isinstance(param, AtomRef):
            _from = controller.get_current()
            if _from == param.get_aref():
                aurl = urlparse(_from)
                obj = Auto_Proxy(self.objects[aurl.path].obj, _from)
            else:
                obj = self._lookup(param.get_aref(), _from)

            return obj
        elif isinstance(param, list):
            return [self._loads(elem) for elem in param]
        else:
            return param                
                    
    def my_import(self, name):
        __import__(name)
        return sys.modules[name]    

    
def keep_alive():
    return True           
        
def init_host(transport=()):
    a = controller.Actor()
    h = Host(transport)
    a.set_aref(h.aref)
    a.host = h
    a.registry_object(h)
    h.register(h.aref, a)
    a.ref_on()
    a.run()
    h.channel = a.channel
    h.atom = a
    global host
    host = h
    return a.get_proxy()

def new_group(aref):
    a = controller.MultiActor()
    a.host = host
    a.aref = aref+'/multi'
    host.register(a.aref, a)
    return a

def new_supervisor(aref):
    a = controller.Actor()
    a.host = host
    a.aref = aref+'/dev'
    host.register(a.aref, a)
    return a

def launch(func, params=[]):
    controller.launch(func, params)   
     
def serve_forever(func, params=[]):
    controller.serve_forever(func, params)
    
def sleep(seconds):
    timeController.sleep(seconds)

def interval(time, f, *args, **kwargs):
    timeController.interval(time, f, *args, **kwargs)
def later(time, f, *args, **kwargs):
    timeController.later(time, f, *args, **kwargs)
def send_timeout():
    controller.send_timeout()
def send_timeout_multi(channel, rpc_list):
    controller.send_timeout_multi(channel, rpc_list)
    