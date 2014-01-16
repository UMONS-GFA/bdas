__author__ = 'christophe'
__date__ = '13/01/14'

import das
import unittest


class TestSerialConnection(unittest.TestCase):

    def setUp(self):
        self.das = das.Das()

    def test_scan(self):
        out = self.das.scan()
        sl = out[2:6]
        self.assertEqual(sl, 'Hey!')

    def test_connect(self):
        out = self.das.connect()
        sl = out[0:3]
        self.assertEqual(sl, '!HI')

    def test_listen(self):
        out = self.das.listen(2)
        sl = out[0:1]
        self.assertEqual(sl, '!')

    def test_set_no_echo(self):
        out = self.das.set_no_echo()
        sl = out[2:5]
        self.assertEqual(sl, '!E0')

    # def test_download(self):
    #     self.das.download('/home/christophe/Documents/das-download')
