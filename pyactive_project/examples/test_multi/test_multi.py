'''
@author: Edgar Zamora Gomez <edgar.zamora@urv.cat>
'''
from pyactive.controller import init_host, serve_forever, start_controller

from pyactive.Multi import AMulti

class Server(object):
    _sync = {}
    _async = ['add_actors', 'add']
    _ref = ['add_actors']
    _parallel = []
    
    def add_actors(self, list_actors):
        self.amulti = AMulti(list_actors, self._atom)
    
    def add(self, x, y):
        self.amulti.add(x, y)
        

class Calc():
    _sync = {}
    _async = ['add']
    _ref = []
    _parallel = []
        
    def add(self, x, y):
        print x+y
        
        
def test():
    
    calcs = []
    
    tcpconf = ('tcp',('127.0.0.1',6664))
    host = init_host(tcpconf)
    
    for i in range(4):
        calcs.append(host.spawn_id(str(i),'test_multi','Calc',[]))
    
    server = host.spawn_id('serv', 'test_multi', 'Server', [])
    server.add_actors(calcs)
    
    server.add(4,4)
    
  
   
def main():
    start_controller('pyactive_thread')
    serve_forever(test)
    
   
if __name__ == "__main__":
    main()
  
   

    