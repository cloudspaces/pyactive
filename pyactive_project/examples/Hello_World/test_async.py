"""
Author: Edgar Zamora Gomez   <edgar.zamora@urv.cat>
"""
import unittest

from pyactive.controller import init_host, launch, start_controller

class Server():
    def __init__(self):
        self.name = None
    
       
    #@async
    def hello_world(self):
        self.name = 'async done'
    
    #@sync(1)     
    def get_name(self):
        return self.name
    
    #@sync(2)
    def registry_obj(self, obj):
        self.obj = obj
        return True
    
def test_hello(test):
    n1 = test.host.spawn_id('1', 'test_async', 'Server', [])
    n1.hello_world()
    
    result = n1.get_name()
    test.assertEqual(result, 'async done')
    
def test_registry_object(test):
    n1 = test.host.spawn_id('2', 'test_async', 'Server', [])
    n2 = test.host.spawn_id('3', 'test_async', 'Server', [])
    
    test.assertTrue(n1.registry_obj(n2))
    
class Test(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        super(Test, cls).setUpClass()
        start_controller('pyactive_thread')
        cls.host = init_host()

    def test_hello(self):
        launch(test_hello, [self])    
    
    def test_registry_object(self):
        launch(test_registry_object, [self])
        
    @classmethod
    def tearDownClass(cls):
        super(Test, cls).tearDownClass()
        cls.host.shutdown()



if __name__ == "__main__":
    unittest.main()