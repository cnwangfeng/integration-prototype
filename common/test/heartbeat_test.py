from multiprocessing import Process
import subprocess
import time
import unittest
import os

from sip_common.heartbeat import Listener

class HeartbeatTest(unittest.TestCase):
    def setUp(self):
        proc = os.path.join(os.path.dirname(__file__),'heartbeat_test_send.py')
        self.pid = subprocess.Popen(proc)
        self.listener = Listener(1000)
        self.listener.connect('localhost', '12345')

    def testSimple(self):
        time.sleep(2)
        msg = self.listener.listen()
        self.assertEqual(msg[0], 'test')
        self.pid.kill()

if __name__ == '__main__':
    unittest.main()
