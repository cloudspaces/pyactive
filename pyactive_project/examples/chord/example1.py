from pyactive.controller import init_host, serve_forever, start_controller, interval_host, sleep
from chord_protocol import show, update

def example1():
    nodes = [1,8,14,21,32,38,42,48,51,56]
    nodes_h = {}

    tcpconf = ('tcp', ('127.0.0.1', 1234))
    host = init_host(tcpconf)

    # Create and initialize nodes
    for i in range(len(nodes)):
        print 'iteration', i
        nodes_h[i] = host.spawn_id(str(nodes[i]), 'chord_protocol', 'Node', [])
        nodes_h[i].init_node()

    for i in range(len(nodes)):
        j = 0 if i is 0 else i-1
        try:
            nodes_h[i].join(nodes_h[j])
        except:
            print 'Node %s fails' % str(i)
        else:
            interval_host(host, 1, update, nodes_h[i])

    interval_host(host, 30, show, nodes_h[0])
    interval_host(host, 31, show, nodes_h[5])
    interval_host(host, 32, show, nodes_h[9])

def main():
    start_controller('pyactive_thread')
    serve_forever(example1)

if __name__ == "__main__":
    main()
