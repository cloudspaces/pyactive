"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from threading import Thread, current_thread, Lock
from Queue import Queue
import cPickle
import copy
import signal
import sys

from pyactive.abstract_actor import Abstract_actor
from pyactive import controller
from pyactive.constants import *
from pyactive.exception import TimeoutError, MethodError, NotFoundDispatcher
from mom_server import Server as Session
from tcp_server import Server


pending = dict()
threads = dict()


class Channel(Queue):
    def __init__(self):
        Queue.__init__(self)

    def send(self, msg):
        self.put(msg)

    def receive(self, timeout=None):
        return self.get(timeout=timeout)


class Actor(Abstract_actor):
    def __init__(self):
        Abstract_actor.__init__(self)
        self.__lock = None
        self.channel = Channel()
        self.callbacks = {}
        self.sync_parallel = []

    def __processQueue(self):
        while True:
            message = self.channel.receive()
            if message == StopIteration:
                break
            self.receive(message)

    def registry_object(self, obj):
        self.obj = obj

    def run(self):
        Abstract_actor.run(self)
        self.thread = Thread(target=self.__processQueue)
        self.thread.daemon = True
        self.thread.start()
        threads[self.thread] = self.aref

    def stop(self):
        self.channel.send(StopIteration)
        del threads[self.thread]
        self.obj.host.unregister(self.obj.id)

    def send(self, msg):
        # print self.aref, 'actor send', msg
        msg[TO] = self.aref
        msg[TYPE] = CALL
        msg[TARGET] = self.target
        if msg[MODE] == SYNC:
            self.set_pending(msg[RPC_ID])
            msg[SRC] = self.channel

        self.out.send(msg)

    def set_pending(self, rpc_id):
        pending[rpc_id] = 1

    def init_parallel(self):
        '''Create Lock to guarantee concurrency when it uses parallel wrapper.
        In addition it put parallel wrapper in the correct objects methods'''
        self.__lock = Lock()
        for method_name in self.sync_parallel:
            method = getattr(self.obj, method_name)
            sync_wrap = ParallelSyncWraper(method, self.aref, self, self.__lock)
            setattr(self.obj, method_name, sync_wrap)
        for method_name in self.async_parallel:
            method = getattr(self.obj, method_name)
            async_wrap = ParallelAsyncWraper(method, self.aref, self.__lock)
            setattr(self.obj, method_name, async_wrap)
        return self.__lock

    def receive_result(self, timeout=None):
        '''receive result of synchronous calls'''
        result = self.channel.receive(timeout)
        return result[RESULT]

    def receive(self, msg):
        ''' receive messages and invokes object method'''
        invoke = getattr(self.obj, msg[METHOD])
        params = msg[PARAMS]

        result = None
        # try:
        if msg[METHOD] in self.sync_parallel:
            self.callbacks[msg[RPC_ID]] = msg
            params = list(params)
            params.insert(0, {'rpc_id': msg[RPC_ID], 'actor': self})
            invoke(*params)
        else:
            try:
                if self.__lock is not None:
                    self.__lock.acquire()
                    result = invoke(*params)
                    self.__lock.release()
                else:
                    result = invoke(*params)
            except TypeError, e:
                result = MethodError(msg[METHOD], e)
                msg[ERROR] = 1
            except Exception, e:
                result = e
                msg[ERROR] = 1

            if msg[MODE] == ONEWAY and ERROR in msg.keys():
                raise result

            if msg[MODE] == SYNC:
                msg2 = copy.copy(msg)
                target = msg2[SRC]
                msg2[TYPE] = RESULT
                msg2[RESULT] = result

                del msg2[PARAMS]
                del msg2[SRC]

                if msg[RPC_ID] in pending:
                    del pending[msg[RPC_ID]]
                    _from = msg2[FROM]
                    msg2[FROM] = self.aref
                    msg2[TO] = _from
                    self.send2(target, msg2)

        #    else:
        #       result = invoke(*params)
        # except PyactiveError,e:
        #     result= PyactiveError()
        #     msg[ERROR]=1
        # except TypeError, e2:
        #     result = MethodError()
        #     msg[ERROR]=1

    def receive_sync(self, result, rpc_id):
        msg = self.callbacks[rpc_id]
        del self.callbacks[rpc_id]
        msg2 = copy.copy(msg)
        target = msg2[SRC]
        msg2[TYPE] = RESULT
        msg2[RESULT] = result
        del msg2[PARAMS]
        del msg2[SRC]
        if msg[RPC_ID] in pending:
            del pending[msg[RPC_ID]]
            _from = msg2[FROM]
            msg2[FROM] = self.aref
            msg2[TO] = _from
            self.send2(target, msg2)

    def get_proxy(self):
        return self.host.load_client(self.channel, self.aref, get_current())


