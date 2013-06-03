"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""

from pyactive.constants import TCP, MODE, SYNC, RESULT, FROM, TO, TYPE, CALL, PARAMS, TARGET, METHOD, SRC, RPC_ID, ERROR
from pyactive.exception import PyactiveError, TimeoutError, MethodError, NotFoundDispatcher
import copy
from tcp_server import Server
from threading import Thread, Event, RLock,current_thread, Lock
from Queue import Queue
import pyactive.controller as controller
from pyactive.abstract_actor import Abstract_actor
from urlparse import urlparse

pending = {} 
threads = {}   

    
class Channel(Queue):
    def __init__(self):
        Queue.__init__(self)
    def send(self,msg):
        self.put(msg)
    def receive(self):
        return self.get()
    
class AsyncResult:
    """Represents an asynchronous operation that may not have completed yet."""
    def __init__(self):
        self.completed = False
        self.failed = False
        self.__wait = Event()
        self.__callbacks = []
        self.__errbacks = []
        self.__retval = []
        self.__error = None
        self.__lock = RLock()
        self.current_msg = None

    def complete(self):
        self.__lock.acquire()
        self.completed = True
        self.__wait.set()
        self.__lock.release()
        
    def reset(self):
        self.__lock.acquire()
        self.completed = False
        self.__wait.set()
        self.__lock.release()

    def succeed(self, retval):
        self.__retval.append(retval)
        self.complete()
        for callback in self.__callbacks:
            callback(retval)
        self.clearCallbacks()

    def fail(self, error):
        self.__error = error
        self.failed = True
        self.complete()
        for errback in self.__errbacks:
            errback(error)
        self.clearCallbacks()


    def send(self,msg):
        self.current_msg = msg
        result = msg[RESULT]
        if isinstance(msg,PyactiveError):
            self.fail(result)
        else:
            self.succeed(result)


    def clearCallbacks(self):
        self.__callbacks = []
        self.__errbacks = []

    def addCallback(self, callback, errback=None):
        self.__lock.acquire()
        try:
            if self.completed:
                if not self.failed:
                    callback(self.retval)
            else:
                self.__callbacks.append(callback)
            if not errback == None:
                self.addErrback(errback)
        finally:
            self.__lock.release()

    def addErrback(self, errback):
        self.__lock.acquire()
        try:
            if self.completed:
                if self.failed:
                    errback(self.error)
            else:
                self.__errbacks.append(errback)
        finally:
            self.__lock.release()

    def __getResult(self):
        self.__wait.wait()
        if not self.failed:
            if len(self.__retval)==1:
                return self.__retval[0]
            else:
                return self.__retval
        else:
            raise self.__error
    result=property(__getResult)   
    
    
class Pyactive(Abstract_actor):
    
    def __init__(self):
        Abstract_actor.__init__(self)
        self.__lock = None
        
    def __processQueue(self):
        while True:
            message = self.channel.receive()
            if message==StopIteration:
                break
            self.receive(message)
    
    def registry_object(self, obj):
        self.obj = obj
        
    def run(self):
        Abstract_actor.run(self)
        self.channel = Channel()
        self.thread = Thread(target=self.__processQueue)
        self.thread.start()
        threads[self.thread] = self.aref
        
    def stop(self):
        self.channel.send(StopIteration)
    
    def send(self,msg):
        msg[TO] = self.aref
        msg[TYPE] = CALL
        msg[TARGET] = self.target
        if msg[MODE] == SYNC:
            pending[msg[RPC_ID]] = 1
            self.channel = AsyncResult()
            msg[SRC] = self.channel
        self.out.send(msg)
    
    def init_parallel(self):
        '''Create Lock to guarantee concurrency when it use parallel wrapper. 
        In addition it put parallel wrapper in the correct objects methods'''
        self.__lock = Lock()
        for name in self.parallelList:
            setattr(self.obj, name, ParallelWraper(getattr(self.obj, name), self.aref, self.__lock))

    def receive_result(self):
        '''recive result of synchronous calls'''
        result = self.channel.result
        return result
    
    
    def receive(self,msg):   
        ''' receive messages and invokes object method'''
        invoke = getattr(self.obj, msg[METHOD])
        params = msg[PARAMS]
        result = None
        try:
            if self.__lock != None:
                with self.__lock:
                    result = invoke(*params)
            else:
                result = invoke(*params)
        except PyactiveError,e:
            result= e    
            msg[ERROR]=1  
        except TypeError,e2:
            result = MethodError()
            msg[ERROR]=1
    
        if result!= None and msg[MODE] == SYNC:
            msg2 = copy.copy(msg)
            target = msg2[SRC]
            msg2[TYPE]= RESULT
            msg2[RESULT]=result
            del msg2[PARAMS]
            del msg2[SRC]
            if pending.has_key(msg[RPC_ID]):
                del pending[msg[RPC_ID]]
                _from = msg2[FROM]
                msg2[FROM] = self.aref
                msg2[TO] = _from
                self.send2(target,msg2)
                
    def get_proxy(self):
        return self.host.load_client(self.channel, self.aref, get_current())
            

