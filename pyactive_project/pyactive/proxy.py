"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from constants import METHOD, SYNC, ONEWAY, PARAMS, MODE, FROM, RPC_ID, MULTI
import controller
from util import Ref
from copy import copy
from exception import TimeoutError, PyactiveError
import uuid


def select_time(packageName):
    global timeout
    timeout = __import__(packageName + '.' + packageName, globals(), locals(), ['send_timeout'], -1)
    global time
    time = __import__(packageName + '.' + packageName + 'Delay', globals(), locals(), ['later'], -1)


class Auto_Proxy(Ref):
    """This Proxy is used to auto-calls.
    It allows one object can call itself how one direct object calls."""

    def __init__(self, obj, aref):
        self.obj = obj
        self.aref = aref

    def hello(self):
        print self

    def __getattr__(self, name):
        return _RemoteMethod2(getattr(self.obj, name), name)

    def get_aref(self):
        return self.aref

    def get_id(self):
        return self.obj.id


class Proxy(Ref):
    def __init__(self, client, _from, lock):
        self._from = _from
        self.lock = lock
        self.client = client
        self.syncList = copy(self.client.syncList)
        refAsync = set(client.asyncList) & set(client.refList)
        self.refSync = set(client.syncList) & set(client.refList)

        for name in self.refSync:
            setattr(self, name, _RefWraper(self.sync_remote_call, name))
            del self.client.syncList[name]
        for name in refAsync:
            setattr(self, name, _RefWraper(self.async_remote_call, name))
            self.client.asyncList.remove(name)
        for name in self.client.asyncList:
            setattr(self, name, _RemoteMethod(self.async_remote_call, name))
        for name in self.client.syncList.keys():
            setattr(self, name, _RemoteMethod(self.sync_remote_call, name))


    def sync_remote_call(self, methodname, vargs, kwargs):
#         print 'SOC AL PROXY', self._from, self.client._id
#         print 'SOC DINS EL SYNC CALL semafor meu', self.lock
        msg = {}
        msg[METHOD] = methodname
        msg[PARAMS] = vargs
        msg[MODE] = SYNC
        msg[FROM] = self._from
        rpc_id = str(uuid.uuid1())
        msg[RPC_ID] = rpc_id
        self.client.send(msg)
        if self.lock:
            # print 'release_proxy', self._from, self.lock
            self.lock.release()
           # time.later(int(self.syncList.get(methodname)), timeout.send_timeout, self.client.channel, rpc_id)
        self.my_later(methodname, rpc_id)
        result = self.client.receive_result()
        if self.lock:
#             print 'acquire_proxy', self._from
            self.lock.acquire()
        if isinstance(result, Exception):
            print 'it is an exception'
            raise result
        else:
            return result

    def async_remote_call(self, methodname, vargs, kwargs):
        msg = {}
        msg[METHOD] = methodname
        msg[PARAMS] = vargs
        msg[MODE] = ONEWAY
        msg[FROM] = self._from
        self.client.send(msg)

    def my_later(self, methodname, rpc_id):
        time.later(int(self.syncList.get(methodname)), timeout.send_timeout, self.client.channel, rpc_id)

    def get_aref(self):
        return self.client.get_aref()

    def get_gref(self):
        return self.client.get_gref()

    def get_id(self):
        return self.client._id

    def __eq__(self, other):
        return self.client._id == other.get_id()


class _RemoteMethod2():
    def __init__(self, send, name):
        self.__send = send
        self.__name = name

    def __call__(self, *args, **kwargs):
        return self.__send(*args, **kwargs)


class _RemoteMethod():
    """method call abstraction"""

    def __init__(self, send, name):
        self.__send = send
        self.__name = name

    def __call__(self, *args, **kwargs):
        return self.__send(self.__name, args, kwargs)


class _RefWraper():
    def __init__(self, send, name):
        self.__send = send
        self.__name = name

    def __call__(self, *args, **kwargs):
        new_args = controller.get_host()._dumps(list(args))
        result = self.__send(self.__name, new_args, kwargs)
        if result != None:
            return controller.get_host()._loads(result)
        else:
            return result
