"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""
from pyactive.util import Ref
from urlparse import urlparse
from pyactive.constants import *


def save_log(ref):   
    ref.to_uml('chord_test2')
    
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