import unittest
import logging
from twisted.protocols.basic import LineReceiver
from twisted.internet.serialport import SerialPort
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor, task, defer, threads
from threading import Thread

# The protocol premable send to show who we are
PREAMBLE="RTESTPROTOCOL1.0_START"

class RemoteTestClientProtocol(LineReceiver):
    def __init__(self, suite=None):
        self.suite = suite
        self.state = "INIT"

    def connectionMade(self):
        self.state = "CONNECTED"
        logging.info("Connection established, sending preamble to server")
        self.sendLine(PREAMBLE)

    def connectionLost(self, reason):
        logging.info("Disconnected from server.")

    def lineReceived(self, line):
        if self.state == "CONNECTED":
            # expect protocol preamble
            if line==PREAMBLE:
                self.state = "CLIENT_READY"
                logging.info("Got preamble")
        elif self.state == "CLIENT_READY":
            logging.info("Got result")
            self.state = "CLIENT_GOT_RESULT"
            self.result = line

    def getResult(self):
        assert(self.state=="CLIENT_GOT_RESULT")
        self.state="CLIENT_READY"
        return self.result

class RemoteTestCase(unittest.TestCase):
    @classmethod
    def gotProtocol(cls,proto):
        ''' Callback when connection is established and protocol instance is available.'''
        logging.info("Protocol started")
        cls.protocol=proto

    @classmethod
    def setUpClass(cls):
        assert(cls.channel)     # set by client implementation

#        if channel.startswith("serial:"):
#            serial_device=channel[7:]
#            self.transport=SerialPort(RemoteTestProtocol(), serial_device, reactor)
#            logging.info("Connecting via {0} ...".format(serial_device))

        if cls.channel.startswith("tcp:"):
            prefix, host, port=cls.channel.split(':')
            port=int(port)
            logging.info("Connecting via {0}:{1} ...".format(host,port))
            cls.endpoint = TCP4ClientEndpoint(reactor, host, port)
            cls.protocol=None
            d=connectProtocol(cls.endpoint, RemoteTestClientProtocol())
            d.addCallback(cls.gotProtocol)

        # start blocking reactor with event loop in separate thread
        Thread(target=reactor.run, args=(False,)).start()        

    def remote(self,text):
        while not self.protocol:
            pass
        while not self.protocol.state=="CLIENT_READY":
            pass
        logging.info("Sending '{0}'".format(text))
        reactor.callFromThread(self.protocol.sendLine, text)
        while not self.protocol.state=="CLIENT_GOT_RESULT":
            pass
        return self.protocol.getResult()

    @classmethod
    def tearDownClass(cls):
         reactor.callFromThread(reactor.stop)
