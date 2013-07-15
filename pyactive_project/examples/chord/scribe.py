"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""

from chord_protocol import Node, update, k, MAX, betweenE
from pyactive.controller import init_host, serve_forever, start_controller, interval, launch, sleep
from pyactive.exception import TimeoutError
from aop import *
import random

I ={}
def id(MAX):
    # Returns a random number between 0 y 2^k (64)
    return int(random.uniform(0, MAX))

""" Uniform distribution of identifiers across the identifier space"""
def uniform(N, I, max):
    sample = []
    for next in range(N):
        tmp_id = id(max)
        # We are looking for an ID which does not exist in the network, because could happen that
        # the random function gives us an existing value.
        while tmp_id in I:
            tmp_id = id(max)  
        # Once we are sure the value is unique, we store it in the identifier space dictionary
        I[tmp_id] = tmp_id
        # We add it to the list where we have the N identifiers of the uniformly found nodes
        sample.append(tmp_id)  
    return sample

class ScribeMessage():
    
    def __init__(self,id=None, source=None, op=None, parent=None, text=None):
        self.id = id
        self.source = source
        self.operation = op         
        self.parent_node = parent   
        self.text_message = text    
        self.first_node = source    
    
    def get_source_node(self):
        return self.source_node

class ScribeNode(Node):
    
    _sync = {'init_node':'1', 'successor':'2','find_successor':'5', 'get_predecessor':'2','closest_preceding_finger':'2'
             ,'closest_preceding_fingerE':'2','join':'20', 'is_alive':'2','get_my_topics':'5', 
             'get_routing_topic_nodes':'2','lookup_subscribe':'10'}
    _async = ['set_predecessor','run_to_false','remove_son','deliver','subscribe','set_parent', 'set_successor', 'show_finger_node',
               'stabilize', 'notify', 'fix_finger','set_my_topics', 'del_my_topics','leave']
    _ref = ['set_predecessor','remove_son','subscribe','set_parent','lookup_subscribe', 'get_predecessor', 
            'successor', 'find_successor','closest_preceding_finger','closest_preceding_fingerE','deliver', 'join', 
            'set_successor','notify']
    _parallel = ['stabilize', 'fix_finger']
    
    def __init__(self):
        super(ScribeNode, self).__init__()
        self.my_topics = {}            
        self.routing_topic_nodes = {}   
        self.parent_node = None
        
    def set_parent(self, parent):
        self.parent_node = parent
    def run_to_false(self):
        self.run = False
    def get_routing_topic_nodes(self):
        return self.routing_topic_nodes.copy()
    
    def remove_son(self, id, value):
        self.routing_topic_nodes.get(id).remove(value)
        
    def set_my_topics(self, id, value):
        self.my_topics[id] = value
        
    def get_my_topics(self):
        return self.my_topics
    
    def del_my_topics(self, id):
        del self.my_topics[id]
        
    """CountingHops decorator"""
    @CountingHops("ScribeNode")
    def successor(self):
        return Node.successor(self)
    
    """CountingHops decorator"""
    @CountingHops("ScribeNode")
    def closest_preceding_fingerE(self, msg):
        for i in range(k-1,-1,-1):
            if betweenE(int(self.finger[i].get_id()), int(self.id), msg.id):
                return self.finger[i]
        return self.proxy
    
    def lookup_subscribe(self, msg):
        if betweenE(msg.id, int(self.predecessor.get_id()), int(self.id)):
            return self.proxy
        n = self.proxy
        
        while not betweenE(msg.id, int(n.get_id()), int(n.successor().get_id())):
            n = n.closest_preceding_fingerE(msg)   
            
            if not n.is_alive():
                return None 
            
            if int(n.get_id()) == msg.id:
                n.deliver(msg)
                return n           
            #Call to introduce some functionality in each forwarder ;) 
            if n != None:  
                n.subscribe(msg)
        if n.successor().is_alive():
            n.successor().deliver(msg)
            return n.successor()
        
        n.successor().leave()
        return None
    
    def subscribe(self, msg):
        if (msg.operation=='s'):    #Subscribe
            
            if ((msg.id in self.routing_topic_nodes.keys()) and (msg.source not in self.routing_topic_nodes.get(msg.id))):
                self.routing_topic_nodes.get(msg.id).append(msg.source)
            else:
                self.routing_topic_nodes[msg.id] = [msg.source]
            print 'Forward: Source id: ' + str(msg.source.get_id()) + ' --> Node id: ' + str(self.id) + ' (Msg id: ' + str(msg.id) + ')'
            

            #Change message information for next node.
            msg.source.set_parent(self.proxy)
            msg.source = self.proxy      
            

    def deliver(self, msg):
        
        if (msg.operation=='s'):    #Subscribe
            

            if ((msg.id in self.routing_topic_nodes.keys()) and (msg.source not in self.routing_topic_nodes.get(msg.id))):     #Si ya tengo ese id, hago append()
                self.routing_topic_nodes.get(msg.id).append(msg.source)
            else:
                self.routing_topic_nodes[msg.id] = [msg.source]
                
            msg.first_node.set_my_topics(msg.id, self.id)                        
            print 'Deliver: Source id: ' + str(msg.source.get_id()) + ' --> Node id: ' + str(self.id) + ' (Msg id: ' + str(msg.id) + ')'
            msg.source.set_parent(self.proxy)
            
        elif (msg.operation=='p'):  #Publish
            
            if (msg.id in self.my_topics.keys()):
                print 'Node ' + str(self.id) + ' receives the message ' + str(msg.text_message)
                
            if (msg.id in self.routing_topic_nodes.keys()):
                for node in self.routing_topic_nodes.get(msg.id):
                    node.deliver(msg)
            
        elif (msg.operation=='u'):          #Unsubscribe
            
            if ((msg.id not in self.my_topics.keys()) or (msg.first_node.get_id() == self.id)):
                if ((msg.id in self.parent_node.get_routing_topic_nodes().keys()) and 
                    (msg.source in self.parent_node.get_routing_topic_nodes().get(msg.id))):
                    
                    #Clear my node from path of my father
                    self.parent_node.remove_son(msg.id, msg.source)
                    print 'Deliver: Source id: ' + str(msg.source.get_id()) + ' --> Node id: ' + str(self.parent_node.get_id()) + ' (Msg id: ' + str(msg.id) + ')'
            
                    if (len(self.parent_node.get_routing_topic_nodes().get(msg.id)) == 0):
                        if (self.parent_node.get_id() != msg.first_node.get_my_topics(msg.id)[0]):
                            msg.source = self.parent_node  
                            self.parent_node.deliver(msg)
                        else:
                            msg.first_node.del_my_topics(msg.id)
            print 'Unsubscribed successfully'
                            
            
            
