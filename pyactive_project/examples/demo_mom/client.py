'''
Created on 14/07/2014

@author: edgar
'''
from pyactive.controller import init_host, launch, serve_forever,  start_controller, sleep, interval
from pyactive.exception import TimeoutError
class Client():
    _sync = {'get_reference':'1'}
    _async = ['subscribe', 'unsubscribe', 'run', 'stop']
    _ref = []
    _parallel = []
    
    def __init__(self, server):
        self.server = server
        self.run_state = False

    def subscribe(self):
        self.reference = self.server.add_client(self.proxy)
        print 'subsribe id:', self.id,' reference: ', self.reference
    
    def unsubscribe(self):
        print 'unsubscribe id:', self.id, ' state: ', self.server.delete_client(self.proxy)
    
    def run(self):
        print self.id, ' running...'
        self.run_state = True
        self.run_cycle()
    
    def stop(self):
        self.run_state = False
            
    def run_cycle(self):
        while self.run_state:
            self.server.do_something(['12', 'true', 'rasr'])
            sleep(3)
    def get_reference(self):        
        return self.reference
     
        
def test3():
    references = []
    momconf = ('mom',{'name':'c1','ip':'127.0.0.1','port':61613,'namespace':'/topic/test'})
    host = init_host(momconf)
    #host = init_host(('127.0.0.1',4329),True)
    #host = Host(host)
    #oref = 'env2:simple:s1:Server'
    aref = 'mom://s1/server/Server/0'
    ref = host.lookup(aref)
    nodes = {}
    for i in range(1, 1000):
        nodes[i] = host.spawn_id(str(i), 'client', 'Client', [ref])
        nodes[i].subscribe()
    
    #for i in range(100):
    #    ref.resta(34,2)

#    try:
#        ref.wait_a_lot()
#    except TimeoutError:
#        print 'correct timeout'
    
    #sleep(1)
    #host.shutdown()
    list = []
    for node in nodes.values():
        r = node.get_reference()
        if not r in list:
            list.append(r)
        else:
            print 'error: some client has the same reference'
    print 'all ok'
    print ref.get_references()    

def main():
    start_controller("pyactive_thread")
    serve_forever(test3)
    #test1()
    
if __name__ == "__main__":
    main()