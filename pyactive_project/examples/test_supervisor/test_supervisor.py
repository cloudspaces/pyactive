'''
Created on 12/11/2013

@author: Edgar Zamora Gomez
'''
from pyactive.controller import init_host, serve_forever, start_controller, sleep
import time
from pyactive.Multi import AMulti, SMulti
from pyactive.supervisor import Supervisor

class Server(object):
    _sync = {'add_actors':'20'}
    _async = ['add', 'sync_add','print_references']
    _ref = ['add_actors']
    _parallel = []

    def add_actors(self, list_actors):
        self.supervisor = Supervisor(5, 3, self._atom, list_actors)
        self.amulti = AMulti(list_actors)
        self.smulti = SMulti(self._atom, list_actors)
        return True
    def add(self, x, y):
        self.amulti.add(x, y)

    def sync_add(self, x, y):
        result =  self.smulti.sync_add(x, y)
        print result.values()
    def print_references(self):
        print self.smulti.get_reference().values()
    def failure_detect(self, from_actor):
        print 'failure', from_actor

class Calc(object):
    _sync = {'sync_add':'20', 'get_reference':'20'}
    _async = ['add']
    _ref = ['get_reference']
    _parallel = []

    def add(self, x, y):
        print x+y

    def sync_add(self, x, y):
        sleep(2)
        return x+y
    def get_reference(self):
        return self.proxy

class Calc1(object):
    _sync = {'sync_add':'20', 'get_reference':'20'}
    _async = ['add']
    _ref = ['get_reference']
    _parallel = []

    def add(self, x, y):
        print x+y
    def sync_add(self, x, y):
        return x+y
    def get_reference(self):
        return self.proxy

def test():

    calcs = []

    tcpconf = ('tcp',('127.0.0.1',6664))
    host = init_host(tcpconf)

    for i in range(1):
        calcs.append(host.spawn_id(str(i),'test_supervisor','Calc',[]))

    for i in range(2):
        calcs.append(host.spawn_id(str(i),'test_supervisor','Calc1',[]))

    server = host.spawn_id('serv', 'test_supervisor', 'Server', [])
    server.add_actors(calcs)

    server.add(4,4)
    server.sync_add(3,3)
    server.print_references()

def main():
    start_controller('pyactive_thread')
    serve_forever(test)


if __name__ == "__main__":
    main()
