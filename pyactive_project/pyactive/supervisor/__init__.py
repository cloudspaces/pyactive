'''Failure Detect using Supervisor!'''
from pyactive.Multi import SMulti
from pyactive.controller import interval, new_supervisor


class Supervisor():
    def __init__(self, time, retries, owner, actors=[]):
        self.owner = owner
        self.s_actor = new_supervisor(self.owner.aref)
        self.actors = {}
        self.retries = {}
        self.max_retries = retries

        self.multiActors = SMulti(self.s_actor, actors)
        self.add_actors(actors)
        interval(time, self.ask_actors)
        # timer to indicate the frequency to ask to actors

    def add_actor(self, actor):
        self.actors[actor.get_aref()] = actor
        self.retries[actor.get_aref()] = 0
        self.multiActors.attach(actor)

    def add_actors(self, actors):
        for actor in actors:
            self.add_actor(actor)

    def ask_actors(self):
        try:
            result = self.multiActors.keep_alive()
            for k in result.keys():
                self.retries[k] = 0
        except:
            for key in self.actors.keys():
                self.retries[key] += 1
                if self.retries[key] > self.max_retries:
                    self.owner.failure_detect(self.actors[key])
                    self.retries[key] = 0
        else:
            if len(result.keys()) != len(self.actors.keys()):
                fault_list_keys = result.keys() - self.actors.keys()
                for key in fault_list_keys:
                    self.retries[key] += 1
                    if (self.retries[key] > self.max_retries):
                        self.owner.failure_detect(self.actors[key])
                        self.retries[key] = 0
