import unittest
from configparser import ConfigParser
from xenadapter import XenAdapter


class XenAdapterSetupMixin:
    @classmethod
    def setUpClass(cls):
        cls.config = ConfigParser()
        cls.config.read('../login.ini')
        cls.settings = cls.config._sections['settings']  # dictionary

        cls.xen = XenAdapter(cls.settings)

    @classmethod
    def tearDownClass(cls):
        cls.xen.session._logout()
        # self.xen.api.logout()

class TestXenAdapterList(unittest.TestCase, XenAdapterSetupMixin):
    '''
    This class tests list functions
    '''
    @classmethod
    def setUpClass(cls):
        XenAdapterSetupMixin.setUpClass()

    @classmethod
    def tearDownClass(cls):
        XenAdapterSetupMixin.tearDownClass()

    def test_list_pools(self):
        pools = XenAdapterSetupMixin.xen.list_pools()
        self.assertIs(type(pools), list)
        self.assertTrue(len(pools))

    def test_list_vms(self):
        self.assertIs(type(XenAdapterSetupMixin.xen.list_vms()), list)

    def test_list_vdis(self):
        vdis = XenAdapterSetupMixin.xen.list_vdis()
        self.assertIs(type(vdis), list)
        self.assertTrue(len(vdis))

    def test_list_srs(self):
        srs = XenAdapterSetupMixin.xen.list_srs()
        self.assertTrue(next(sr for sr in srs if sr['name_label'] == 'Local storage'))

    def test_list_networks(self):
        networks = XenAdapterSetupMixin.xen.list_networks()
        self.assertIs(type(networks), list)
        self.assertTrue(len(networks))
        
    def test_list_templates(self):
        templates = XenAdapterSetupMixin.xen.list_templates()
        self.assertIs(type(templates), list)
        self.assertTrue(len(templates))

class TestXenAdapterVM(unittest.TestCase, XenAdapterSetupMixin):
    '''
    This class creates a test VM in its setUp and removes in tearDown
    '''
    VM_NAME = 'Test VM created by unittest'
    @classmethod
    def setUpClass(cls):
        XenAdapterSetupMixin.setUpClass()
        #create vm
        sr_uuid = cls.choose_sr()
        template_uuid = cls.choose_template()
        net_uuid = cls.choose_net()
        cls.vm_uuid = cls.xen.create_vm(template_uuid, sr_uuid, net_uuid, '2048', TestXenAdapterVM.VM_NAME)

    @classmethod
    def tearDownClass(cls):
        '''
        halt vm with a hard shutdown
        Destroy VM and call superclass tearDown
        '''
        XenAdapterSetupMixin.xen.hard_shutdown(cls.vm_uuid)
        XenAdapterSetupMixin.xen.destroy_vm(cls.vm_uuid)
        XenAdapterSetupMixin.tearDownClass()

    @classmethod
    def choose_sr(cls):
        '''
        :return: storage repository object to test against
        '''
        return XenAdapterSetupMixin.xen.uuid_by_name(XenAdapterSetupMixin.xen.api.SR, 'Local storage')


    @classmethod
    def choose_template(cls):
        '''
        :return: template to test against
        '''
        return next((templ['uuid'] for templ in XenAdapterSetupMixin.xen.list_templates() if templ['name_label'] == 'Ubuntu Trusty Tahr 14.04'))

    @classmethod
    def choose_net(cls):
        '''
        :return: network IF to test against
        '''
        return XenAdapterSetupMixin.xen.uuid_by_name(XenAdapterSetupMixin.xen.api.network, 'Pool-wide network associated with eth0')



    def test_vm_exists(self):
        '''
        Test if setUp works correctly and test vm is created
        '''

        self.assertNotEqual(XenAdapterSetupMixin.xen.uuid_by_name(XenAdapterSetupMixin.xen.api.VM, TestXenAdapterVM.VM_NAME),
                             str())
        self.assertIn(TestXenAdapterVM.vm_uuid, (vm['uuid'] for vm in XenAdapterSetupMixin.xen.list_vms()))



