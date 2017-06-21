import unittest
import os,sys
import rtest

# enable logging for Twisted and our code
from twisted.python import log
log.startLogging(sys.stdout)
import logging
logging.getLogger().setLevel(logging.DEBUG)

# configure remote testing facility
os.environ[rtest.ENV_VAR_NAME]="tcp:localhost:8001"

# normal test cases, just the base class is different
class DummyTestCase(unittest.TestCase):
	def test_working(self):
		self.assertTrue(True)

	def test_long(self):
		for i in range(10000000):
			pass

if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(DummyTestCase)
	rtest.TestRunner().run(suite)
