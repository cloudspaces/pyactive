'''
@author: Edgar Zamora Gomez <edgar.zamora@urv.cat>
'''
from pyactive.controller import init_host, serve_forever, start_controller, sleep
import time
from pyactive.Multi import AMulti, SMulti

class Server(object):
    _sync = {}
    _async = ['add_actors', 'add', 'sync_add','print_references']
    _ref = ['add_actors']
    _parallel = []
    
    def add_actors(self, list_actors):
        print list_actors
        self.amulti = AMulti(list_actors)
        self.smulti = SMulti(list_actors, self._atom)
        self.list_actors = list_actors
    def add(self, x, y):
        self.amulti.add(x, y)
    
    def sync_add(self, x, y):
        result =  self.smulti.sync_add(x, y)
        print result.values()
    def print_references(self):
        for a in range(16):
            print 'hola'
            print self.smulti.get_reference().keys()
class Calc():
    _sync = {'sync_add':'1', 'get_reference':'1'}
    _async = ['add']
    _ref = ['get_reference']
    _parallel = []
        
    def add(self, x, y):
        print x+y
        
    def sync_add(self, x, y):
        sleep(2)
        return x+y
    def get_reference(self):
        print self.proxy
        return self.proxy
class Calc1():
    _sync = {'sync_add':'1', 'get_reference':'1'}
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
        calcs.append(host.spawn_id(str(i),'test_multi','Calc',[]))
    
    for i in range(2):
        calcs.append(host.spawn_id(str(i),'test_multi','Calc1',[]))
    
    server = host.spawn_id('serv', 'test_multi', 'Server', [])
    server.add_actors(calcs)
    
    server.add(4,4)
    server.sync_add(3,3)
    server.print_references()
   
def main():
    start_controller('pyactive_thread')
    serve_forever(test)
    
   
if __name__ == "__main__":
    main()
  
   

    