'''
Created on 13/02/2014

@author: Edgar Zamora Gomez
'''

import collections
from pyactive.Multi import SMulti, AMulti
ProposalID = collections.namedtuple('ProposalID', ['number', 'uid'])

class Proposer (object):
    _sync = {}
    _async = ['set_multi', 'prepare', 'promise', 'set_proposal']
    _ref = ['set_multi']
    _parallel = []
    

    def __init__(self,  quorum_size):
        self.quorum_size = quorum_size
        self.proposed_value       = {}
        self.last_accepted_id     = {}
        self.next_proposal_number = {}
        self.promises_rcvd = {}
        self.proposal_id = {}
        self.index = 0
        self.highestInstance = 0
    #async, ref
    def set_multi(self, list_acceptors):
        print 'holaa capullo'
        self.list_acceptors = list_acceptors
        self.amulti = AMulti(self.list_acceptors)
        print self.amulti
        
    def set_proposal(self, value, index = None):
        '''
        Sets the proposal value for this node if this node is not already aware of
        another proposal having already been accepted. 
        '''
        if index == None:
            self.highestInstance += 1
            self.index = self.highestInstance
            self.proposed_value[self.index] = value
            self.next_proposal_number[self.index] = 1
        else:
            if self.proposed_value.has_key(index):
                return False
            else:
                self.proposed_value[index] = value
                self.next_proposal_number[index] = 1
                if index < self.highestInstance:
                    self.highestInstance = index
        self.prepare()


    def prepare(self):
        '''
        Sends a prepare request to all Acceptors as the first step in attempting to
        acquire leadership of the Paxos instance. 
        '''
        self.promises_rcvd[self.index] = set()
        self.proposal_id[self.index]   = ProposalID(self.next_proposal_number, self.id)
        self.next_proposal_number[self.index] += 1
        #multi to all acceptors!! 
        self.amulti.onPrepare(self.proxy, self.index,  self.proposal_id[self.index])

    
    def promise(self, from_uid, proposal_id, index, prev_accepted_id, prev_accepted_value):
        '''
        Called when a Promise message is received from an Acceptor
        '''

        # Ignore the message if it's for an old proposal or we have already received
        # a response from this Acceptor
        if proposal_id != self.proposal_id[index] or from_uid in self.promises_rcvd[index]:
            return None

        self.promises_rcvd[index].add( from_uid )
        if not self.last_accepted_id.has_key(index):
            self.last_accepted_id[index] = 1
        if prev_accepted_id > self.last_accepted_id[index]:
            self.last_accepted_id[index] = prev_accepted_id
            # If the Acceptor has already accepted a value, we MUST set our proposal
            # to that value.
            if prev_accepted_value is not None:
                self.proposed_value[index] = prev_accepted_value

        if len(self.promises_rcvd[index]) > self.quorum_size/2:    
            if self.proposed_value[index] is not None:
                self.amulti.accept(self.id, index, self.proposal_id[index], self.proposed_value[index])
                
class Acceptor (object):
    _sync = {}
    _async = ['set_multi', 'onPrepare', 'accept']
    _ref = ['set_multi', 'onPrepare']
    _parallel = []
    
    def __init__(self, quorum_size):
        self.accepted_id = {}
        self.quorum_size = quorum_size
        self.accepted_value = {}
        self.promised_id = {}
        
    def set_multi(self, learners): 
        self.learners = learners
        self.amulti = AMulti(self.learners)
        
    def onPrepare(self, proposer, index, proposal_id):
        '''
        Called when a Prepare message is received from a Proposer
        '''
        if not self.accepted_id.has_key(index):
            self.accepted_id[index] = None
            self.accepted_value[index] = None
        try:
            if proposal_id == self.promised_id[index]:
                # Duplicate prepare message
                proposer.promise(self.id, proposal_id, index, self.accepted_id[index], self.accepted_value[index])
            elif proposal_id > self.promised_id[index]:
                self.promised_id[index] = proposal_id
                proposer.promise(self.id, proposal_id, index, self.accepted_id[index], self.accepted_value[index])
        except:
            self.promised_id[index] = proposal_id
            proposer.promise(self.id, proposal_id, index, self.accepted_id[index], self.accepted_value[index])

            
        
                    
    def accept(self, from_uid, index, proposal_id, value):
        '''
        Called when an Accept! message is received from a Proposer
        '''
        if proposal_id >= self.promised_id[index]:
            self.promised_id[index]     = proposal_id
            self.accepted_id[index]     = proposal_id
            self.accepted_value[index]  = value
            '''send accepted to all learners!! '''
            self.amulti.accepted(self.id, proposal_id, index,self.accepted_value[index])
        
class Learner (object):
    _sync = {'get':'2'}
    _async = ['accepted']
    _ref = []
    _parallel = []
    proposals         = None # maps proposal_id => [accept_count, retain_count, value]
    acceptors         = None # maps from_uid => last_accepted_proposal_id
    final_value       = None
    final_proposal_id = None
    def __init__(self, quorum_size):
        self.quorum_size = quorum_size        
        self.accepted_value = {}
        self.accepted_proposal = {}
        self.accepted_rcvd = {}
    @property
    def complete(self):
        return self.final_proposal_id is not None

    def get(self):
        return self.accpeted_value
    
    def accepted(self, from_uid, proposal_id, index, accepted_value):
        
        self.accepted_rcvd.add
        if proposal_id > self.min_proposal:
            self.max_round = proposal_id
            self.prepared = False
#             self.prepare()
        if len(self.accepted_rcvd) > self.quorum_size/2:    
            self.accepted_proposal[self.index] = 0
            self.accepted_value[self.index] = self.proposed_value[self.index]
            print self.accepted_value

