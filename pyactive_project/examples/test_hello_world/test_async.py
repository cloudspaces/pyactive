"""
Author: Edgar Zamora Gomez   <edgar.zamora@urv.cat>
"""
import unittest

from pyactive.controller import init_host, launch, start_controller

class Server():
    _sync = {'registry_obj': '2', 'get_name': '1'}
    _async = ['hello_world']
    _ref = []
    _parallel = []

    def __init__(self):
        self.name = None
        print 'init_server'


    def hello_world(self):
        self.name = 'async done'

    def get_name(self):
        return self.name

    def registry_obj(self, obj):
        self.obj = obj
        return True

class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(Test, cls).setUpClass()
        start_controller('pyactive_thread')
        cls.host = init_host()

    def test_hello(self):
        n1 = self.host.spawn_id('1', 'test_async', 'Server', [])
        n1.hello_world()

        result = n1.get_name()
        self.assertEqual(result, 'async done')

    def test_registry_object(self):
        n1 = self.host.spawn_id('2', 'test_async', 'Server', [])
        n2 = self.host.spawn_id('3', 'test_async', 'Server', [])

        self.assertTrue(n1.registry_obj(n2))

    @classmethod
    def tearDownClass(cls):
        super(Test, cls).tearDownClass()
        cls.host.shutdown()



if __name__ == "__main__":
    print 'hola que tal!!'
    unittest.main()
