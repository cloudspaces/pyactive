"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from collections import deque
from urlparse import urlparse
from taskletDelay import sleep
from tcp_server import Server
import stackless
import copy

from pyactive.abstract_actor import Abstract_actor
from pyactive.constants import METHOD, MODE, SRC, TO, FROM, TARGET, TYPE, RESULT, PARAMS, RPC_ID, SYNC, CALL, ERROR, MULTI, TCP
from pyactive.exception import TimeoutError, NotFoundDispatcher

pending = dict()
tasklets = dict()


class Actor(Abstract_actor):

    def __init__(self):
        Abstract_actor.__init__(self)
        self.channel = stackless.channel()
        self.activate = stackless.channel()
        self.queue = deque([])
        self.channel.preference = -1
        self.callbacks = {}
        self.sync_parallel = []

    def run(self):
        Abstract_actor.run(self)
        self.in_task = stackless.tasklet(self.enqueue)()
        self.msg_task = stackless.tasklet(self.processMessage)()
        tasklets[self.msg_task] = self.aref

    def registry_object(self, obj):
        self.obj = obj

    def stop(self):
        self.running = False

    def enqueue(self):
        while True:
            msg = self.channel.receive()
            self.queue.append(msg)
            self.receive_all()

    def set_pending(self, rpc_id):
        pending[rpc_id] = 1

    def receive_all(self):
        while self.channel.balance > 0:
            msg = self.channel.receive()
            self.queue.append(msg)
        if self.running:
            self.activate.send(None)

    def processMessage(self):
        while self.running:
            while len(self.queue) > 0:
                self.receive(self.queue.popleft())
            self.activate.receive()

    def send(self, msg):
        msg[SRC] = self.channel
        msg[TO] = self.aref
        msg[TARGET] = self.target
        msg[TYPE] = CALL
        if msg[MODE] == SYNC:
            pending[msg[RPC_ID]] = 1

        self.out.send(msg)

    def init_parallel(self):
        '''Put parallel wrapper on object methods that need'''
        for name in self.sync_parallel:
            setattr(self.obj, name, ParallelSyncWraper(getattr(self.obj, name), self.aref, self, name))
        for name in self.async_parallel:
            setattr(self.obj, name, ParallelAsyncWraper(getattr(self.obj, name), self.aref))

    def receive_result(self):
        '''recive result of synchronous calls'''
        msg = self.channel.receive()
        return msg[RESULT]

    def receive(self, msg):
        ''' receive messages and invokes object method'''

        invoke = getattr(self.obj, msg[METHOD])
        params = msg[PARAMS]
        result = None
        # try:
        if msg[METHOD] in self.sync_parallel:
            self.callbacks[msg[METHOD]] = msg
            result = invoke(*params)
        else:
            result = invoke(*params)
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

        # except PyactiveError, e:
        #     result = PyactiveError(e)
        #     msg[ERROR] = 1
        # except TypeError, e2:
        #     result = MethodError()
        #     msg[ERROR]=1

    def receive_sync(self, result, name):
        msg = self.callbacks[name]
        del self.callbacks[name]
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

    # @sync(2)
    def ping(self):
        return True

    def get_proxy(self):
        return self.host.load_client(self.channel, self.aref, get_current())


class MultiActor(Actor):
    def receive_result(self):
        '''receive result of synchronous calls'''
        result = self.channel.receive()
        return result[FROM], result[RESULT]


class ParallelSyncWraper():
    def __init__(self, send, aref, principal_thread, name):
        self.__name = name
        self.__send = send
        self.__aref = aref
        self.__principal_thread = principal_thread

    def __call__(self, *args, **kwargs):
        t = stackless.tasklet(self.__send)(*args)
        tasklets[t] = self.__aref

    def invoke(self, func, args=[], kwargs=[]):
        result = func(*args, **kwargs)
        self.__principal_thread.receive_sync(result, self.__name)


class ParallelAsyncWraper():

    def __init__(self, send, aref):
        self.__send = send
        self.__aref = aref

    def __call__(self, *args, **kwargs):
        t = stackless.tasklet(self.__send)(*args)
        tasklets[t] = self.__aref


class TCPDispatcher(Actor):

    def __init__(self, host, addr):
        Actor.__init__(self)
        ip, port = addr
        self.name = ip + ':' + str(port)
        self.conn = Server(ip, port, self)
        self.addr = addr
        self.host = host

        self.callback = {}

    # @async
    def _stop(self):
        self.conn.close()
        super(TCPDispatcher, self)._stop()

    def receive(self, msg):
        if msg[MODE] == SYNC and msg[TYPE] == CALL:
            self.callback[msg[RPC_ID]] = msg[SRC]
        msg[SRC] = self.addr

        self.conn.send(msg)

    def is_local(self, name):
        return name == self.name

    def on_message(self, msg):
        try:
            if msg[TYPE] == RESULT:
                if MULTI in msg:
                    target = self.callback[msg[RPC_ID]]
                    target.send(msg)
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
                aurl = urlparse(aref)
                self.host.objects[aurl.path].channel.send(msg)
        except Exception as e:
            print e, 'TCP ERROR2'


def new_TCPdispatcher(host, dir):
    tcp = TCPDispatcher(host, dir)
    tcp.run()
    return tcp


def new_dispatcher(host, transport):
    '''Select and create new dispatcher '''
    dispatcher_type = transport[0]
    if dispatcher_type == TCP:
        return new_TCPdispatcher(host, transport[1])
    else:
        raise NotFoundDispatcher()


def get_current():
    current = stackless.getcurrent()
    if current in tasklets:
        return tasklets[current]


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
    t1 = stackless.tasklet(func)(*params)
    tasklets[t1] = 'atom://localhost/' + func.__module__ + '/' + func.__name__

    while t1.scheduled:
        stackless.schedule()
        sleep(0.01)


def serve_forever(func, params=[]):
    t1 = stackless.tasklet(func)(*params)
    tasklets[t1] = 'atom://localhost/' + func.__module__ + '/' + func.__name__
    while True:
        stackless.run()
        sleep(0.01)
