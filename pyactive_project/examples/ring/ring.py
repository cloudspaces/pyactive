"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
import unittest

from pyactive.controller import init_host, launch,start_controller, sleep

       
class Node():
    _sync = {'get_cnt': '1', 'hello_sync': '1'}
    _async = ['hello', 'start', 'start2']
    _ref = []
    _parallel = []
    
    def __init__(self,id=None,n2=None):
        self.id = id
        self.now=False  
        self.remote = n2  
        self.cnt = 0
        
    #@sync(1)
    def get_cnt(self):
        return self.cnt
    #@async
    def hello(self):
        self.cnt += 1
     
    #@sync(1)        
    def hello_sync(self):
        self.cnt += 1
        return self.cnt
        
    #@async   
    def start(self):
        for i in range(100):
            self.remote.hello()
    #@async
    def start2(self):
        for i in range(100):
            z = self.remote.hello_sync()
                        

def test1(test):
    n2  = test.host.spawn_id('0','ring','Node',['n2'])
    n1 = test.host.spawn_id('1','ring','Node',['n1',n2]) 
    n3 = test.host.spawn_id('2','ring','Node',['n3',n2]) 
    n1.start()     
    n3.start()
    sleep(0.5)
    cnt = n2.get_cnt()
    test.assertEqual(cnt, 200, "testing load oneway") 

class Simple(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        start_controller('pyactive_thread')
        self.host = init_host()
         
    def test_load_oneway(self):
        launch(test1,[self])
        
    def tearDown(self):
        self.host.shutdown()
      
    def tearDownModule(self):
        sleep(0.2)
      
if __name__ == '__main__':
    unittest.main()