class ParallelWraper():
    def __init__(self, send, aref, lock):
        self.__send = send
        self.__aref = aref
        self.__lock = lock
    def __call__(self, *args, **kwargs):
        t1 = Thread(target=self.invoke, args=(self.__send, args, kwargs))
        t1.start()
        threads[t1] = self.__aref
        
    def invoke(self, func, args=[], kwargs=[]):
        with self.__lock:
            func(*args, **kwargs)
        
class TCPDispatcher(Pyactive):
    """ """
    def __init__(self,host, addr = ('127.0.0.1',40406)):
        Pyactive.__init__(self)
        self.aref = 'asdhsah'
        ip, port = addr
        self.name = ip + ':' + str(port)
        self.conn = Server(ip, port,self)
        self.addr = addr
        self.host = host
        self.callback = {}

        
    def receive(self,msg):
        
        if msg[MODE]==SYNC and msg[TYPE]==CALL:
            self.callback[msg[RPC_ID]]= msg[SRC]
        
        msg[SRC] = self.addr
        
        try:
            self.conn.send(msg)
        except Exception,e:
            pass
    def _stop(self):
        self.channel.send(StopIteration)
        self.conn.close()
        
    def is_local(self, name):
        return name == self.name
   
    def on_message(self, msg):
        try:
            if msg[TYPE]==RESULT:
                if pending.has_key(msg[RPC_ID]):
                    del pending[msg[RPC_ID]]
                    target = self.callback[msg[RPC_ID]]
                    del self.callback[msg[RPC_ID]]       
                    target.send(msg)
            else:
                if msg[MODE]== SYNC:
                    msg[TARGET]=msg[SRC]
                    msg[SRC]= self.channel
                    pending[msg[RPC_ID]] = 1
                aref = msg[TO]
                aurl = urlparse(aref)
                self.host.objects[aurl.path].channel.send(msg)
        except Exception,e:
            pass
            
def new_TCPdispatcher(host, dir):
    tcp = TCPDispatcher(host, dir) 
    tcp.run()
    return tcp

def new_dispatcher(host, transport):
    dispatcher_type = transport[0]
    if dispatcher_type == TCP:
        return new_TCPdispatcher(host, transport[1])
    else:
        raise NotFoundDispatcher()
           
def get_current():
    current = current_thread()
    if threads.has_key(current):
        return threads[current] 
                
def send_timeout(receiver,rpc_id):
    if pending.has_key(rpc_id):
        del pending[rpc_id]
        receiver.fail(TimeoutError())
    
def launch(func, params=[]):
    #TODO Mirar que funcione bien el tema de matar todos los threads
    t1 = Thread(target=func, args=params)
    threads[t1] = 'atom://localhost/'+func.__module__+'/'+func.__name__
    t1.start()
    t1.join()
    host =  controller.get_host()
    host._shutdown()
        
def serve_forever(func, params=[]):
    threads[current_thread()] = 'atom://localhost/'+func.__module__+'/'+func.__name__
    func(*params)
    