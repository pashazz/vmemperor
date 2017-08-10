import unittest
from configparser import ConfigParser
from xenadapter import XenAdapter

class TestXenAdapterList(unittest.TestCase):
    def setUp(self):
        self.config = ConfigParser()
        self.config.read('../login.ini')
        self.settings = self.config._sections['settings'] #dictionary

        self.xen = XenAdapter(self.settings)

    def tearDown(self):
        self.xen.session._logout()
        #self.xen.api.logout()


    def test_list_pools(self):
        pools = self.xen.list_pools()
        self.assertIs(type(pools), list)
        self.assertTrue(len(pools))

    def test_list_vms(self):
        self.assertIs(type(self.xen.list_vms()), list)

    def test_list_vdis(self):
        vdis = self.xen.list_vdis()
        self.assertIs(type(vdis), list)
        self.assertTrue(len(vdis))


    def test_list_networks(self):
        networks = self.xen.list_networks()
        self.assertIs(type(networks), list)
        self.assertTrue(len(networks))
        
    def test_list_templates(self):
        templates = self.xen.list_templates()
        self.assertIs(type(templates), list)
        self.assertTrue(len(templates))

