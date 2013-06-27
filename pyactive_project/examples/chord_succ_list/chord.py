"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""

from pyactive.controller import init_host, serve_forever, start_controller, interval,sleep
from pyactive.exception import TimeoutError, PyactiveError



k = 14
MAX = 2 ** k


        
#---------BETWEEN---------#
def between(value, init, end):
    if init == end:
        return True
    elif init > end :
        shift = MAX - init
        init = 0
        end = (end + shift) % MAX
        value = (value + shift) % MAX
    return init < value < end

def Ebetween(value, init, end):
    if value == init:
        return True
    else:
        return between(value, init, end)

def betweenE(value, init, end):
    if value == end:
        return True
    else:
        return between(value, init, end)
    
def stablilize(ref):
    ref.stabilize()
def fix_finger(ref):
    ref.fix_finger()
    
def exit1(ref):
    ref.leave()
    
def show(ref):
    ref.show_finger_node()
    ref.show_finger_list()
#    ref.get_fingers()

class succ_err(PyactiveError):
    def __str__(self):
        return 'The successor is down'

#-------END_BETWEEN-------#

class Node():
    
    _sync = {'init_node':'1','give_successor_list':'5', 'successor':'2','find_successor':'5', 'get_predecessor':'2','closest_preceding_finger':'2','join':'20', 'is_alive':'2'}
    _async = ['set_predecessor', 'set_successor', 'show_finger_node', 'stabilize', 'notify', 'fix_finger']
    _ref = ['set_predecessor','give_successor_list', 'get_predecessor', 'successor', 'find_successor', 'closest_preceding_finger', 'join', 'set_successor', 'notify']
    _parallel = ['stabilize', 'fix_finger']
    
    def __init__(self):
        self.finger = {}
        self.start = {}
        self.indexLSucc = 1
        self.currentFinger = 0
        self.successorList = []
        self.retry = [0,0]
    
    
    def init_node(self):
        for i in range(k):
            self.start[i] = (int(self.id) + (2 ** i)) % (2 ** k)
        return True
    
    # SUCCESSOR #
 
    def successor(self):
        return self.successorList[0]
        
    # FIND SUCCESSOR #
 
    def  find_successor(self, id):
        if betweenE(id, int(self.predecessor.get_id()), int(self.id)):
#                print 'self.proxy', self.proxy
            return self.proxy
        n = self.find_predecessor(id)
#            print 'find_successor 2', n.successor(), n
        return n.successor()
    
    def get_fingers(self):
        self.successorList[0].show_finger_succ(self.proxy)     
        
    # END FIND SUCCESSOR #
    
    def get_predecessor(self):
        return self.predecessor
    
  
    def set_predecessor(self, pred):
        self.predecessor = pred
    
    #Iterative programming
    def find_predecessor(self, id):
        if id == int(self.id):
            return self.predecessor
        n1 = self.proxy
        while not betweenE(id, int(n1.get_id()), int(n1.successor().get_id())): 
            n1 = n1.closest_preceding_finger(id)
        return n1

   
    def closest_preceding_finger(self, id):
        try:
            for i in range(k - 1, -1, -1):
                if between(int(self.finger[i].get_id()), int(self.id), id):
                    return self.finger[i]
            return self.proxy
        except(TimeoutError):
            raise succ_err()
    
    

    def join(self, n1):
        """if join return false, the node not entry in ring. Retry it before"""
        if self.id == n1.get_id():
            for i in range(k):
                self.finger[i] = self.proxy
                self.successorList.append(self.proxy)
            self.predecessor = self.proxy
            self.run = True
            return True
        else:
            try:
                self.init_finger_table(n1)
            except:
                print 'Join failed'
                return False
            else:
                self.init_successor_list()
                self.run = True
                print 'predecessor', self.predecessor
                return True
            
    def init_finger_table(self, n1):
        self.predecessor = self.proxy
        self.finger[0] = n1.find_successor(self.start[0]) 
        for i in range(k - 1):
            self.finger[i + 1] = self.finger[0]
    
    def init_successor_list(self):
        self.successorList.append(self.finger[0])
        for i in range(k - 1):
            self.successorList.append(self.successorList[i].successor())
        
        
    def update_list_successor(self):
        try:
            if(self.successorList[0].is_alive()):
                auxList = self.successorList[0].give_successor_list()
                for i in range(k-1):
                    self.successorList[i+1] = auxList[i]
                self.retry[0] = 0
        except(TimeoutError):
            self.retry[0] += 1
            if self.retry[0] > 5:
                self.retry[0] = 0
                self.update_successor()
