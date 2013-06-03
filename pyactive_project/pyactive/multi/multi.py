"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""


from pyactive.exception import PyactiveError, TimeoutError, MethodError
from pyactive.constants import  *
import uuid
import copy
from pyactive.tasklet.tasklet import Pyactive
def start_multi(package_name):
    global actor
    actor = __import__(package_name+'.'+package_name, globals(), locals(), ['Pyactive'], -1)
    print actor
    global timeController
    timeController = __import__(package_name+'.'+package_name+'Delay', globals(), locals(), ['later'], -1)

def new_multi():
    return Multi()

class Multi(Pyactive):
   
    def __init__(self,actors=[]):
        Pyactive.__init__(self)
        self.actors = actors
        self.callback = {}
        self.results = {}
        self.targets = {}
        self.obj = self

  
    def join(self,actor):
        self.actors.append(actor)
        actor.group = self
        return actor
      
    #@ref
    #@sync(1)        
    def leave(self, actor):
        self.actors.remove(actor)
        #key = atom.get_aref()
        #if self.actors.has_key(key):
        #    del self.actors[key]
        return True
    
    #@ref
    #@sync(1)        
    def members(self):
        return self.actors.copy()
    
    def forward(self,msg):
        for actor in self.actors:
            msg2 = copy.copy(msg)
            msg2[TARGET]=actor.target
            msg2[TO] = actor.aref
            actor.send(msg2)
    
    
    def receive(self,msg2):   
        msg = copy.copy(msg2)
        if msg.has_key(MULTI):
            if msg[MODE]==SYNC and msg[TYPE]==CALL:
                #pending[msg[RPC]] = msg[SRC]
                self.callback[msg[RPC_ID]]= msg[SRC]
                self.results[msg[RPC_ID]]= []
                self.targets[msg[RPC_ID]]=msg[TARGET]
                msg[SRC] = self.channel
                msg[MULTI]=1
                timeController.later(msg[TIMEOUT],send_timeout,self.channel,msg[RPC_ID])
                self.forward(msg)
            elif msg[MODE]==ONEWAY:
                self.forward(msg)
            elif msg[TYPE]==RESULT:
                if msg.has_key(ERROR):
                    self.reply(msg)
                else:
                    if self.results.has_key(msg[RPC_ID]):
                        self.results[msg[RPC_ID]].append(msg[RESULT]) 
                        if len(self.results[msg[RPC_ID]])==len(self.actors):
                            msg[RESULT]= self.results[msg[RPC_ID]]
                            self.reply(msg)
    
            elif msg[MODE]==TIMEOUT:
                self.reply(msg)
        else:
            Pyactive.receive(self, msg)
        
    def reply(self,msg):  
        if self.callback.has_key(msg[RPC_ID]):
            target = self.callback[msg[RPC_ID]]
            msg[TARGET] = self.targets[msg[RPC_ID]]
            del self.targets[msg[RPC_ID]]
            del self.callback[msg[RPC_ID]]
            del self.results[msg[RPC_ID]]
            #target.send(msg)
            #_from = msg[FROM]
            #msg[FROM] = self.aref
            #msg[TO] = _from
            self.send2(target,msg)


class Many(Multi):
    def __init__(self,atoms=[]):
        Multi.__init__(self,atoms)
    def receive(self,msg):   
        if msg[MODE]==TIMEOUT:
            msg[RESULT]= self.results[msg[RPC_ID]]
            self.reply(msg)
        else:
            super(Many,self).receive(msg)
 
class Any(Multi):
    def __init__(self,atoms=[]):
        Multi.__init__(self,atoms)
    def receive(self,msg):   
        if msg[TYPE]==RESULT:
            self.reply(msg)
        else:
            super(Any,self).receive(msg)
            
            
class Pool(Multi):
    def __init__(self,atoms=[]):
        Multi.__init__(self,atoms)
        self.current = 0
       
    def forward(self,msg):
        self.actors[self.current].send(msg)
        self.current = (self.current + 1)%len(self.actors) 
        
    def receive(self,msg):   
        if msg[TYPE]==RESULT:
            self.reply(msg)
        else:
            super(Pool,self).receive(msg)            

class Server(Multi):
    
    def __init__(self):
        super(Multi,self).__init__()
    #@async
    def set_value(self,value):
        self.value = value
          
    def get_value(self):
        return self.value
    
def send_timeout(channel,rpc_id):
    msg = {}
    msg[MODE]=TIMEOUT
    msg[TYPE]=TIMEOUT
    msg[RPC_ID]=rpc_id
    msg[MULTI]=1
    msg[RESULT]= TimeoutError()
    channel.send(msg)   