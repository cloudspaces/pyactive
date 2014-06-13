'''
Created on 13/01/2014

@author: edgar
'''
import collections
from pyactive.Multi import SMulti, AMulti
from pyactive.controller import interval


ProposalID = collections.namedtuple('ProposalID', ['number', 'uid'])

class Server(object):
    _sync = {'is_alive':'1', 'prepare':'2', 'get_accepted_values':'2'}
    _async = ['set_multi', 'set_interval','promise', 'set_proposal', 'onPrepare',
               'accepted', 'accept', 'set_leader', 'heartbeat' ]
    _ref = ['set_multi', 'onPrepare', 'accept', 'accepted', 'set_proposal']
    _parallel = ['heartbeat']
    
    def __init__(self,  quorum_size):
        self.quorum_size = quorum_size
        self.retries = 0
        self.last_log_index = None
        self.min_proposal = None   
        self.first_unchosen_index = 0
        self.accepted_value = {}
        self.accepted_proposal = {}
        self.index = 0
        self.max_round = 0
        self.leader = False
        self.highestInstance = 0
        self.prepared = False
        self.next_index = self.index + 1
        self.leader_proxy = None
        self.proposed_value       = {}
        self.last_accepted_id     = {}
        self.next_proposal_number = 1 # [1]*self.max_round
        self.num_noMoreAccepted = {}
        self.accepted_rcvd = set()
        self.server_dict = {}
        
    def set_leader(self):
        self.leader = True  
    def set_server_dict(self):
        '''Dict <key, value> --> <server_id, server_reference>'''
        for acceptor in self.list_acceptors:
            self.server_dict[acceptor.get_id()] = acceptor    
    def set_multi(self, list_acceptors):
        self.list_acceptors = list_acceptors
        self.set_server_dict()
        self.amulti = AMulti(self.list_acceptors)
        self.smulti = SMulti(self.list_acceptors, self.proxy)
    def get_accepted_values(self):
        return self.accepted_value.values()
    
    '''Leader Election'''
    def heartbeat(self):
        change_leader = True
        list_ids = self.smulti.is_alive() 
        max_id = max(list_ids.values())  
        if max_id > self.id:
            change_leader = False
            self.leader_proxy = self.server_dict[max_id]
        
        if change_leader:
            self.retries +=1
        else:
            self.retries = 0
            
        if self.retries >= 2:
            self.leader = True
            
    def is_alive(self):
        return self.id
    
    def set_proposal(self, value, client):
        '''
        Sets the proposal value for this node if this node is not the leader, it redirect the value 
        to actual leader.
        '''
        self.current_client = client
        if not self.leader:
            if not self.leader_proxy:
                return False
            return self.leader_proxy.set_proposal(value, client)
            
        else:
            self.index = self.highestInstance
            self.proposed_value[self.index]= value
            self.highestInstance += 1
            self.last_accepted_id[self.index] = 0
            self.num_noMoreAccepted[self.index] = 0
            self.prepare()
            
    '''
    Acceptor
    '''
    def onPrepare(self, proposer, n, index):
        '''
        Called when a Prepare message is received from a Proposer
        '''
       
        if n >= self.min_proposal:
            # Duplicate prepare message
            self.min_proposal = n
            try:
                proposer.promise(self.id, self.accepted_proposal[index], self.accepted_value[index], True)
            except:
                proposer.promise(self.id, None, None, True)


    def accept(self, proxy, index, n, v, first_unchosen_index):
        '''
        Called when an Accept! message is received from a Proposer
        '''
        if n >= self.min_proposal:
            self.accepted_proposal[index] = n
            self.min_proposal = n
            self.accepted_value[index]  = v
            '''send accepted to all learners!! '''
#             self.amulti.accepted(self.id, proposal_id, self.accepted_value)
        for i in range(1, first_unchosen_index-1):
            if self.accepted_proposal[i] == n:
                self.accepted_proposal[i] = 0
        
        '''revisar returns'''    
#         print proxy, proxy.get_id()
        proxy.accepted(self.proxy, self.min_proposal, self.first_unchosen_index)
#         '''send accepted to all learners!! '''
#         self.amulti.accepted(self.id, proposal_id, self.accepted_value)
    
    def success(self, index, v):
        self.accepted_value[index] = v
        self.accepted_proposal[index] = 0

        '''revisar returns'''    
        return self.firstUnchosenIndex
    
    '''
    Proposer
    '''
    def prepare(self):
        '''
        Sends a prepare request to all Acceptors as the first step in attempting to
        acquire leadership of the Paxos instance. 
        '''
        if self.prepared:
            try:
                self.accepted_rcvd = set()
                self.amulti.accept(self.proxy, self.index, self.min_proposal, self.proposed_value[self.index], self.first_unchosen_index)
            except:
                return False
        else:            
            self.promises_rcvd = set()
            self.min_proposal = ProposalID(self.next_proposal_number, self.id)
            self.next_proposal_number += 1      
        
        #multi to all acceptors!! 
            self.amulti.onPrepare(self.proxy, self.min_proposal, self.index)
        
        return True
    
    def promise(self, from_uid, accepted_proposal, accepted_value, noMoreAccepted):
        #if accepted_proposal
        #si el maxim accepted_proposal != 0
        '''
        Called when a Promise message is received from an Acceptor
        '''

        # Ignore the message if it's for an old proposal or we have already received
        # a response from this Acceptor
        #if accepted_proposal != self.accepted_proposal[self.index] or from_uid in self.promises_rcvd:
        #    return None
        self.promises_rcvd.add( from_uid )
        
        #si el maxim accepted_proposal != 0
        print 'last_accepted_id', self.last_accepted_id, 'index', self.index
        if accepted_proposal > self.last_accepted_id[self.index]:
            self.last_accepted_id[self.index] = accepted_proposal
            # If the Acceptor has already accepted a value, we MUST set our proposal
            # to that value.
            if accepted_value is not None:
                self.proposed_value[self.index] = accepted_value
                
        if noMoreAccepted:
            self.num_noMoreAccepted[self.index] += 1
                              
        if len(self.promises_rcvd) > self.quorum_size/2:
            
            if self.num_noMoreAccepted[self.index] > self.quorum_size/2:
                self.prepared = True  
                
            if self.proposed_value[self.index] is not None:
                self.accepted_rcvd = set()
                self.amulti.accept(self.proxy, self.index, self.min_proposal, self.proposed_value[self.index], self.first_unchosen_index)
                self.promises_rcvd = set()
                
                
    def accepted(self, proxy, n, first_unchosen_index):   
        self.accepted_rcvd.add( proxy.get_id())
        if n > self.min_proposal:
            self.max_round = n
            self.prepared = False
#             self.prepare()
        if first_unchosen_index <= self.last_log_index and self.accepted_proposal[first_unchosen_index] == 0:
            result = proxy.success(first_unchosen_index, self.accepted_value[first_unchosen_index])
            self.index = result
            while True:
                if (result < self.first_unchosen_index):
                    result = proxy.success(result, self.accepted_value[result])
                    self.index = result
                else:
                    break
        if len(self.accepted_rcvd) > self.quorum_size/2:    
            self.accepted_proposal[self.index] = 0
            self.accepted_value[self.index] = self.proposed_value[self.index]
            self.current_client.internal_get(self.accepted_value[self.index])
            
#             if self.accepted_value[self.index] == self.proposed_value[self.index]:
#                 self.prepare()
        
#         if len(self.promises_rcvd) > self.quorum_size/2:
#             
#                
    
            
                    
    
    