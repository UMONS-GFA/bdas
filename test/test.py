__author__ = 'christophe'
__date__ = '13/01/14'

import das
import unittest


class TestSerialConnection(unittest.TestCase):

    def setUp(self):
        self.das = das.Das()

    # def test_scan(self):
    #     out = self.das.scan()
    #     sl = out[2:6]
    #     self.assertEqual(sl, 'Hey!')
    #
    # def test_connect(self):
    #     out = self.das.connect()
    #     sl = out[0:3]
    #     self.assertEqual(sl, '!HI')
    #
    # def test_listen(self):
    #     out = self.das.listen(2)
    #     sl = out[0:1]
    #     self.assertEqual(sl, '!')
    #
    # def test_set_no_echo(self):
    #     out = self.das.set_no_echo()
    #     sl = out[2:5]
    #     self.assertEqual(sl, '!E0')
    #
    # def test_set_echo_data(self):
    #     out = self.das.set_echo_data()
    #     self.assertEqual(out, '!E1')
    #
    # def test_set_echo_data_and_time(self):
    #     out = self.das.set_echo_data_and_time()
    #     self.assertEqual(out, '!E2')
    #
    # def test_set_date_and_time(self):
    #     out = self.das.set_date_and_time()
    #     sl = out[0:3]
    #     self.assertEqual(sl, '!SD')
    #
    # def test_set_integration_period(self):
    #     out = self.das.set_integration_period('0060')
    #     sl = out[0:3]
    #     self.assertEqual(sl, '!SR')
    #
    # def test_get_integration_period(self):
    #     out = self.das.get_integration_period()
    #     self.assertGreaterEqual(out, 0)
    #     self.assertLessEqual(out, 60)
    #
    # def test_set_das_netid(self):
    #     out = self.das.set_das_netid(255)
    #     print(out)
    #     sl = out[0:3]
    #     self.assertEqual(sl, '!SI')
    #
    # def test_get_das_netid(self):
    #     out = self.das.get_das_netid()
    #     sl = out[0:3]
    #     self.assertEqual(sl, '!SI')

    def test_set_station_id(self):
        out = self.das.set_station_id(42)
        print(out)
        sl = out[0:3]
        self.assertEqual(sl, '!SS')

    def test_get_das_info(self):
        out = self.das.get_das_info()
        sl = out[0:3]
        self.assertEqual(sl, '!RI')

    def test_get_memory_info(self):
        out = self.das.get_memory_info()
        sl = out[0:3]
        self.assertEqual(sl, '!RM')

    # def test_flash_das(self):
    #     out = self.das.flash_das()
    #     sl = out[0:3]
    #     self.assertEqual(sl, '!ZF')


    # def test_download(self):
    #     self.das.download('/home/christophe/Documents/das-download')
