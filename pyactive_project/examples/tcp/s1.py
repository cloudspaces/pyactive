"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""
from pyactive.controller import init_host, serve_forever, start_controller, sleep
class Server():
    #@sync(1)
    def add(self,x,y):
        return x+y
    #@async
    def substract(self,x,y):
        print 'subtract',x-y
    #@sync(1)    
    def wait_a_lot(self):
        sleep(2)
        return 'ok'
   

def test3():
    tcpconf = ('tcp',('127.0.0.1',1234))
    host = init_host(tcpconf)
  
    server = host.spawn_id('0','s1','Server',[])
    server.substract(4,3)
    print server.add(66,7)
   
   


def main():
    start_controller('tasklet')
    serve_forever(test3)
    
if __name__ == "__main__":
    main()