def menu(host, nodes_h, num_nodes):
    fin = False
    while (fin == False):
        print ("-------------Menu-----------------")
        print ("1 - Subscribe to a topic")
        print ("2 - Unsubscribe a topic")
        print ("3 - Publish a message")
        print ("4 - Show Finger Table")
        print ("5 - Leave Node of Chord")
        print ("6 - Exit")
        op = int(raw_input("Choose an option: "))
        if (op==1):     #Subscribe to a topic
            nod = int(raw_input("Choose a node: "))
            src = nodes_h[nod]
            top = raw_input("Topic's name to subscribe: ")
            key = hash(top)%num_nodes 
            print key, src.get_id()
            src.lookup_subscribe(ScribeMessage(key,src,'s',-1,''))
                
        elif (op==2):   #Unsubscribe a topic
            nod = int(raw_input("Choose a node: "))
            src = nodes_h[nod]
            top = raw_input("Topic's name to unsubscribe: ")
            key = hash(top)%num_nodes 
            src.deliver(ScribeMessage(key,src,'u',-1,''))
            
        elif (op==3): #Publish a message
            nod = int(raw_input("Choose a node: "))
            src = nodes_h[nod]
            top = raw_input("Topic's name to publish: ")
            key = hash(top)%num_nodes  
            msg = raw_input("Write the message: ")
            topics = src.get_my_topics()
            try:
                topics = topics.get(key)
                node_responsible = nodes_h[int(topics[0])-1]   
                node_responsible.deliver(ScribeMessage(key,src,'p',-1, msg)) 
            except:
                print "This node hasn't this topic"
        elif (op==4):
            nod = int(raw_input("Choose a node: "))
            src = nodes_h[nod]
            src.show_finger_node()
        elif (op==5):
            nod = int(raw_input("Chose a node: "))
            src = nodes_h[nod]
            src.leave()
        
        elif (op==6):
            print 'Exit'
            host.shutdown()
            fin = True
            
        else:
            None          
def start_node():            
    nodes_h = {}
    num_nodes = 10
    cont = 1
    retry = 0
    index=0
    tcpconf = ('tcp', ('127.0.0.1', 1238))
    host = init_host(tcpconf)
