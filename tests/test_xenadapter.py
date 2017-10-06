import unittest
from configparser import ConfigParser
from xenadapter import XenAdapter
import requests
import rethinkdb
from vmemperor import read_settings, opts
from authentication import DummyAuth
from unittest import mock

read_settings_called = False

class XenAdapterSetupMixin:
    @classmethod
    def setUpClass(cls):
        if not hasattr(cls, 'auth_obj'):
            cls.auth_obj = None


        global read_settings_called
        if not read_settings_called:
            read_settings()
            read_settings_called = True


        cls.settings = opts.group_dict('xenadapter')
        cls.settings['debug'] = True
        cls.xen = XenAdapter(cls.settings, cls.auth_obj)

    @classmethod
    def tearDownClass(cls):
        cls.xen.session._logout()
        # cls.xen.session.logout()


class TestXenAdapterWithLogin(unittest.TestCase, XenAdapterSetupMixin):
    '''
    This class creates XenAdapter with a Dummy authentication object
    '''
    @classmethod
    def setUpClass(cls):
        cls.uuid = 'fc4eec10-0cb6-406a-14b8-42b1c8dc63ac'
        cls.userid = '570e9a59-e3bd-42c5-87ee-d46b312dbfcb'
        XenAdapterSetupMixin.auth_obj = DummyAuth(id=cls.userid, name='Ololoj Ololojson')
        XenAdapterSetupMixin.setUpClass()

    def test_check_rights(self):
        uuid = self.uuid
        vm_ref = self.xen.api.VM.get_by_uuid(uuid)
        self.xen.manage_actions('launch', uuid, force=True, user=self.userid)
        self.assertTrue(self.xen.api.VM.get_xenstore_data(vm_ref))
        self.assertTrue(self.xen.check_rights('launch', uuid=uuid))

    def test_list_vms(self):
        vms = self.xen.list_vms()
        print(vms)