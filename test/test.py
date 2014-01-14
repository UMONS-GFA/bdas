__author__ = 'christophe'
__date__ = '13/01/14'

import das
import unittest

class TestSerialConnection(unittest.TestCase):

    def setUp(self):
        self.das = das.Das()

    def test_scan(self):
        out = self.das.scan()
        print(out)
        self.assertEqual(out, '\n\rHey! I\'m NanoDAS 255')