#    momconf = ('mom',{'name':'s1','ip':'127.0.0.1','port':61613,'namespace':'/topic/test'})
#    host = init_host(momconf)

    for i in range(num_nodes):
        nodes_h[i] = host.spawn_id(str(cont), 'scribe', 'ScribeNode', [])
        cont += 1
    for i in range(num_nodes):    
        nodes_h[i].init_node()
    
    while index < num_nodes:
        try:
            if(nodes_h[index].join(nodes_h[0])):
                print "True"
            interval(5, update, nodes_h[index])
            index += 1
            retry = 0
#            sleep(0.2)
        except TimeoutError:
            retry += 1
            if retry > 3:
                index += 1
    num_nodes -= 1
    "Lookup test"
    menu(host, nodes_h, num_nodes)
    
def start_remote_node():
    nodes_h = {}
    num_nodes = 10
    cont = 11
    retry = 0
    index=0
    tcpconf = ('tcp', ('127.0.0.1', 6377))
    host = init_host(tcpconf)
#    momconf = ('mom',{'name':'c1','ip':'127.0.0.1','port':61613,'namespace':'/topic/test'})
#    host = init_host(momconf)
    for i in range(num_nodes):
        nodes_h[i] = host.spawn_id(str(cont), 'scribe', 'ScribeNode', [])
        cont += 1
    for i in range(num_nodes):    
        nodes_h[i].init_node()
#    remote_aref = 'mom://s1/scribe/ScribeNode/1'   
    remote_aref = 'atom://127.0.0.1:1238/scribe/ScribeNode/2'
    remote_node = host.lookup(remote_aref)

    while index < num_nodes:
        try:
            if(nodes_h[index].join(remote_node)):
                print "True"
            interval(5, update, nodes_h[index])
            index += 1
            retry = 0
        except(TimeoutError):
            retry += 1
            print 'Timeout Error: Attempts '+retry
            if retry > 3:
                index += 1
    menu(host, nodes_h, num_nodes)

def failed_nodes(nodes_h, f, num_nodes):
    print '--------------'
    print ' FAILED NODES:'
    print '--------------'
    print f, num_nodes
    percen = int((f / 100) * num_nodes)
    for i in range(percen):
        nodes_h[i].run_to_false()
        print 'Node \'%s\' failed!' % nodes_h[i].get_id()
    print '\n'
    
def test():
    # We get the list with the N node identifiers, uniformly distributed in theidentifier space dictionary.
    nodes_h = {}
    num_nodes = 40
    retry = 0
    index=0
    sample = uniform(num_nodes, I, MAX)
        # Decorator that controls the number of hoops. Enabled.
    HopCounter.enable(True)
    # Counter at 0.
    
    "Lookup test"
#    tcpconf = ('tcp', ('127.0.0.1', 1238))
#    host = init_host(tcpconf)
    momconf = ('mom',{'name':'s1','ip':'127.0.0.1','port':61613,'namespace':'/topic/test'})
    host = init_host(momconf)

    for i in range(num_nodes):
        nodes_h[i] = host.spawn_id(str(sample[i]), 'scribe', 'ScribeNode', [])
    for i in range(num_nodes):    
        nodes_h[i].init_node()
    
    while index < num_nodes:
        try:
            if(nodes_h[index].join(nodes_h[0])):
                print "True"
            interval(20, update, nodes_h[index])
            index += 1
            retry = 0
#            sleep(0.2)
        except TimeoutError:
            retry += 1
            if retry > 3:
                index += 1

    "select the set of failed peers"
    # We randomly set some nodes as fallen using the flag failed = True.
#    Standard code initially given:
#    for node_id in sample:
#        if random.random() < f:
#            dht[node_id].failed = True
    print 'Id List', sample
#    f = raw_input("Number of failed nodes:")
#    failed_nodes(nodes_h, float(f), num_nodes)

    f = raw_input("Number of failed nodes:")

    HopCounter.resetCounter()
    num = 0
    NUM_QUERIES = 5000
    for i in range(NUM_QUERIES):
        "Return a random element from the non-empty sequence seq. If seq is empty, raises IndexError."
        # We randomly get a node identifier, in the sample list, which we found before.
        src = random.choice(nodes_h)
        # We randomly get a number btween 0 and MAX.
        key = int(random.uniform(0, MAX - 1))
        dst = src.lookup_subscribe(ScribeMessage(id=key))
        num += ((dst != None) and 1) or 0
    
    "disable"
    print HopCounter.getHopCounter()
    print ("<L> = %f Pr[success] = %f" % (HopCounter.getMeanHops(NUM_QUERIES), num / float(NUM_QUERIES)))
    print 'finish!!'
    
def main():
    start_controller('pyactive_thread')
    launch(test)
if __name__ == "__main__":
    main() 
