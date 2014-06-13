'''
Created on 13/02/2014

@author: Edgar Zamora Gomez
'''
from multi_paxos import Server
from mpaxos_main import save_log
from pyactive.controller import init_host, start_controller, launch, serve_forever, sleep, interval
from pyactive.Multi import SMulti, AMulti
import random
from pyactive.constants import *

N_SERVERS = 25
class Key_value_store(object):
    _sync = {'put':'3', 'get':'2'}
    _async = ['internal_get']
    _ref = []
    _parallel = ['put', 'get']
    
    def __init__(self, paxos_leader):
        self.proposer = paxos_leader
        self.current_value = None
    def put(self, value):
        if self.proposer.set_proposal(value, self.proxy) == False:
            return False

        return 'OK'
    def internal_get(self, current_value):
        print 'hello internal_get', current_value

    def get(self):
        '''Return list of accepted values'''
        #We can check if this value is really replicated to majority servers
        return self.proposer.get_accepted_values()

def update(ref):
    ref.heartbeat()
    
def test():
    server_list = []
    key_value = []
    host = init_host()
    log = host.spawn_id('log', 'mpaxos_main', 'LogUML', [])
    host.set_tracer(log)
    interval(1, save_log, log)
    for i in range(0, N_SERVERS):
        l = host.spawn_id(str(i), 'multi_paxos', 'Server',[N_SERVERS])
        server_list.append(l)
    for i in range(0, N_SERVERS):
        if i == 0:
            server_list[i].set_multi(server_list[1:])
        else:
            server_list[i].set_multi(server_list[:i] + server_list[i+1:])
        
        interval(2, update, server_list[i])       

    
    server_list[N_SERVERS - 1].set_leader() 
    for i in range(0, N_SERVERS ): 
        key_value.append(host.spawn_id(str(i + N_SERVERS), 'key_value_store', 'Key_value_store',[server_list[i]]))
   
    
    try:
        while True:
            try:
                print '1 - PUT'
                print '2 - GET'
                value=int(raw_input('Choose an option that you can view above:'))
                if value == 1:
                    value=int(raw_input('Enter a new value:'))
                    num = int(random.random() * 100)%N_SERVERS
                    print num
                    print key_value[num].put(value)
                elif value == 2:
                    '''Get log of random server'''
                    num = int(random.random() * 100)%N_SERVERS
                    print num, key_value[num].get()
 
#                     for num in range(N_SERVERS):
#                         print num,  server_list[num].get()

                else:
                    print 'Choose an option between 1 and 2'
            except ValueError:
                print "Not a number"
    except KeyboardInterrupt:
        pass # do cleanup here
         

    
#     print server_list[N_SERVERS - 1].set_proposal(int(random.random() * 100))
#     print server_list[N_SERVERS - 1].set_proposal(int(random.random() * 100))
#     print server_list[N_SERVERS - 1].set_proposal(int(random.random() * 100))
#     print server_list[N_SERVERS - 1].set_proposal(int(random.random() * 100))    
#    lP[0].set_multi([lA[0], lA[1],lA[2]])
#    lP[1].set_multi([lA[2], lA[3],lA[4]])
#    lP[2].set_multi([lA[0], lA[1],lA[2]])
#    lP[3].set_multi([lA[2], lA[3],lA[4]])
#     p = AMulti(lP)
#     p.prepare()
    
#     print server_list[0].prepare()
#     print server_list[1].prepare()
#     print server_list[2].prepare()
#     print server_list[N_SERVERS - 1].prepare()
#     sleep(5)
#     server_list[N_SERVERS - 1].set_proposal(num) 
#     print server_list[N_SERVERS - 1].prepare()
def main():
    start_controller('pyactive_thread')
    serve_forever(test)

if __name__ == "__main__":
    main()