"""
Author: Pedro Garcia Lopez <pedro.garcia@urv.cat>
"""
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import socket
import struct
import cPickle
import stackless
import stacklesssocket

from pyactive.constants import TARGET, SRC


PKT_CALL = 1
PKT_RESULT = 2
PKT_ERROR = 3


stacklesssocket.install()

# SEE HOSTNAME !!!


class Server:

    def __init__(self, host, port, listener):
        listenSocket = socket.socket(AF_INET, SOCK_STREAM)
        listenSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        listenSocket.bind((host, port))
        listenSocket.listen(5)
        print "SERVER: Listening"
        self.sockets = dict()
        self.endpoints = dict()
        self.socket = listenSocket
        self.listener = listener
        # self.endpointsByAddress = {}
        # self.namespaces = { "testSvc": TestService() }

        self.tasklet = stackless.tasklet(self.AcceptConnections)(listenSocket)

    def AcceptConnections(self, listenSocket):
        while True:
            self.AcceptEndpointConnection(listenSocket)

    def AcceptEndpointConnection(self, listenSocket):
        clientSocket, clientAddress = listenSocket.accept()
        print "SERVER: Accepted connection from", clientAddress
        print "SERVER: Client socket", id(clientSocket._sock)
        # self.endpointsByAddress[clientAddress] =
        EndPoint(self, clientSocket)
        # self.endpoints[clientAddress]=EndPoint(self, clientSocket)

    def send(self, msg):

        # Marshal the data to be sent, into a packet.
        addr = msg[TARGET]
        data = cPickle.dumps(msg)
        conn = None
        if addr in self.endpoints:
            end_point = self.endpoints[addr]
            conn = end_point.socket
        else:
            conn = socket.socket(AF_INET, SOCK_STREAM)
            (ip, port) = addr.split(':')
            conn.connect((ip, int(port)))

            # self.sockets[hostname] = conn
            self.endpoints[addr] = EndPoint(self, conn)
            # self.sockets[hostname]= EndPoint(self,conn)
            # conn
            # EndPoint(self,conn)
        # Packet size.
        conn.send(struct.pack("!I", len(data)))
        # Packet data.
        conn.send(data)

    def close(self):
        print "SERVER: Shutting down the server"
        self.tasklet.kill()
        self.socket.close()
        for endpoint in self.endpoints.values():
            endpoint.Release()


class EndPoint:

    packetSizeFmt = "!I"
    packetSizeLength = struct.calcsize(packetSizeFmt)

    def __init__(self, server, epSocket):
        """Stores and manages the socket to allow synchronous calls over it."""
        self.socket = epSocket
        # self.callID = 0
        # self.channelsByCallID = {}
        self.server = server
        self.init = False

        self.tasklet = stackless.tasklet(self._ManageSocket)()

    def Release(self):
        self.tasklet.kill()
        self.socket.close()

    def _ManageSocket(self):
        try:
            self._ReceivePackets()
        except socket.error:
            self.Release()
            # print e
            # Disconnection while blocking on a recv call.
            # return

    def _ReceivePackets(self):
        rawPacket = self._ReadIncomingPacket()
        while rawPacket:
            self._DispatchIncomingPacket(rawPacket)
            rawPacket = self._ReadIncomingPacket()

    def _ReadIncomingPacket(self):
        sizeData = self._ReadIncomingData(self.packetSizeLength)
        if sizeData:
            dataLength = struct.unpack(self.packetSizeFmt, sizeData)[0]
            return self._ReadIncomingData(dataLength)

    def _ReadIncomingData(self, dataLength):
        readBuffer = ""
        while len(readBuffer) != dataLength:
            data = self.socket.recv(dataLength - len(readBuffer))
            if not data:
                self.Release()
                # print self.__class__.__name__, "socket unexpectedly disconnected"
                # return
            readBuffer += data
        return readBuffer

    def _DispatchIncomingPacket(self, rawPacket):
        msg = cPickle.loads(rawPacket)
        if not self.init:
            self.server.endpoints[msg[SRC]] = self
            self.init = True
        # self.server.sockets[hostname] = self.socket
        # self.server.sockets[hostname] = self
        # self.socket
        # msg[HOSTNAME] = hostname
        self.server.listener.on_message(msg)

    def _SendPacket(self, packetType, callID, payload):
        # Marshal the data to be sent, into a packet.
        data = cPickle.dumps((packetType, callID, payload))
        # Packet size.
        self.socket.send(struct.pack("!I", len(data)))
        # Packet data.
        self.socket.send(data)

    def send(self, data):
        self.socket.send(struct.pack("!I", len(data)))
        # Packet data.
        self.socket.send(data)
