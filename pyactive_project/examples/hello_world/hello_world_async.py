from pyactive.controller import init_host, launch,start_controller, sleep

class Server():
    _sync = {}
    _async = ['hello_world']
    _parallel = []
    _ref = []
    def hello_world(self):
        print 'hello world'

def test():
    host = init_host()

    # parameters 1 = 'id', 'test_async' = module name, 'Server' = class name
    n1 = host.spawn_id('1', 'hello_world_async', 'Server', [])

    n1.hello_world()

if __name__ == '__main__':
    #you can change the parameter 'tasklet' to 'pyactive_thread' if you like thread controller.
    start_controller('pyactive_thread')
    launch(test)
