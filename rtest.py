import unittest
import logging
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ClientFactory
from twisted.internet.serialport import SerialPort
from twisted.internet.endpoints import UNIXClientEndpoint
from twisted.internet.error import ConnectionDone
from twisted.internet import reactor, task, defer
import os

# The name of the environment variable configuring the mode of operation
ENV_VAR_NAME="RTEST_CHANNEL"

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
                logging.info("Got preamble, sending tests")
                task_list=[task.deferLater(reactor, 0, self.sendTest, test) for test in self.suite]
                d=defer.gatherResults(task_list)
                d.addCallback(self.all_tests_send)

    def sendTest(self, test):
        self.sendLine(str(test))

    def all_tests_send(self, arg):
        logging.info("All tests send")
        self.transport.loseConnection()


class RemoteTestServerProtocol(LineReceiver):
    def __init__(self, suite=None):
        self.suite = suite
        self.state = "INIT"

    def connectionLost(self, reason):
        logging.info("Client disconnected.")

    def connectionMade(self):
        self.state = "CONNECTED"
        logging.info("Connection established, sending preamble to server")

    def lineReceived(self, line):
        if self.state == "CONNECTED":
            # expect protocol preamble
            if line==PREAMBLE:
                self.state = "SERVER_READY"
                logging.info("Got preamble, answering with my preamble")
                self.sendLine(PREAMBLE)
        elif self.state == "SERVER_READY":
            logging.info("Got test data: "+line)

class RemoteTestProtocolFactory(ClientFactory):
    def __init__(self, suite=None):
        if suite:
            self.protocol=RemoteTestClientProtocol(suite) # test case sender / client
        else:
            self.protocol=RemoteTestServerProtocol()      # test case receiver / server

    def buildProtocol(self, addr):
        return self.protocol

class TestRunner():
    def run(self, suite):

        factory=RemoteTestProtocolFactory(suite)

        channel=os.environ[ENV_VAR_NAME]
        # Determine mode of operation for remote testing
#        if channel.startswith("serial:"):
#            serial_device=channel[7:]
#            self.transport=SerialPort(RemoteTestProtocol(), serial_device, reactor)
#            logging.info("Connecting via {0} ...".format(serial_device))

        if channel.startswith("tcp:"):
            prefix, host, port=channel.split(':')
            port=int(port)
            logging.info("Connecting via {0}:{1} ...".format(host,port))
            reactor.connectTCP(host, port, factory)

        # start event loop
        reactor.run()
