import das

__author__ = 'christophe'
__date__ = '13/01/14'

import unittest


class TestSerialConnection(unittest.TestCase):

    def setUp(self):
        self.das = das.Das()

    def test_scan(self):
        out = self.das.scan()
        sl = out[2:6]
        self.assertEqual('Hey!', sl)

    def test_connect(self):
        out = self.das.connect()
        sl = out[0:3]
        self.assertEqual('!HI', sl)

    def test_listen(self):
        out = self.das.listen(2)
        sl = out[0:1]
        self.assertEqual('!', sl)

    def test_set_no_echo(self):
        out = self.das.set_no_echo()
        sl = out[2:5]
        self.assertEqual('!E0', sl)

    def test_set_echo_data(self):
        out = self.das.set_echo_data()
        self.assertEqual( '!E1', out)

    def test_set_echo_data_and_time(self):
        out = self.das.set_echo_data_and_time()
        self.assertEqual('!E2', out)

    def test_set_date_and_time(self):
        out = self.das.set_date_and_time()
        sl = out[0:3]
        self.assertEqual('!SD', sl)

    def test_set_integration_period(self):
        out = self.das.set_integration_period('0060')
        sl = out[0:3]
        self.assertEqual('!SR', sl)

    def test_set_das_netid(self):
        out = self.das.set_das_netid(255)
        print(out)
        sl = out[0:3]
        self.assertEqual('!SI', sl)

    def test_get_das_info(self):
        out = self.das.get_das_info()
        sl = out[0:3]
        self.assertEqual('!RI', sl)

    def test_get_memory_info(self):
        out = self.das.get_memory_info()
        sl = out[0:3]
        self.assertEqual('!RM', sl)

    def test_set_station_id(self):
        out = self.das.set_station_id(43)
        print(repr(out))
        sl = out[0:3]
        self.assertEqual('!SS', sl)

    # def test_flash_das(self):
    #     out = self.das.flash_das()
    #     sl = out[0:3]
    #     self.assertEqual('!ZF', sl)


    # def test_download(self):
    #     self.das.download('/home/christophe/Documents/das-download')

    # def test_next_download(self):
    #     self.das.next_download('/home/christophe/Documents/das-next-download')