class MultiActor(Actor):
    def receive_result(self, timeout=None):
        '''receive result of synchronous calls'''
        result = self.channel.receive(timeout)
        return result[FROM], result[RESULT]


class ParallelActor(Actor):
    def receive_result(self, timeout=None):
        '''receive result of synchronous calls'''
        result = self.channel.receive(timeout)
        return result[FROM], result[RESULT]


class ParallelSyncWraper():
    def __init__(self, send, aref, principal_thread, lock):
        self.__send = send
        self.__aref = aref
        self.__lock = lock
        self.__principal_thread = principal_thread

    def __call__(self, *args, **kwargs):
        try:
            args = list(args)
            rpc_id = args[0]['rpc_id']
            actor = args[0]['actor']
            del args[0]
            args = tuple(args)
        except:
            rpc_id = None
        finally:
            if not rpc_id:
                result = self.__send(*args)
                return result
            else:
                args = (self.__send, rpc_id, self.__lock, args, kwargs)
                th = Thread(target=self.invoke, args=args)
                th.start()
                threads[th] = self.__aref

    def invoke(self, func, rpc_id, lock, args=[], kwargs=[]):
        lock.acquire()
        try:
            result = func(*args)
        except TypeError as e:
            result = MethodError()
        except Exception as e:
            result = e

        lock.release()

        self.__principal_thread.receive_sync(result, rpc_id)


class ParallelAsyncWraper():
    def __init__(self, send, aref, lock):
        self.__send = send
        self.__aref = aref
        self.__lock = lock

    def __call__(self, *args, **kwargs):
        th = Thread(target=self.invoke, args=(self.__send, args, kwargs))
        th.daemon = True
        th.start()
        threads[th] = self.__aref

    def invoke(self, func, args=[], kwargs=[]):
        self.__lock.acquire()
        func(*args, **kwargs)
        self.__lock.release()


class TCPDispatcher(Actor):

    def __init__(self, host, addr):
        Actor.__init__(self)
        ip, port = addr
        self.name = ip + ':' + str(port)
        self.conn = Server(ip, port, self)
        self.addr = addr
        self.host = host

        self.callback = {}

    def receive(self, msg):
        if msg[MODE] == SYNC and msg[TYPE] == CALL:
            self.callback[msg[RPC_ID]] = msg[SRC]

        msg[SRC] = self.addr
        try:
            self.conn.send(msg)
        except Exception as e:
            print e, 'TCP ERROR 2'

    def _stop(self):
        self.conn.close()
        self.channel.send(StopIteration)
        del threads[self.thread]

    def is_local(self, name):
        return name == self.name

    def on_message(self, msg):
        try:
            if msg[TYPE] == RESULT:
                if msg[RPC_ID] in pending:
                    del pending[msg[RPC_ID]]
                    target = self.callback[msg[RPC_ID]]
                    del self.callback[msg[RPC_ID]]
                    target.send(msg)
            else:
                if msg[MODE] == SYNC:
                    msg[TARGET] = msg[SRC]
                    msg[SRC] = self.channel
                    pending[msg[RPC_ID]] = 1
                aref = msg[TO]
                _, _, _, _, oid = self.host.parse_aref(aref)
                self.host.objects[oid].channel.send(msg)
        except Exception as e:
            print e, 'TCP ERROR 1'


