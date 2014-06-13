"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from pyactive.controller import init_host, launch, start_controller, sleep
    
class Node():
    _sync = {'send_msg':'50', 'return_msg':'50'}
    _async = ['print_some', 'start', 'start_n3']
    _parallel = ['start']
    _ref = []
    def __init__(self,id=None,n2=None):
        self.id = id
        self.now=False  
        self.remote = n2
        self.cnt = 0
        
    #@parallel
    #@sync(100)
    def send_msg(self):
        print self.remote
        msg = self.remote.return_msg()
        print msg
        return True
    
    
    #@sync(100)
    def return_msg(self):
        sleep(10)
        return 'Hello World'
    
    #@async
    def print_some(self):
        print 'hello'
        
    #@parallel    
    #@async
    def start(self):
        print 'call ...'
        msg = self.remote.return_msg()
        print msg
        
    #@async
    def start_n3(self):
        for i in range(6):
            self.remote.print_some()
            
def test1():
    host = init_host()
    n2 = host.spawn_id('2','parallel1','Node',['n2'])
    n1 = host.spawn_id('1','parallel1','Node',['n1',n2]) 
    n3 = host.spawn_id('3','parallel1','Node',['n3',n1]) 
    n1.start()
    sleep(2)
    n3.start_n3()
    sleep(15)   
#    n2.stop()
#    n1.stop()
#    n3.stop() 
def main():
    start_controller('tasklet')
    launch(test1)
 
if __name__ == "__main__":
    main()