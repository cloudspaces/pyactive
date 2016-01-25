"""
Author: Edgar Zamora Gomez   <edgar.zamora@urv.cat>
"""
import unittest


from pyactive.controller import init_host, launch,start_controller, sleep
import pyactive.exception as e

class Server():
    _sync = {'throw_timeout': '1', 'hello_world': '1'}
    _async = []
    _ref = []
    _parallel = []

    def hello_world(self):
        return 'hello_world'

    def throw_timeout(self):
        sleep(3)
        return 'timeout test'


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(Test, cls).setUpClass()
        start_controller('pyactive_thread')
        cls.host = init_host()

    def test_hello(self):
        n1 = self.host.spawn_id('1', 'test_sync', 'Server', [])
        response = n1.hello_world()
        self.assertEqual(response, 'hello_world')

    def test_throw_timeout(self):
        n2 = self.host.spawn_id('2', 'test_sync', 'Server', [])
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
