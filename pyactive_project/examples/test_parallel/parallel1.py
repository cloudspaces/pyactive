"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from pyactive.controller import init_host, launch, start_controller, sleep

class Node(object):
    _sync = {'send_msg':'50', 'return_msg':'50'}
    _async = ['print_some', 'start', 'start_n3', "registry_node"]
    _parallel = ['start']
    _ref = ["registry_node"]

    def registry_node(self, n2):
        self.remote = n2

    def send_msg(self):
        print self.remote
        msg = self.remote.return_msg()
        print msg
        return True

    def return_msg(self):
        print 'im here'
        sleep(10)
        print 'after sleep'
        return 'Hello World'

    def print_some(self):
        print 'hello print some'

    def start(self):
        print 'call ...'
        msg = self.remote.return_msg()
        print msg

    def start_n3(self):
        for i in range(6):
            self.remote.print_some()

def test1():
    host = init_host()
    n2 = host.spawn_id('2','parallel1','Node',[])
    n1 = host.spawn_id('1','parallel1','Node',[])
    n3 = host.spawn_id('3','parallel1','Node',[])
    n2.registry_node(n1)
    n1.registry_node(n2)
    n3.registry_node(n1)
    n1.start()
    sleep(1)
    n3.start_n3()
    sleep(10)


def main():
    start_controller('pyactive_thread')
    launch(test1)

if __name__ == "__main__":
    main()
