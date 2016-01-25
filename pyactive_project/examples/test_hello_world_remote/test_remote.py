"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
import unittest


from pyactive.controller import init_host, launch, start_controller, sleep
import pyactive.exception as e


class Server():
    _sync = {'hello_world': '2', 'throw_timeout': '2'}
    _async = []
    _ref = []
    _parallel = []

    def hello_world(self):
        print 'hola que tal!!!'
        return 'hello_world'

    def throw_timeout(self):
        sleep(3)
        return 'timeout test'


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        tcpconf = ('tcp',('127.0.0.1',6664))
        start_controller('pyactive_thread')
        self.host = init_host(tcpconf)


    def test_hello(self):
        n1 = self.host.spawn_id('1', 'test_remote', 'Server', [])
        response = n1.hello_world()
        self.assertEqual(response, 'hello_world')

    def test_throw_timeout(self):
        n2 = self.host.spawn_id('2', 'test_remote', 'Server', [])
        try:
            n2.throw_timeout()
            self.assertTrue(False)
        except(e.TimeoutError):
            self.assertTrue(True)

    @classmethod
    def tearDownClass(cls):
        super(Test, cls).tearDownClass()
        cls.host.shutdown()

if __name__ == '__main__':
    unittest.main()
