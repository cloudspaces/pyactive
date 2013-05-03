"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""

from pyactive.controller import init_host, launch, start_controller, interval, sleep

class Server():
    
    
    #@sync(1) 
    def add(self,x,y):
        return x+y
    
    #@async
    def substract(self,x,y):
        print 'substract',x-y
        

class Log():
    
    #@async
    def notify(self,msg):
        print msg,' logged !!!'


  

def test_log():
    host = init_host()
    log = host.spawn_id('log', 'log','Log',[])
    host.set_tracer(log)
    ref = host.spawn_id('1','log','Server',[])
    ref.substract(6,5)
    print ref.add(5,5)
    sleep(1)
 

def main():
    start_controller('pyactive_thread')
    launch(test_log)
  
if __name__ == "__main__":
    main()