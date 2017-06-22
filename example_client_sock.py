import unittest
import os,sys
import rtest

# enable logging for Twisted and our code
# you can comment that out
from twisted.python import log
log.startLogging(sys.stdout)
import logging
logging.getLogger().setLevel(logging.DEBUG)

# There are only differences to ordinary Python tests:
# - The base class
# - The usage of 'self.remote()'
class DemoTestCase(rtest.RemoteTestCase):
	def test_calc_remote(self):
		self.assertEquals(self.remote('1+1'),'2')

	def test_calc_local(self):
		self.assertEquals(str(eval('1+1')),'2')

# Mandatory: Set the connection method before the TestCase is instantiated
setattr(DemoTestCase,"channel","tcp:localhost:8001")

if __name__ == '__main__':
	unittest.main()