class MOMDispatcher(Actor):
                    # ,ConnectionListener):

    def __init__(self, host, conf):
        Actor.__init__(self)
        momip = conf[IP]
        momport = conf[PORT]
        self.namespace = conf[NAMESPACE]
        self.session = Session(momip, momport)
        self.host = host
        self.name = conf[NAME]
        self.session.subs(self, self.namespace, {'selector': "HOST='%s'" % self.name})
        self.callback = {}

    def receive(self, msg):
        if msg[MODE] == SYNC and msg[TYPE] == CALL:
            self.callback[msg[RPC_ID]] = msg[SRC]
            del msg[SRC]
        parsed_msg = cPickle.dumps(msg)
        try:
            self.session.pub(parsed_msg, self.namespace, {'HOST': msg[TARGET], SRC: self.name})
        except Exception as e:
            print e, 'MOM ERROR'

    def is_local(self, name):
        return name == self.name

    def _stop(self):
        self.session.close()
        self.channel.send(StopIteration)
        del threads[self.thread]

    def on_message(self, headers, message):
        try:
            msg = cPickle.loads(message)
            if msg[TYPE] == RESULT:
                if msg[RPC_ID] in pending:
                    del pending[msg[RPC_ID]]
                    target = self.callback[msg[RPC_ID]]
                    del self.callback[msg[RPC_ID]]
                    target.send(msg)
            else:
                if msg[MODE] == SYNC:
                    msg[SRC] = self.channel
                    msg[TARGET] = headers[SRC]
                    pending[msg[RPC_ID]] = 1
                aref = msg[TO]
                _, _, _, _, oid = self.host.parse_aref(aref)
                self.host.objects[oid].channel.send(msg)
        except Exception:
            pass


def new_MOMdispatcher(controller_host, ip_port):
    mom = MOMDispatcher(controller_host, ip_port)
    mom.run()
    return mom


def new_TCPdispatcher(controller_host, ip_port):
    tcp = TCPDispatcher(controller_host, ip_port)
    tcp.run()
    return tcp


def new_dispatcher(controller_host, transport):
    dispatcher_type = transport[0]
    ip_port = transport[1]
    if dispatcher_type == TCP:
        return TCP, new_TCPdispatcher(controller_host, ip_port)
    if dispatcher_type == MOM:
        return MOM, new_MOMdispatcher(controller_host, ip_port)
    else:
        raise NotFoundDispatcher()


def get_current():
    current_th = current_thread()
    if current_th in threads:
        return threads[current_th]


def send_timeout(channel, rpc_id):
    if rpc_id in pending:
        del pending[rpc_id]
        msg = {}
        msg[TYPE] = ERROR
        msg[RESULT] = TimeoutError()
        channel.send(msg)


def send_timeout_multi(channel, rpc_id_list):
    send_message = False
    for rpc_id in rpc_id_list:
        if rpc_id in pending:
            del pending[rpc_id]
            send_message = True
    if send_message:
        msg = {}
        msg[TYPE] = ERROR
        msg[FROM] = 'timeout_controller'
        msg[RESULT] = 'error'
        channel.send(msg)


def launch(func, params=[]):
    th = Thread(target=func, args=params)
    threads[th] = 'atom://localhost/'+func.__module__+'/'+func.__name__
    th.start()
    th.join()
    controller.sleep(2)
    host = controller.get_host()
    host._shutdown()


def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    host = controller.get_host()
    host.shutdown()
    sys.exit(0)


def serve_forever(func, params=[]):
    threads[current_thread()] = 'atom://localhost/'+func.__module__+'/'+func.__name__
    func(*params)
    signal.signal(signal.SIGINT, signal_handler)
    print 'Press Ctrl+C to kill the execution'
    while True:
        controller.sleep(1)
