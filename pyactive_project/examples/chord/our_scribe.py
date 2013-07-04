"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""

from chord_protocol import Node, update, k, betweenE
from pyactive.controller import init_host, serve_forever, start_controller, interval
from pyactive.exception import TimeoutError

class ScribeMessage():
    
    def __init__(self,id, source,  parent, text):
        self.id = id
        self.source = source
        self.parent_node = parent   
        self.text_message = text    
        self.first_node = source    
    
    def get_source_node(self):
        return self.source_node

class ScribeNode(Node):
    
    _sync = {'init_node':'1', 'successor':'2','find_successor':'5', 'get_predecessor':'2','closest_preceding_finger':'2'
             ,'closest_preceding_fingerE':'3','join':'20', 'is_alive':'2','get_my_topics':'5', 
             'get_routing_topic_nodes':'2','fail_stop_find_successor':'5'}
    _async = ['set_predecessor','remove_son','subscribe_owner','forward','publish','unsubscribe','set_parent', 'set_successor', 'show_finger_node',
               'stabilize', 'notify', 'fix_finger','set_my_topics', 'del_my_topics','leave']
    _ref = ['set_predecessor','remove_son','forward','set_parent','fail_stop_find_successor','publish','unsubscribe', 'get_predecessor', 
            'successor', 'find_successor','closest_preceding_finger','closest_preceding_fingerE','subscribe_owner', 'join', 
            'set_successor','notify']
    _parallel = ['stabilize', 'fix_finger']
    
    def __init__(self):
        super(ScribeNode, self).__init__()
        self.my_topics = {}            
        self.routing_topic_nodes = {}   
        self.parent_node = None
        
    def set_parent(self, parent):
        self.parent_node = parent
        
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
    
    def closest_preceding_fingerE(self, msg):
        for i in range(k-1,-1,-1):
            if betweenE(int(self.finger[i].get_id()), int(self.id), msg.id):
                return self.finger[i]
        return self.proxy
    
    def fail_stop_find_successor(self, msg):
        if betweenE(msg.id, int(self.predecessor.get_id()), int(self.id)):
            return self.proxy
        n = self.proxy
        
        print msg.id, int(n.get_id()), int(n.successor().get_id())
        while not betweenE(msg.id, int(n.get_id()), int(n.successor().get_id())):
            n = n.closest_preceding_fingerE(msg)    
            if int(n.get_id()) == msg.id:
                n.subscribe_owner(msg)
                return n           
            #Call to introduce some functionality in each forwarder ;) 
            if n != None:  
                n.forward(msg)
        
        n.successor().subscribe_owner(msg)
        return n.successor()
    
    def forward(self, msg):   #Subscribe
            
        if ((msg.id in self.routing_topic_nodes.keys()) and (msg.source not in self.routing_topic_nodes.get(msg.id))):
            self.routing_topic_nodes.get(msg.id).append(msg.source)
        else:
            self.routing_topic_nodes[msg.id] = [msg.source]
        print 'Forward: Source id: ' + str(msg.source.get_id()) + ' --> Node id: ' + str(self.id) + ' (Msg id: ' + str(msg.id) + ')'
        

        #Change message information for next node.
        msg.source.set_parent(self.proxy)
        msg.source = self.proxy               
            

    def subscribe_owner(self, msg): #Subscribe

        if ((msg.id in self.routing_topic_nodes.keys()) and (msg.source not in self.routing_topic_nodes.get(msg.id))):     #Si ya tengo ese id, hago append()
            self.routing_topic_nodes.get(msg.id).append(msg.source)
        else:
            self.routing_topic_nodes[msg.id] = [msg.source]
            
        msg.first_node.set_my_topics(msg.id, self.id)                        
        print 'Deliver: Source id: ' + str(msg.source.get_id()) + ' --> Node id: ' + str(self.id) + ' (Msg id: ' + str(msg.id) + ')'
        msg.source.set_parent(self.proxy)
    
    def publish(self, msg):            
            
        if (msg.id in self.my_topics.keys()):
            print 'Node ' + str(self.id) + ' receives the message ' + str(msg.text_message)
            
        if (msg.id in self.routing_topic_nodes.keys()):
            for node in self.routing_topic_nodes.get(msg.id):
                node.publish(msg)
    def unsubscribe(self, msg):             #Unsubscribe
            
        if ((msg.id not in self.my_topics.keys()) or (msg.first_node.get_id() == self.id)):
            if ((msg.id in self.parent_node.get_routing_topic_nodes().keys()) and 
                (msg.source in self.parent_node.get_routing_topic_nodes().get(msg.id))):
                
                #Clear my node from path of my father
                self.parent_node.remove_son(msg.id, msg.source)
                print 'Deliver: Source id: ' + str(msg.source.get_id()) + ' --> Node id: ' + str(self.parent_node.get_id()) + ' (Msg id: ' + str(msg.id) + ')'
        
                if (len(self.parent_node.get_routing_topic_nodes().get(msg.id)) == 0):
                    if (self.parent_node.get_id() != msg.first_node.get_my_topics(msg.id)[0]):
                        msg.source = self.parent_node  
                        self.parent_node.unsubscribe(msg)
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
            src.fail_stop_find_successor(ScribeMessage(key,src,-1,''))
                
        elif (op==2):   #Unsubscribe a topic
            nod = int(raw_input("Choose a node: "))
            src = nodes_h[nod]
            top = raw_input("Topic's name to unsubscribe: ")
            key = hash(top)%num_nodes 
            src.unsubscribe(ScribeMessage(key,src,-1,''))
            
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
                node_responsible.publish(ScribeMessage(key,src,-1, msg)) 
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
        nodes_h[i] = host.spawn_id(str(cont), 'our_scribe', 'ScribeNode', [])
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
#    tcpconf = ('tcp', ('127.0.0.1', 6377))
#    host = init_host(tcpconf)
    momconf = ('mom',{'name':'c1','ip':'127.0.0.1','port':61613,'namespace':'/topic/test'})
    host = init_host(momconf)
    for i in range(num_nodes):
        nodes_h[i] = host.spawn_id(str(cont), 'scribe', 'ScribeNode', [])
        cont += 1
    for i in range(num_nodes):    
        nodes_h[i].init_node()
    remote_aref = 'mom://s1/scribe/ScribeNode/1'   
#    remote_aref = 'atom://127.0.0.1:1432/chord/Node/2'
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
    
def main():
    start_controller('pyactive_thread')
    serve_forever(start_node)
if __name__ == "__main__":
    main() 
