import unittest
import sys

from iqrf.util import io


class IoTests(unittest.TestCase):

    def test_to_iotime(self):
        time = 2**16
        self.assertEqual(time, io.to_iotime(time))
        self.assertEqual(sys.maxsize, io.to_iotime(None))
