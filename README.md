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


## how to use PyActive? 


In this section we explain all you need to use this middleware. It's easy!

**Requirements**
* If you only use the threads module, you only need Python 2.7

* If you need use the stackless version, you need Python 2.7 with 
  Stackless Python

You can download Python in: http://www.python.org/download/ 

Once you have installed python, the next step is to install Stackless python.
You can download Stackless python at: [http://www.stackless.com/]

Atom contains some examples and tests. You can run the following tests:

        $> cd/atom
        $> python ./test/Hello_World/test_async.py
        $> python ./test/registry/first.py

Choose the module using the function: 'start_controller'.  Nowadays, 
you can put either the parameter 'tasklet' or 'atom_thread' to choose the module.
Note that you choose the tasklet module, you need the Stacklees Python. 


## Perspectives uses and future work 


* **Simulation and implementation of distributed algorithms**: Pyactive can 
  considerably simplify the development of distributed algorithms. It is 
  possible to simulate algorithms in a single machine before they are 
  deployed in an experimentation testbed. We implemented Chord in the past 
  for an event-based traditional p2p simulator (PlanetSim) and the code is 
  complex to understand and follow. On the other hand, our implementation 
  using Pyactive is more succinct, and quit similar to the original algorithms 
  proposed in the Chord paper. The main reason is that Pyactive clearly separates 
  communication code from algorithm code inside methods. We plan to use Pyactive 
  in our distributed systems course and in our peer-to-peer and networking courses.

* **Web middleware**: Pyactive has a big potential to ease the development of REST 
  and Web RPC platforms. Web asynchronous networking libraries that use green 
  threads. We are even considering to create a novel version of Pyactive on top of
  one these libraries. In particular, we plan to rewrite some server code of the
  OpenStack Swift is based on WSGI python servers that already use green threads
  to improve the performance. But the current code is tangling communication, 
  marshalling and distributed storage algorithms. Pyactive can decouple these layers
  and make the code performance and easy to understand ans modify

* **Multi-core programming**: One of the promises of message passing concurrency 
  is the future of multi-core concurrency programming. Erlang offers truly 
  parallelism over different cores with Symmetric Multi-Processing(SMP). They mainly 
  added multi-threading support to the Erlang VM, so that different lightweight 
  process schedulers can live inside their native threads. In our case, stackless 
  also permits to have different microthreads living inside their own thread or 
  process. But python threads do not benefit from multi-core programming due to 
  the GIL (Global Interpreter lock). Instead of that, we could support multi-core 
  programming using the python multiprocessing library.

* **Distributed continuations**: We outline an important future work with the 
  combination of RPCs and distributed continuations in Pyactive. Stackless python 
  permits to serialize microthreads in their current frames. It is thus feasible
  to create novel call abstractions supporting distributed continuations between
  different hosts.
