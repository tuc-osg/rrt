from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Factory
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver
from twisted.python import log
import sys, os
import rtest

def eval_code(line):
    print("Got code: "+line)
    try:
    	output=str(eval(line))
    except Exception as e:
    	output=str(e)
    print("Test result: "+output)
    return output


class RemoteTestServerProtocol(LineReceiver):
    def __init__(self):
        self.state = "INIT"

    def connectionMade(self):
        self.state = "CONNECTED"

    def lineReceived(self, line):
        if self.state == "CONNECTED":
            # expect protocol preamble
            if line==rtest.PREAMBLE:
                self.state = "SERVER_READY"
                self.sendLine(rtest.PREAMBLE)
        elif self.state == "SERVER_READY":
            self.sendLine(eval_code(line))

class RemoteTestServerProtocolFactory(Factory):
    protocol = RemoteTestServerProtocol

endpoint = TCP4ServerEndpoint(reactor, 8001)
endpoint.listen(RemoteTestServerProtocolFactory())
reactor.run()
