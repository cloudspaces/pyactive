from pyactive.controller import init_host, serve_forever, start_controller, interval_host, sleep
from chord_protocol import show, update, k
from time import time
import random

def hash(line):
    import sha
    key=long(sha.new(line).hexdigest(),16)
    return key

def id():
    return long(random.uniform(0,2**k))

def example2():

    nodes_h = {}

    tcpconf = ('tcp', ('127.0.0.1', 1234))
    host = init_host(tcpconf)

    t1  = time()
    # Create and initialize nodes
    for i in range(100):
        nodes_h[i] = host.spawn_id(str(id()), 'chord_protocol', 'Node', [])
        nodes_h[i].init_node()

    for i in range(len(nodes_h)):
        j = 0 if i is 0 else i-1
        try:
            nodes_h[i].join(nodes_h[j])
        except:
            print 'Node %s fails' % str(i)
        else:
            interval_host(host, 0.5, update, nodes_h[i])

    t2 = time()
    print 'Time to create 100 nodes'
    print t2 - t1

    # Wait to give time to chord to fix its tables.
    # Note that if we use the class chord_improved we will need less time to fix the node tables.
    sleep(30)

    key = hash('pedro')
    print key
    found = nodes_h[0].find_predecessor(key)
    print found.get_id()



def main():
    start_controller('pyactive_thread')
    serve_forever(example2)

if __name__ == "__main__":
    main()
