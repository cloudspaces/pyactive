"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from pyactive.constants import *
from pyactive.controller import later, send_timeout, new_group, send_timeout_multi, get_host
from pyactive.exception import PyactiveError, TimeoutError
from time import sleep
import uuid
import copy
import exceptions

class AbstractMulti(object):
    def __init__(self, list_actors):
        self.list_actors = []
        self.list_actors = list_actors
        
    def attach(self, actor):
        self.list_actors.extend(actor)
    
    def detach(self, actor):
        self.list_actors.remove(actor)
        
class AMulti(AbstractMulti):
    def __init__(self, list_actors):
        AbstractMulti.__init__(self, list_actors)
    def __getattr__(self, name):
        return _RemoteMethod2(self.dispatch, name)
    
        
    def dispatch(self, methodname, vargs, kwargs):
        for a in self.list_actors:
            getattr(a, methodname)(*vargs)
#             a.async_remote_call(methodname, vargs, kwargs)
    
class SMulti(AbstractMulti):
    
    def __init__(self, list_actors, atom):
        AbstractMulti.__init__(self, list_actors)
        self.own_actor = atom
        self.actor = new_group(self.own_actor.aref)
        self.ref_list = self.list_actors[0].refSync
        for name in self.ref_list:
            setattr(self, name, _RefWraper(self.dispatch, name))
                        
    def __getattr__(self, name):
        return _RemoteMethod2(self.dispatch, name)
    
    def dispatch(self, methodname, vargs, kwargs):
        
        result = []
        rpc_id_list = []
        msg = {}
        msg[METHOD] = methodname
        msg[PARAMS] = vargs
        msg[MODE] = SYNC
        msg[FROM] = self.actor.aref
        msg[TYPE] = CALL
        rpc_id = str(uuid.uuid1())
        msg[SRC] = self.actor.channel
        later(int(self.list_actors[0].syncList.get(methodname)), send_timeout_multi, self.actor.channel, rpc_id_list)
        for a in self.list_actors:
            msg[TO] = a.client.aref
            rpc_id = str(uuid.uuid1())
            msg[RPC_ID] = rpc_id
            a.client.set_pending(msg[RPC_ID])
            rpc_id_list.append(rpc_id) 
            msg2 = copy.copy(msg)
            a.client.out.send(msg2)
        for a in self.list_actors:
            parcial_result =  self.actor.receive_result()
            if isinstance(parcial_result, PyactiveError):
                if not result:
                    raise Exception, 'The timeout has expired'
                else:
                    return result
            
            result.append(parcial_result)
        return result

class _RefWraper():
    def __init__(self, send, name):
        self.__send = send
        self.__name = name
    def __call__(self, *args, **kwargs):
        new_args = get_host()._dumps(list(args))
        result = self.__send(self.__name, new_args, kwargs)
        if result != None:
            return get_host()._loads(result)
        else:
            return result
class _RemoteMethod2():
    def __init__(self, send, name):
        self.__send = send
        self.__name = name
        
    def __call__(self, *args, **kwargs):
        return self.__send(self.__name, args, kwargs)        