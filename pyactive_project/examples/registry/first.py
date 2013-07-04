"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""

from pyactive.controller import init_host, serve_forever, start_controller
class Registry():
    def __init__(self):
        self.names = {}
   
    #@ref
    #@sync(50)
    def bind(self,name,atom):
        print 'binding ...'
        self.names[name] = atom
        print 'Parameters',name, self.names[name]
        return True
    
    #@async
    def hello(self):
        print 'hello'
    
    #@sync(50)
    def lookup(self,name):
        return self.names[name]
   
    #@sync(50)
    def get_names(self):
        return self.names.keys()
   
    
    #@sync(50)
    def get_values(self):
        return self.names.values()


def test3():
    
    tcpconf = ('tcp',('127.0.0.1',6664))
    host = init_host(tcpconf)
    
    registry = host.spawn_id('1','first','Registry',[])
    print 'hola'
    registry.bind('first', host)
   

def main():
    start_controller('pyactive_thread')
    serve_forever(test3)
    
   
if __name__ == "__main__":
    main()