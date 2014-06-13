'''
Created on 13/02/2014

@author: Edgar Zamora Gomez
'''

from paxos_protocol import Acceptor, Learner, Proposer
from pyactive.controller import init_host, start_controller, launch, serve_forever, sleep, interval
from pyactive.Multi import SMulti, AMulti
import random
from pyactive.constants import *
from urlparse import urlparse
from pyactive.util import Ref
N_PROPOSERS = 4
N_ACCEPTORS = 5
N_LEARNERS = 5

class LogUML():
    _sync = {}
    _async = ['notify', 'to_uml']
    _ref = []
    _parallel = []
    
    def __init__(self):
        self.events = []
        self.nameNodes = {}
        self.cnt2 = 0
        self.cont = 0
        self.nodes = {}
        self.titles = {}
        self.list_nodes = []
        
 

    def notify(self,msg):  
        self.events.append(msg.copy())
#         print msg
   
    def to_uml(self, filename):
        uml = []
        uml_names = []
        uml.append('\n')
        for msg in self.events:
            #try:
            fromref = urlparse(msg[FROM])
            toref = urlparse(msg[TO])
            if not self.nodes.has_key(fromref.path):
                self.list_nodes.append(fromref.path)
                self.nodes[fromref.path] = fromref.path
            if not self.nodes.has_key(toref.path):
                self.list_nodes.append(toref.path)
                self.nodes[toref.path] = toref.path
         
#            self.nodes.add(fromref.path)
#            self.nodes.add(toref.path)
            self.titles[fromref.path] = msg[FROM]
            self.titles[toref.path] = msg[TO]   
            #except:
            #    None
        while(self.cnt2 < len(self.list_nodes)):
            evt = 'n'+str(self.cnt2)+':Process[p] "'+self.titles[self.list_nodes[self.cnt2]]+'"\n'
            self.nameNodes[self.titles[self.list_nodes[self.cnt2]]] = "n"+str(self.cnt2)
            uml_names.append(evt)
            self.cnt2 += 1
        
                
        uml.append('\n')
        
        for msg in self.events:
            if msg[TYPE]==CALL:
                #try:
                fromref = urlparse(msg[FROM])
                toref = urlparse(msg[TO])
                nfrom = 'n'+str(self.list_nodes.index(fromref.path))
                nto = 'n'+str(self.list_nodes.index(toref.path))
                if isinstance(msg[PARAMS], list):
                    params = []
                    for node in msg[PARAMS]:
                        if isinstance(node, Ref):
                            params.append(self.nameNodes.get(str(node.get_aref())))
                        else:
                            params.append(node)
                    evt = nfrom+':'+nto+'.'+msg[METHOD]+'('+str(params)+')\n'
                else:
                    evt = nfrom+':'+nto+'.'+msg[METHOD]+'('+str(msg[PARAMS])+')\n'
                #except:
                #    None        
            else:
                #try:
                fromref = urlparse(msg[FROM])
                toref = urlparse(msg[TO])
                nfrom = 'n'+str(self.list_nodes.index(fromref.path))
                nto = 'n'+str(self.list_nodes.index(toref.path))
                if isinstance(msg[RESULT], list):
                    result = []
                    for node in msg[RESULT]:
                        result.append(self.nameNodes.get(str(node.get_aref())))
                    evt = nfrom+':'+nto+'.'+msg[METHOD]+'()='+str(result)+'\n'    
                elif isinstance(msg[RESULT], Ref):
                    evt = nfrom+':'+nto+'.'+msg[METHOD]+'()='+self.nameNodes.get(str(msg[RESULT].get_aref()))+'\n'    
                else:
                    evt = nfrom+':'+nto+'.'+msg[METHOD]+'()='+str(msg[RESULT])+'\n'
                #except:
                #    None
            try:
                uml.append(evt)
            except:
                None
        
        self.events = []
        write_uml(filename+'_names.sdx', uml_names)
        write_uml(filename+'.sdx', uml)
    
def write_uml(filename, events):    
    f3 = open(filename, 'a')
    f3.writelines(events)
    f3.close()
    
def save_log(ref):   
    ref.to_uml('paxos_example')  
     
class Log():
    _sync = {}
    _async = ['notify']
    _ref = []
    _parallel = []
    #@async
    def notify(self,msg):
        print msg
        
def test():
    lP = []
    lA = []
    lL = []
    host = init_host()
#     log = host.spawn_id('log', 'main', 'LogUML', [])
#     host.set_tracer(log)
#      interval(1, save_log, log)
    for i in range(0, N_LEARNERS):
        l = host.spawn_id(str(i), 'paxos_protocol_multi_instance', 'Learner',[N_ACCEPTORS])
        lL.append(l)
    for i in range(0, N_ACCEPTORS):
        a = host.spawn_id(str(i+N_LEARNERS), 'paxos_protocol_multi_instance', 'Acceptor', [N_ACCEPTORS])
        print 'hola edsa'
        a.set_multi(lL)
        lA.append(a)    
    for i in range(0,N_PROPOSERS):
        p = host.spawn_id(str(i+N_LEARNERS+N_ACCEPTORS+5), 'paxos_protocol_multi_instance', 'Proposer', [N_ACCEPTORS])
       
        lP.append(p)
    lP[0].set_multi([lA[0], lA[1],lA[2]])
    lP[1].set_multi([lA[2], lA[3],lA[4]])
    lP[2].set_multi([lA[0], lA[1],lA[2]])
    lP[3].set_multi([lA[2], lA[3],lA[4]])
#     p = AMulti(lP)
#     p.prepare()
    for a in range(10):
        num = int(random.random() * 100)
        print a, num
        num_p = int(random.random() * 100%N_PROPOSERS)
        lP[num_p].set_proposal(num)
#     lP[3].prepare()
#     lP[0].prepare()
#     lP[1].prepare()
#     lP[2].prepare()
    
def main():
    start_controller('pyactive_thread')
    serve_forever(test)
    
if __name__ == "__main__":
    main()