"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
import unittest


from pyactive.controller import init_host, launch, start_controller, sleep
import pyactive.exception as e


class Server():
    #@sync(1)
    def hello_world(self):
        return 'hello_world'
    
    #@sync(1)
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
        tcpconf = ('tcp',('127.0.0.1',6842))
        start_controller('pyactive_thread')
        cls.host = init_host(tcpconf)
        
        
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