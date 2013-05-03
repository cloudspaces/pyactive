"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from pyactive.controller import init_host, serve_forever, start_controller

class Registry():
    def __init__(self):
        self.names = {}
    #@async
    def hello(self):
        print 'Hello'
    #@sync(2)
    def hello_sync(self):
        return 'hello_sync'
    
    

def test3():
    
    tcpconf = ('tcp',('127.0.0.1',1234))
    host = init_host(tcpconf)
    
    registry = host.spawn_id('1','server','Registry',[])

    
def main():
    start_controller('tasklet')
    serve_forever(test3)

if __name__ == "__main__":
    main()