"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""

from pyactive.controller import init_host, serve_forever, start_controller, interval
from pyactive.exception import TimeoutError, PyactiveError


k = 14
MAX = 2 ** k


def decr(value, size):
    if size <= value:
        return value - size
    else:
        return MAX - (size - value)
        
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
    
def update(ref):
    ref.stablilize()
    ref.fix_finger()
    
def exit1(ref):
    ref.leave()
    
def show(ref):
    ref.show_finger_node()
#    ref.get_fingers()

class succ_err(PyactiveError):
    def __str__(self):
        return 'The successor is down'

#-------END_BETWEEN-------#

class Node():
    _sync = {'init_node':'1', 'successor':'2','find_successor':'5', 'get_predecessor':'2','closest_preceding_finger':'2','join':'20', 'is_alive':'2'}
    _async = ['set_predecessor', 'set_successor', 'show_finger_node', 'stabilize', 'notify', 'fix_finger']
    _ref = ['set_predecessor', 'get_predecessor', 'successor', 'find_successor', 'closest_preceding_finger', 'join', 'set_successor', 'notify']
    _parallel = ['stabilize', 'fix_finger']
    def __init__(self):
        self.finger = {}
        self.start = {}
        self.indexLSucc = 0
        self.finger = {}
        self.currentFinger = 1
    

    def init_node(self):
        for i in range(k):
            self.start[i] = (int(self.id) + (2 ** i)) % (2 ** k)
        return True
    
    # SUCCESSOR #

    def successor(self):
        try:
#            print 'successor', self.finger[0]
            return self.finger[0]
        except(TimeoutError):
            print succ_err()
        
    # FIND SUCCESSOR #

    def  find_successor(self, id):
        try:
            if betweenE(id, int(self.predecessor.get_id()), int(self.id)):
#                print 'self.proxy', self.proxy
                return self.proxy
            n = self.find_predecessor(id)
#            print 'find_successor 2', n.successor(), n
            return n.successor()
        except(succ_err):
            raise succ_err()
        except(TimeoutError):
            raise TimeoutError()

    def get_fingers(self):
        self.finger[0].show_finger_succ(self.proxy)     
        
    # END FIND SUCCESSOR #

    def get_predecessor(self):
        return self.predecessor
    

    def set_predecessor(self, pred):
        self.predecessor = pred
    
    #Iterative programming
    def find_predecessor(self, id):
        try:
            if id == int(self.id):
                return self.predecessor
            n1 = self.proxy
            while not betweenE(id, int(n1.get_id()), int(n1.successor().get_id())): 
                n1 = n1.closest_preceding_finger(id)
            return n1
        except(succ_err):
            raise succ_err()
        except(TimeoutError):
            raise TimeoutError()
    

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
#                self.successorList[i] = self.proxy
            self.predecessor = self.proxy
            self.run = True
#            print 'finger', self.finger
            return True
        else:
            try:
                self.init_finger_table(n1)
            except:
                print 'Join failed'
                return False
            else:
#                self.init_successor_list()
                self.run = True
#                print 'finger', self.finger
                return True
            
    def init_finger_table(self, n1):
        try:
            self.predecessor = self.proxy
            self.finger[0] = n1.find_successor(self.start[0]) 
        except(succ_err):
            raise succ_err
        except(TimeoutError):
            raise TimeoutError()
        else:
            for i in range(k - 1):
                self.finger[i + 1] = self.finger[0]
        
      
    def is_alive(self):
        if (self.run == True):
            return True
        else:
            return False           
               
   
    def stablilize(self):
        x = self.finger[0].get_predecessor()
        if(between(int(x.get_id()), int(self.id), int(self.finger[0].get_id()))):
            self.set_successor(x)
        self.finger[0].notify(self.proxy)
        
        
    
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
            
   
    def leave(self):
        print 'bye'
        self.finger[0].set_predecessor(self.predecessor)
        self.predecessor.set_successor(self.finger[0])
        self._atom.stop()

        
      
    def set_successor(self, succ):
        self.finger[0] = succ
    
    
    def show_finger_node(self):
        print 'Finger table of node ' + self.id
        print 'Predecessor' + self.predecessor.get_id()
        print 'start:node'
        for i in range(k):
            try:
#                print self.finger
                print str(self.start[i]) + ' : ' + self.finger[i].get_id() 
            except:
                print'ERRORRRR!!!(doesnt have method get_id()',  self.finger[i]
        print '-----------'
        
        
def hash(line):
    import sha
    key = long(sha.new(line).hexdigest(), 16)
    return key
    
def printNodes(node):
    print ' Ring nodes:'
    end = node
    print node.get_id()
    while end != node.successor():
        node = node.successor()
        print node.get_id()
    print '-----------'

def showFinger(node):
    print 'Finger table of node ' + str(node.get_id())
    print 'start:node'
    for i in range(k):
        print str(node.start[i]) + ' : ' + str(node.finger[i].get_id())  
    print '-----------'
        
       
def save_log(ref):   
    ref.to_uml('chord_test2')


def start_node():            
    nodes_h = {}
    num_nodes = 10
    cont = 201 
    retry = 0
    index = 0
#    tcpconf = ('tcp', ('127.0.0.1', 6375))
#    host = init_host(tcpconf)
    momconf = ('mom',{'name':'c1','ip':'127.0.0.1','port':61613,'namespace':'/topic/test'})
    host = init_host(momconf)
    
    for i in range(num_nodes):
        nodes_h[i] = host.spawn_id(str(cont), 'chord_remote', 'Node', [])
        cont += 1
    for i in range(num_nodes):    
        nodes_h[i].init_node()
    remote_aref = 'mom://s1/chord/Node/5'
#    remote_aref = 'atom://127.0.0.1:1238/chord/Node/1'
    remote_node = host.lookup(remote_aref)
    while index < num_nodes:
        try:
            if(nodes_h[index].join(remote_node)):
                print "True"
            interval(15, update, nodes_h[index])
            index += 1
            retry = 0
        except TimeoutError:
            retry += 1
            if retry > 3:
                break
        
    interval(100, show, nodes_h[0])
    interval(100, show, nodes_h[num_nodes/2])
    interval(100, show, nodes_h[num_nodes - 1])
        
def main():
    start_controller('pyactive_thread')
    serve_forever(start_node)
    
if __name__ == "__main__":
    main() 