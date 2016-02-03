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
    def __init__(self, method_name=None, e=None):
        PyactiveError.__init__(self)
        self.method_name = method_name
    def __str__(self):
        if self.method_name:
            return "Incorrect Parameters in method: %s" % self.method_name
        return 'Incorrect parameters'

class SyncMethodError(PyactiveError):
    def __init__(self, actor_name=None, e=None):
        PyactiveError.__init__(self)
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

class DuplicatedActor(PyactiveError):
    def __str__(self):
        return 'Duplicated: Already exists an Actor with the same ID'
