"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
import copy
import exceptions
from time import sleep
import uuid

from pyactive.constants import *
from pyactive.controller import later, send_timeout, new_group, send_timeout_multi, get_host
from pyactive.exception import PyactiveError, TimeoutError


class AbstractMulti(object):
    def __init__(self, list_actors=[]):
        self.dict_actors = dict()
        self.attach_list(list_actors)

    def attach(self, actor):
        dumps_actor = get_host()._dumps(actor)
        actor = get_host()._loads(dumps_actor)
        self.dict_actors[actor.get_aref()] = actor

    def detach(self, actor):
        if actor.get_aref in self.dict_actors.keys():
            del self.dict_actors[actor.get_aref()]

    def attach_list(self, actors):
        for actor in actors:
            self.attach(actor)


class AMulti(AbstractMulti):
    def __init__(self, list_actors=[]):
        AbstractMulti.__init__(self, list_actors)

    def __getattr__(self, name):
        return _RemoteMethod2(self.dispatch, name)

    def dispatch(self, methodname, vargs, kwargs):
        for a in self.dict_actors.values():
            getattr(a, methodname)(*vargs)
            # a.async_remote_call(methodname, vargs, kwargs)


class SMulti(AbstractMulti):
    def __init__(self, atom, list_actors=[]):
        AbstractMulti.__init__(self, list_actors)
        self.own_actor = atom
        self.actor = new_group(self.own_actor.aref)
        self.ref_list = self.dict_actors.values()[0].refSync
        for name in self.ref_list:
            setattr(self, name, _RefWraper(self.dispatch, name))

    def __getattr__(self, name):
        return _RemoteMethod2(self.dispatch, name)

    def dispatch(self, method_name, vargs, kwargs):
        final_result = {}
        rpc_id_list = []
        msg = {}
        msg[METHOD] = method_name
        msg[PARAMS] = vargs
        msg[MODE] = SYNC
        msg[FROM] = self.actor.aref
        msg[TYPE] = CALL
        rpc_id = str(uuid.uuid1())
        msg[SRC] = self.actor.channel

        if method_name == 'keep_alive':
            later(20, send_timeout_multi, self.actor.channel, rpc_id_list)
        else:
            timeout = int(self.dict_actors.values()[0].syncList.get(method_name))
            later(timeout, send_timeout_multi, self.actor.channel, rpc_id_list)

        for a in self.dict_actors.values():
            msg[TO] = a.client.aref
            rpc_id = str(uuid.uuid1())
            msg[RPC_ID] = rpc_id
            a.client.set_pending(msg[RPC_ID])
            rpc_id_list.append(rpc_id)
            msg2 = copy.copy(msg)
            a.client.out.send(msg2)

        for a in self.dict_actors.values():
            from_result, parcial_result = self.actor.receive_result()
            if from_result == 'timeout_controller':
                if not final_result:
                    raise Exception('The timeout has expired')
                else:
                    return final_result
            final_result[from_result] = parcial_result#.append(parcial_result)

        return final_result


class _RefWraper():
    def __init__(self, send, name):
        self.__send = send
        self.__name = name

    def __call__(self, *args, **kwargs):
        new_args = get_host()._dumps(list(args))
        result = self.__send(self.__name, new_args, kwargs)
        if result is not None:
            return {k: get_host()._loads(v) for k, v in result.items()}
            # return get_host()._loads(result.values)
        else:
            return result


class _RemoteMethod2():
    def __init__(self, send, name):
        self.__send = send
        self.__name = name

    def __call__(self, *args, **kwargs):
        return self.__send(self.__name, args, kwargs)
