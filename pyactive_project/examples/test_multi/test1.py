"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from pyactive.controller import init_host, serve_forever, launch, start_controller
from pyactive.Multi import AMulti
class Server(object):
    _sync = {}
    _async = ['add', 'add_atoms']
    _parallel = []
    _ref = ['add_atoms']
 
    def add_atoms(self, list_actors):
        self.multi = AMulti(list_actors, self._atom)
        
    def add(self, x, y):
        self.multi.add(x, y)
        

class Calc(object):
    _sync = {}
    _async = ['add']
    _parallel = []
    _ref = []
    
    def __init__(self, hola=None):
        self.hola = hola
    def add(self, x, y):
        print x+y
        
def test1():
    
    calc = []
    
    tcpconf = ('tcp',('127.0.0.1',6664))
    host = init_host(tcpconf)
    for i in range(4):
        calc.append(host.spawn_id(str(i),'test1','Calc',[]))
    
    server = host.spawn_id(str(30),'test1','Server',[])
    server.add_atoms(calc)
    
    server.add(4,4)

if __name__ == '__main__':
    start_controller('pyactive_thread')
    serve_forever(test1)