#@author Marc Sanchez Artigas

class HopCounter(object):
    "Decorator that keeps track of the number of hops"
    __numHops      = 0
    __counting     = False
    __tracking     = False
    __route        = {}
    __routeId      = None

    def __init__(self, func):
        "Saves the method to intercept."
        self.__func = func
    
    def __call__(self, obj, *args, **kwargs):
        "Invokes the method"
        result = self.__func(obj,*args, **kwargs)
        if HopCounter.__counting:
            HopCounter.incCounter()
            if HopCounter.__tracking:
                if HopCounter.__routeId is None:
                    raise IndexError('A route must be defined beforehand')
                HopCounter.appendHop(result)
        return result
    
    @staticmethod
    def enableTracking(tracking = True):
        HopCounter.__tracking = tracking
    
    @staticmethod
    def enable(counting = True):
        "Sets the flag 'counting' to the specified value (default to True). It permits to count nodes."
        HopCounter.__counting = counting

    @staticmethod
    def incCounter():
        "Increment by one the total number of afected nodes."
        print 'holaaaa increment'
        HopCounter.__numHops += 1
   
    @staticmethod
    def decCounter():
        "Increment by one the total number of afected nodes."
        HopCounter.__numHops = HopCounter.__numHops - 1

    @staticmethod
    def setRoute(source, target):
        "Appends the route from source to target"
        if source is None:
            raise ValueError('source is None')
        if target is None:
            raise ValueError('target is None')
        HopCounter.__routeId = '%(source)d-%(target)d' % {'source': source, 'target': target}
        HopCounter.__route[HopCounter.__routeId] = [source]
    
    @staticmethod
    def appendHop(hop):
        "Appends a hop to the local route as stated in __routeID"
        if hop is None:
            raise ValueError('hop is None')
        HopCounter.__route[HopCounter.__routeId].append(hop)
        
    @staticmethod
    def getRoute(source, target):
        if source is None:
            raise ValueError('source is None')
        if target is None:
            raise ValueError('target is None')
        return HopCounter.__route['%(source)d-%(target)d' % {'source': source, 'target': target}]
    
    @staticmethod
    def getHopCounter():
        "Gets the total number of afected nodes."
        return HopCounter.__numHops

    @staticmethod
    def getMeanHops(numQueries):
        "Returns the mean of afected nodes, i.e. #nodes / #msgs"
        result = float(HopCounter.__numHops) / float(numQueries)
        HopCounter.resetCounter()
        return result
    
    @staticmethod
    def resetCounter():
        "Sets to zero the number of afected nodes."
        HopCounter.__numHops = 0
        print 'RESEEEEEEEET!!!!', HopCounter.__numHops
    
    @staticmethod
    def resetRoutes():
        "Resets the route map"
        HopCounter.__route.clear()
        HopCounter.__routeId = None


"""Wrap-around function for method invocation: for supporting 'self' object reference
as an argument"""
def CountingHops(CLname):
    """
     Define this function stores the class name.
     <CLname>: class name of the intercepted method
     <PInfo>: path information from source to target
    """
    def decorator(func):
        "decorator function."
        # signature's name for the interception method
        name = '_%s_%s_countingHops' % (CLname, func.__name__)
        print name
        
        def CountingInvokations(obj, *args, **kwargs):
            "Adds the decorator functionality for the method to invoke."
            try:
                "try to get the counter."
                gen = getattr(obj, name)
            except AttributeError:
                """ when there's not exist this method within the local instance,
                build a new counter up for the incoming method."""
                gen = HopCounter(func)
                setattr(obj, name, gen)
            "call the counter and return its result."
            return gen(obj, *args, **kwargs)
        return CountingInvokations
    return decorator

""" how to use them?

@aop.CountingHops("Node")
def f(self, *args, **kwargs):
    ......
   
HopCounter.setCounting()
 ... your test...
results = [HopCounter.getHopCounter(), HopCounter.getMeanHops(100)]
HopCounter.setCounting(False)
"""
