"""
Author: Edgar Zamora Gomez  <edgar.zamora@urv.cat>
"""

class AtomError(Exception):
    def __init__(self, e=None):
        self.e = e
    
    def __str__(self):
        return self.e.__str__()


class TimeoutError(AtomError):
    def __str__(self):
        return 'The timeout has expired'
    
class NotFoundDispatcher(AtomError):
    def __str__(self):
        return 'Not found dispatcher, it is possible this dispatcher not work with this actor'

class NotExistsMethod(AtomError):
    def __str__(self):
        return 'This method not exists'
    
class MethodNotFoundError(AtomError):
    def __str__(self):
        return 'The method was not found'
    
class MethodError(AtomError):
    def __str__(self):
        return 'Incorrect parameters'