import unittest
from configparser import ConfigParser
from xenadapter import XenAdapter
import requests



class XenAdapterSetupMixin:
    @classmethod
    def setUpClass(cls):
        cls.config = ConfigParser()
        cls.config.read('../login.ini')
        cls.settings = cls.config._sections['settings']  # dictionary
        cls.settings['debug'] = True
        cls.xen = XenAdapter(cls.settings)

    @classmethod
    def tearDownClass(cls):
        cls.xen.session._logout()
        # cls.xen.session.logout()

class TestXenAdapterDict(unittest.TestCase, XenAdapterSetupMixin):
    '''
    This class tests dict functions
    '''
    @classmethod
    def setUpClass(cls):
        XenAdapterSetupMixin.setUpClass()

    @classmethod
    def tearDownClass(cls):
        XenAdapterSetupMixin.tearDownClass()

    def test_list_pools(self):
        pools = self.xen.list_pools()
        self.assertIs(type(pools), dict)
        self.assertTrue(len(pools))
        for key, value in pools.items():
            self.xen.api.pool.get_by_uuid(key) #raises an exception if uuid is invalid


    def test_list_vms(self):
        vms = self.xen.list_vms()
        self.assertIs(type(vms), dict)
        for key, value in vms.items():
            self.xen.api.VM.get_by_uuid(key)

    def test_list_vdis(self):
        vdis = XenAdapterSetupMixin.xen.list_vdis()
        self.assertIs(type(vdis), dict)
        self.assertTrue(len(vdis))
        for key, value in vdis.items():
            self.xen.api.VDI.get_by_uuid(key)

    def test_list_srs(self):
        srs = XenAdapterSetupMixin.xen.list_srs()
        local_storage_key = None
        for key, value in srs.items():
            if value['name_label'] == 'Local storage':
                local_storage_key = key
        self.xen.api.SR.get_by_uuid(local_storage_key)




    def test_list_networks(self):
        networks = XenAdapterSetupMixin.xen.list_networks()
        self.assertIs(type(networks), dict)
        self.assertTrue(len(networks))
        for key, value in networks.items():
            self.xen.api.network.get_by_uuid(key)
        
    def test_list_templates(self):
        templates = XenAdapterSetupMixin.xen.list_templates()
        self.assertIs(type(templates), dict)
        self.assertTrue(len(templates))
        for key, value in templates.items():
            self.xen.api.VM.get_by_uuid(key)


class XenAdapterSetupVmMixin(XenAdapterSetupMixin):
    """
    This class creates a test VM in its setUp and removes in tearDown
    """
    VM_NAME = 'Test VM created by unittest'


    @classmethod
    def setUpClass(cls):
        if not hasattr(cls, 'start'):
            cls.start = True
        XenAdapterSetupMixin.setUpClass()
        #remove all vms that are vm_name
        vms_to_remove=[vm for vm, value in cls.xen.list_vms().items() if value['name_label'] == cls.VM_NAME]
        # create vm
        sr_uuid = cls.choose_sr()
        template_uuid = cls.choose_template()
        net_uuid = cls.choose_net()
        cls.vm_uuid = cls.xen.create_vm(template_uuid, sr_uuid, net_uuid, '2048', TestXenAdapterVM.VM_NAME, cls.start)

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
        return cls.xen.uuid_by_name(cls.xen.api.SR, 'Local storage')

    @classmethod
    def choose_template(cls):
        '''
        :return: template to test against
        '''
        return next((key for key, value in cls.xen.list_templates().items() if
                     value['name_label'] == 'Ubuntu Trusty Tahr 14.04'))

    @classmethod
    def choose_net(cls):
        '''
        :return: network IF to test against
        '''
        return cls.xen.uuid_by_name(cls.xen.api.network, 'Pool-wide network associated with eth0')


class TestXenAdapterVM(unittest.TestCase, XenAdapterSetupVmMixin):
    '''

    '''
    @classmethod
    def setUpClass(cls):
        XenAdapterSetupVmMixin.setUpClass()

    @classmethod
    def tearDownClass(cls):
        '''
        halt vm with a hard shutdown
        Destroy VM and call superclass tgearDown
        '''
        XenAdapterSetupVmMixin.tearDownClass()

    def test_vm_exists(self):
        '''
        Test if setUp works correctly and test vm is created
        '''

        self.assertNotEqual(self.xen.uuid_by_name(self.xen.api.VM, self.VM_NAME),
                             str())
        self.assertIn(self.vm_uuid, self.xen.list_vms().keys())

    def test_vnc_url(self):
        '''
        Test if VNC url is valid
        '''
        vnc_url = self.xen.get_vnc(self.vm_uuid)

        # If we'd use it more than once, move to an external method

        req = requests.api.request('GET', vnc_url, auth=(self.settings['login'], self.settings['password']),
                                   verify=False, headers={"Connection": "close"})
        self.assertEqual(req.status_code, 501) #not implemented





class TestXenAdapterDisk (unittest.TestCase, XenAdapterSetupVmMixin):
    """
    This class creates a Disk, tests attachment and detachment and destroys it
    """
    @classmethod
    def setUpClass(cls):
        XenAdapterSetupVmMixin.start = False
        XenAdapterSetupVmMixin.setUpClass()
        sr_uuid = XenAdapterSetupVmMixin.choose_sr()
        cls.vdi_uuid = cls.xen.create_disk(sr_uuid, '2048', 'Test disk')
        cls.vbd_uuid = None

    @classmethod
    def tearDownClass(cls):
        XenAdapterSetupVmMixin.tearDownClass()
        #cls.xen.destroy_disk(cls.vdi_uuid)

    def test_attachment(self):
        self.vbd_uuid = self.xen.attach_disk(self.vm_uuid, self.vdi_uuid)
        self.assertIsNotNone(self.vbd_uuid)

        vm_ref = self.xen.api.VM.get_by_uuid(self.vm_uuid)

        self.assertIn(self.vbd_uuid, (self.xen.api.VBD.get_uuid(vbd_ref)
                                      for vbd_ref in self.xen.api.VM.get_VBDs(vm_ref)))

    def test_detachment(self):
        self.xen.start_stop_vm(self.vm_uuid, True)
        if (self.xen.detach_disk(self.vbd_uuid) == 1):
            self.xen.start_stop_vm(self.vm_uuid, False)
            self.xen.detach_disk(self.vbd_uuid)

        vm_ref = self.xen.api.VM.get_by_uuid(self.vm_uuid)

        self.assertNotIn(self.vbd_uuid, (self.xen.api.VBD.get_uuid(vbd_ref)
                                      for vbd_ref in self.xen.api.VM.get_VBDs(vm_ref)))



