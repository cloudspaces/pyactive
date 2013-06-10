# PyActive 


## Description 


PyActive is a novel object oriented implementation of the Actor model in Python. 
What it is novel in our approach is the tight integration with OO concepts that 
considerably simplifies the use of this library. 

In particular, PyActive provides non-blocking synchronous invocations in Actors. Unlike 
traditional Actor frameworks that only provide asynchronous calls, our library offers 
synchronous non-blocking calls that respect and maintain the message-passing concurrency model.
To this end, we have implemented a variant of the Active Object pattern using both Threads and 
micro-Threads (Stackless). We demonstrate in complex examples like the Chord overlay that our approach 
reduces substantially the complexity and Lines of Code (LoC) of the problem.

PyActive follows a pure object oriented approach for method invocation. 
Other actor frameworks use special notations (!) for sending messages 
and pattern matching or conditionals to receive them. Instead of that, Pyactive
middleware transparently maps messages to methods and thus achieving better 
code expressiveness.

PyActive also includes advanced abstractions like remote reference passing, one-to-many invocation abstractions,  and
exception handling to ease the implementation of distributed algorithms.  PyActive is also a distributed object middleware 
and it offers remote dispatchers enabling remote method invocation. Finally, PyActive's log mechanisms can generate UML sequence diagrams
that help to understand the  interactions among Actors using a OO aproach.

PyActive is now provided in two platforms: using cooperative microthreads on top of Stackless Python and on top of python threads
using the standard threading library.  We validated the performance and expressiveness of Pyactive to code distributed algorithms.



## Basic method abstractions


* **async**: It’s used to indicate the method can receive asynchronous remote calls.

* **sync**: It’s used to indicate the method can receive synchronous remote calls.
  So it’s necessary to return something.

* **parallel**: It guarantees that the current method will not be blocked in a synchronous call by launching an additional thread of control. Our library ensures that no concurrency conflicts arise by ensuring that only one thread at a time can access the Passive Object.

* **ref**: It’s used to activate the remote reference layer in this method. This means that one parameter or result are Actors. So this annotation guarantees pass-by-reference.


## Basic Functions 

* **start_controller**: It's used to choose the module. At this moment, we can choose 
  between 'atom_thread' and 'tasklet'. Note that this decision can change the 
  python version that you need. For example the 'tasklet' module needs Stackless Python. 
  
* **launch**: It's used to throw the main function which initializates the program. Once this function ends, the program will die.

* **serve_forever**. It’s used like launch function but once the function ends, the program continues.


## What do you need to run PyActive? 


In this section we explain all you need to use this middleware. It's easy!

Into Pyactive_Project folder you can find how to install the middleware in INSTALL.txt.

**Requirements**
* If you only use the threads module, you only need Python 2.7

* If you need use the stackless version, you need Python 2.7 with 
  Stackless Python

You can download Python in: http://www.python.org/download/ 

Once you have installed python, the next step is to install Stackless python.
You can download Stackless python at: [http://www.stackless.com/]


PyActive contains some examples and tests. You can run the following tests:

        $> cd/pyactive
        $> python ./examples/Hello_World/test_async.py
        $> python ./examples/registry/first.py

Choose the module using the function: 'start_controller'.  Nowadays, 
you can put either the parameter 'tasklet' or 'atom_thread' to choose the module.
Note that you choose the tasklet module, you need the Stacklees Python. 

## Hello_world example

In this section you can see a simple Hello World synchronous and asynchronous. Into Pyactive_Project you can find more complex examples into Examples folder.

**Hello_World Synchronous**

        from pyactive.controller import init_host, launch,start_controller, sleep
        class Server():
        	#@sync(1)
        	def hello_world(self):
        		return 'hello world'
        
        def test():
        	host = init_host()
        	
        	# parameters 1 = 'id', 'test_sync' = module name, 'Server' = class name
        	n1 = host.spawn_id('1', 'test_sync', 'Server', [])
        	
        	response = n1.hello_world()
        	print response
        
        if __name__ == '__main__':
        	#you can change the parameter 'tasklet' to 'pyactive_thread' if you like thread controller.
        	start_controller('tasklet')
			
**Hello_World Asynchronous**

        from pyactive.controller import init_host, launch,start_controller, sleep
        class Server():
        	#@async
        	def hello_world(self):
        		print 'hello world'
        
        def test():
        	host = init_host()
        	
        	# parameters 1 = 'id', 'test_async' = module name, 'Server' = class name
        	n1 = host.spawn_id('1', 'test_async', 'Server', [])
        	
        	n1.hello_world()
        
        if __name__ == '__main__':
        	#you can change the parameter 'tasklet' to 'pyactive_thread' if you like thread controller.
        	start_controller('tasklet')




