"""
Created on 20/02/2014

Author: Edgar Zamora Gomez   <edgar.zamora@urv.cat>
"""

import unittest


from pyactive.controller import init_host, launch,start_controller, sleep
from pyactive.exception import TimeoutError
class Server(object):
    _sync = {'throw_timeout': '1', 'hello_world': '8'}
    _async = ['print_some', 'start', 'start2']
    _ref = []
    _parallel = ['hello_world']
    
    def __init__(self, n2 = None):
        self.remote = n2
 
    def hello_world(self):
        sleep(3)
        return 'hello_world'
    def start(self):
        print 'start call'
        response = self.remote.hello_world()
        print 'response', response
    def start2(self):
        for i in range(5):
            self.remote.print_some()

    def print_some(self):
        print 'hello'
    

    def throw_timeout(self):
        sleep(3)
        return 'timeout test'
    

def test1():
    host = init_host()
    n2 = host.spawn_id('2','test_sync_parallel','Server',[])
    n1 = host.spawn_id('3','test_sync_parallel','Server',[n2]) 
    n3 = host.spawn_id('4','test_sync_parallel','Server',[n2]) 
    n1.start()
    sleep(1)
    n3.start2()
    sleep(15)   

        
def main():
    start_controller('pyactive_thread')
    launch(test1)        
if __name__ == '__main__':
    main()