'''
Created on 07/01/2014

@author: cesk002
'''
'''
Created on 04/11/2013

@author: Edgar Zamora Gomez
'''


from pyactive.controller import init_host, start_controller, launch, serve_forever, sleep, interval
from pyactive.Multi import SMulti, AMulti
import random
from pyactive.constants import *
from urlparse import urlparse
from pyactive.util import Ref
N_PROPOSERS = 4
N_ACCEPTORS = 5
N_SERVERS = 4

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
                        if isinstance(node, Ref):
                            result.append(self.nameNodes.get(str(node.get_aref())))
                        else:
                            result.append(node)

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
    ref.to_uml('multi_paxos')  
     
class Log():
    _sync = {}
    _async = ['notify']
    _ref = []
    _parallel = []
    
    def notify(self,msg):
        print msg
 
def update(ref):
    ref.heartbeat()
def test():
    lP = []
    lA = []
    lL = []
    host = init_host()
    log = host.spawn_id('log', 'mpaxos_main', 'LogUML', [])
    host.set_tracer(log)
    interval(1, save_log, log)
    for i in range(0, N_SERVERS):
        l = host.spawn_id(str(i), 'multi_paxos', 'Server',[N_SERVERS])
        lL.append(l)
    for i in range(0, N_SERVERS):
        if i == 0:
            lL[i].set_multi(lL[1:])
        else:
            lL[i].set_multi(lL[:i] + lL[i+1:])
        
        interval(2, update, lL[i])       

    lL[N_SERVERS - 1].set_leader()         
    for i in range(0,N_SERVERS):        
        num = int(random.random() * 100)
        print i, num
        lL[i].set_proposal(num)
    
    print lL[N_SERVERS - 1].set_proposal(int(random.random() * 100))
    print lL[N_SERVERS - 1].set_proposal(int(random.random() * 100))
    print lL[N_SERVERS - 1].set_proposal(int(random.random() * 100))
    print lL[N_SERVERS - 1].set_proposal(int(random.random() * 100))    
#    lP[0].set_multi([lA[0], lA[1],lA[2]])
#    lP[1].set_multi([lA[2], lA[3],lA[4]])
#    lP[2].set_multi([lA[0], lA[1],lA[2]])
#    lP[3].set_multi([lA[2], lA[3],lA[4]])
#     p = AMulti(lP)
#     p.prepare()
    
    print lL[0].prepare()
    print lL[1].prepare()
    print lL[2].prepare()
    print lL[N_SERVERS - 1].prepare()
    sleep(5)
    lL[N_SERVERS - 1].set_proposal(num) 
    print lL[N_SERVERS - 1].prepare()
def main():
    start_controller('tasklet')
    serve_forever(test)
    
if __name__ == "__main__":
    main()
    