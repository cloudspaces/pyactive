"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""

class PyactiveError(Exception):
    def __init__(self, e=None):
        self.e = e

    def __str__(self):
        return self.e.__str__()


class TimeoutError(PyactiveError):
    def __str__(self):
        return 'The timeout has expired'

class NotFoundDispatcher(PyactiveError):
    def __str__(self):
        return 'Not found dispatcher, it is possible this dispatcher not work with this actor'

class NotExistsMethod(PyactiveError):
    def __str__(self):
        return 'This method not exists'

class MethodNotFoundError(PyactiveError):
    def __str__(self):
        return 'The method was not found'

class MethodError(PyactiveError):
    def __init__(self, actor_name=None, e=None):
        super(self.__class__, self).__init__(e)
        self.actor_name = actor_name
    def __str__(self):
        if self.actor_name:
            return "%s, ERROR: %s" % (self.actor_name, self.e.__str__())
        return "ERROR: %s" % self.e.__str__()

class SyncMethodError(PyactiveError):
    def __init__(self, actor_name=None, e=None):
        super(self.__class__, self).__init__(e)
        self.actor_name = actor_name
    def __str__(self):
        if self.actor_name:
            return "A sync method needs a timeout value. Note that the _sync \
variable must be a dictionary. Review the class: %s" % self.actor_name
        return "A sync method needs a timeout value. Note that the _sync \
variable must be a dictionary"


class NotImplementedMethod(PyactiveError):

    def __str__(self):
        return 'Please implement this method'

class ActorNotFound(PyactiveError):
    def __init__(self, actor_reference=None, e=None):
        super(self.__class__, self).__init__(e)
        self.actor_reference = actor_reference
    def __str__(self):
        if self.actor_reference:
            return 'NOT FOUND: Any actor with the reference: %s' % self.actor_reference
        return 'NOT FOUND: Any actor with this reference'

class DuplicatedActor(PyactiveError):
    def __str__(self):
        return 'Duplicated: Already exists an Actor with the same ID'
