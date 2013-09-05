"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from pyactive.constants import *
from pyactive.controller import later, send_timeout, new_group
from time import sleep
import uuid

class AMulti(object):
    def __init__(self, list_actors, atom):
        self.actors = list_actors
        self.own_actor = atom
        
        
    def __getattr__(self, name):
        return _RemoteMethod2(self.dispatch, name)
    
        
    def dispatch(self, methodname, vargs, kwargs):
        for a in self.actors:
            a.async_remote_call(methodname, vargs, kwargs)

class _RemoteMethod2():
    def __init__(self, send, name):
        self.__send = send
        self.__name = name
        
    def __call__(self, *args, **kwargs):
        return self.__send(self.__name, args, kwargs)
    
class SMulti(object):
    
    def __init__(self, list_actors, atom):
        self.actors = list_actors
        self.own_actor = atom
        self.actor = new_group(self.own_actor.aref)
        
    def __getattr__(self, name):
        return _RemoteMethod2(self.dispatch, name)
    
    def dispatch(self, methodname, vargs, kwargs):
        msg = {}
        msg[METHOD] = methodname
        msg[PARAMS] = vargs
        msg[MODE] = SYNC
        msg[FROM] = self.actor.aref
        rpc_id = str(uuid.uuid1())
        msg[RPC_ID] = rpc_id
        msg[SRC] = self.actor.channel
        later(self.actors[0].syncList.get(methodname), send_timeout(), self.own_actor.channel, rpc_id)
        for a in self.actors:
            a.sync_remote_call(methodname, vargs, kwargs)
        
        