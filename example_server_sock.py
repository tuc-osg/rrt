from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from twisted.python import log
from tempfile import mktemp
import os,sys
import rtest

# enable logging for Twisted and our code
from twisted.python import log
log.startLogging(sys.stdout)
import logging
logging.getLogger().setLevel(logging.DEBUG)

endpoint = TCP4ServerEndpoint(reactor, 8001)
endpoint.listen(rtest.RemoteTestProtocolFactory())
reactor.run()
