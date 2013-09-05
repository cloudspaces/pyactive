"""
This provides basic connectivity to a message broker supporting the 'stomp' protocol.
At the moment ACK, SEND, SUBSCRIBE, UNSUBSCRIBE, BEGIN, ABORT, COMMIT, CONNECT and DISCONNECT operations
are supported.

See the project page for more information.

Meta-Data
---------
Author: Jason R Briggs
License: http://www.apache.org/licenses/LICENSE-2.0
Start Date: 2005/12/01
Last Revision Date: 2011/09/17
Project Page: http://www.briggs.net.nz/log/projects/stomp.py

Notes/Attribution
-----------------
 * patch from Andreas Schobel
 * patches from Julian Scheid of Rising Sun Pictures (http://open.rsp.com.au)
 * patch from Fernando
 * patches from Eugene Strulyov
 * patch for SSL protocol from 'jmgdaniec'
"""

import os
import sys
sys.path.insert(0, os.path.split(__file__)[0])

import connect, listener, exception

__version__ = __version__ = (3, 0, 5)
Connection = connect.Connection
ConnectionListener = listener.ConnectionListener
StatsListener = listener.StatsListener
