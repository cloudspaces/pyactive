from pyactive.util import Ref, ref_d, ref_l
from pyactive.constants import METHOD, MODE, SRC, TO, FROM, TARGET, TYPE, RESULT, PARAMS, RPC_ID, SYNC, CALL, ERROR, MULTI, TCP
from exceptions import NotImplementedError
from urlparse import urlparse

class Abstract_actor(Ref):
    def __init__(self):
        self.aref = ''
        self.group = None
        self.running = False
        
    
    def registry_object(self, obj):
        self.obj = obj
        
    def run(self):
        self.running = True
        
    def stop(self):
        raise NotImplementedError()   
    
    def send(self,msg):
        raise NotImplementedError()   
    
    def init_parallel(self):
        raise NotImplementedError()

    def send2(self,target,msg):
        target.send(msg)
        
    def receive_result(self):
        '''recive result of synchronous calls'''
        result = self.channel.result
        return result
    
    def keep_alive(self):
        return True
    
    def failure_detect(self, actor):
        self.obj.failure_detect(actor.get_id())
        
    def receive(self,msg):   
        raise NotImplementedError()
    
    def ref_on(self):
        '''this method put wrapper to process ref'''
        self.receive = ref_l(self.receive)
        self.send2 = ref_d(self.send2)
            
    def get_aref(self):
        return self.aref    
    
    def get_gref(self):
        if self.group != None:
            return self.group.aref
    
    def set_aref(self, aref):
        self.aref = aref
        aurl = urlparse(aref)
        module, kclass, oid = aurl.path[1:].split('/')
        self._id = oid 
        
    def get_proxy(self):
        raise NotImplementedError()
    
    
    