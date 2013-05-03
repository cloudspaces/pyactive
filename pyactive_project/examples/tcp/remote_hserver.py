"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""
from pyactive.controller import init_host, serve_forever


tcpconf = ('tcp',('127.0.0.1',1232))
host = init_host(tcpconf)
serve_forever()