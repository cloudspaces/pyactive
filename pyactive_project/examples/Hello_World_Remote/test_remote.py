"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
import unittest


from pyactive.controller import init_host, launch, start_controller, sleep
import pyactive.exception as e


class Server():
    _sync = {'hello_world': '2', 'throw_timeout': '1'}
    _async = []
    _ref = []
    _parallel = []
    
    def hello_world(self):
        return 'hello_world'
    
    def throw_timeout(self):
        sleep(3)
        return 'timeout test'


def test_hello(test):
    n1 = test.host.spawn_id('1', 'test_remote', 'Server', [])
    response = n1.hello_world()
    test.assertEqual(response, 'hello_world')
    
def test_throw_timeout(test):
    n2 = test.host.spawn_id('2', 'test_remote', 'Server', [])
    try:
        n2.throw_timeout()
        test.assertTrue(False)
    except(e.TimeoutError):
        test.assertTrue(True)
 
class Test(unittest.TestCase):
     
    @classmethod
    def setUpClass(cls):
        super(Test, cls).setUpClass()
        conf = ('tcp',('127.0.0.1',1234))
        start_controller('pyactive_thread')
        cls.host = init_host(conf)
        
        
    def test_hello(self):
        launch(test_hello, [self])
    
    def test_throw_timeout(self):
        launch(test_throw_timeout, [self])
    
    @classmethod
    def tearDownClass(cls):
        super(Test, cls).tearDownClass()
        cls.host.shutdown()
        
if __name__ == '__main__':
    unittest.main()