#             
    def update_successor(self):
        searching = True
        while(searching and self.indexLSucc < k):
            n = self.successorList[self.indexLSucc]
            self.indexLSucc += 1
            self.successorList[0] = n
            try:
                if(n.is_alive()):
                    self.set_successor(n)
                    searching = False
            except(TimeoutError): 
                searching = True
        self.indexLSucc = 1
        self.update_list_successor()
#        
        
  
    def give_successor_list(self):
        return self.successorList[:]
    
       
    def is_alive(self):
        if self._atom.running:
            return True
        else:
            return False           
 
    def stabilize(self):
        try:
            x = self.successorList[0].get_predecessor()
            self.retry[1] = 0
        except(TimeoutError):
            self.retry[1] += 1
            if self.retry[1] > 5:
                self.retry[1] = 0
                self.update_successor()
            
        else:
            if(between(int(x.get_id()), int(self.id), int(self.successorList[0].get_id()))):
                self.set_successor(x)
            self.update_list_successor()
            self.successorList[0].notify(self.proxy)
        
        

    def notify(self, n):
        if(self.predecessor.get_id() == self.id or between(int(n.get_id()), int(self.predecessor.get_id()), int(self.id))):
            self.predecessor = n

    def fix_finger(self):
        #el cas 0 no es mira perque ja tenim la listSuccessor
        if(self.currentFinger <= 0 or self.currentFinger >= k):
            self.currentFinger = 1
        try:
            self.finger[self.currentFinger] = self.find_successor(self.start[self.currentFinger])
        except:
            None
        finally:
            self.currentFinger += 1
#            
  
    def leave(self):
        print 'bye bye!'
        self.successorList[0].set_predecessor(self.predecessor)
        self.predecessor.set_successor(self.successorList[0])
        self._atom.stop()

        
  
    def set_successor(self, succ):
        self.successorList[0] = succ
        self.finger[0] = succ


    def show_finger_list(self):
        print 'Successor List of node ' + self.id
        for i in range(k):
            print self.successorList[i].get_id()
    

    def show_finger_node(self):
        print 'Finger table of node ' + self.id
        print self.id
        print 'Predecessor' + self.predecessor.get_id()
        print 'start:node'
        for i in range(k):
            print str(self.start[i]) + ' : ' + self.finger[i].get_id() 
        print '-----------'
        
       
def save_log(ref):   
    ref.to_uml('chord_test2')
    
def leave(ref):
    ref.leave()
    
    
def start_node():            
    nodes_h = {}
    num_nodes = 50
    cont = 1
    retry = 0
    j = 0
    tcpconf = ('tcp', ('127.0.0.1', 1432))
    host = init_host(tcpconf)
#    momconf = ('mom',{'name':'s1','ip':'127.0.0.1','port':61613,'namespace':'/topic/test'})
#    host = init_host(momconf)
#    log = host.spawn_id('log','chord_log','LogUML',[])
#    host.set_tracer(log)
    for i in range(num_nodes):
        nodes_h[i] = host.spawn_id(str(cont), 'chord', 'Node', [])
        cont += 1
    for i in range(num_nodes):    
        nodes_h[i].init_node()
        
    while j < num_nodes:
        try:
            if(nodes_h[j].join(nodes_h[0])):
                print "True"
            
            interval(20, stablilize, nodes_h[j])
            interval(20, fix_finger, nodes_h[j])
            sleep(1)
                
        except TimeoutError:
            retry += 1
            if retry > 3:
                break
        else:
            j += 1
    interval(200, show, nodes_h[0])
    interval(200, show, nodes_h[num_nodes /2])
    interval(200, show, nodes_h[num_nodes -1])
#    interval(15, save_log, log)
        
def main():
    start_controller('pyactive_thread')
    serve_forever(start_node)
    
if __name__ == "__main__":
    main() 