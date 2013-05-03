"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from pyactive.controller import init_host, launch, start_controller

class Test():
    def __init__(self):
        self.name = None
    
       
    #@async
    def hello_world(self):
        print 'async done'
    
    #@sync(1)     
    def get_name(self):
        return self.name
    #@sync(2)
    def registry_obj(self, obj):
        self.obj = obj
        return True
    
def test3():
    
#    tcpconf = ('tcp',('127.0.0.1',6664))
    host = init_host()
 
    test = host.spawn_id('1','launch','Test',[])
    test.hello_world()
    host.shutdown()

if __name__ == "__main__":
    start_controller('tasklet')
    launch(test3)