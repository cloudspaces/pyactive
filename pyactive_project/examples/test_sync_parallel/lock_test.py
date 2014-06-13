'''
Created on 05/05/2014

@author: Edgar Zamora Gomez
'''

from pyactive.controller import init_host, launch,start_controller, sleep
class Node(object):
    _sync = {'send_msg':'50','start2':'20', 'return_msg':'50'}
    _async = ['print_some', 'start', 'start_n3', 'registry_object']
    _parallel = ['start', 'start2']
    _ref = ['registry_object']
    
    def __init__(self,id=None):
        self.id = id
        self.now=False  
        self.cnt = 0
    def registry_object(self, remote):
        self.remote = remote
    def send_msg(self):
        print self.remote
        msg = self.remote.return_msg()
        print msg
        return True

    def return_msg(self):
        sleep(10)
        return 'Hello World'

    def print_some(self):
        print 'hello'

    def start(self):
        print 'call ...'
        msg = self.remote.return_msg()
        print msg
    def start2(self):
        msg = self.remote.return_msg()
        return msg
    def start_n3(self):
        for i in range(6):
            self.remote.print_some()
            
def test1():
    host = init_host()
    n2 = host.spawn_id('2','lock_test','Node',['n2'])
    sleep(2)
    n1 = host.spawn_id('1','lock_test','Node',['n1']) 
    n1.registry_object(n2)
    n3 = host.spawn_id('3','lock_test','Node',['n3']) 
    n3.registry_object(n1)

    n1.start()
    n3.start_n3()
    sleep(15)
    result =  n1.start2() 
    print 'response_start2', result
    sleep(20)
#    n2.stop()
#    n1.stop()
#    n3.stop() 
def main():
    start_controller('pyactive_thread')
    launch(test1)
 
if __name__ == "__main__":
    main()