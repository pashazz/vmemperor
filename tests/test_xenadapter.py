import unittest
from configparser import ConfigParser
from xenadapter import XenAdapter
import requests
import rethinkdb
from vmemperor import read_settings, opts
from authentication import DummyAuth
from unittest import mock

read_settings_called = False
import  pprint

class XenAdapterSetupMixin:
    @classmethod
    def setUpClass(cls):
        if not hasattr(cls, 'auth_obj'):
            cls.auth_obj = None


        global read_settings_called
        if not read_settings_called:
            read_settings()
            read_settings_called = True


        cls.settings = {**opts.group_dict('xenadapter'), **opts.group_dict('rethinkdb')};
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

    @unittest.skip
    def test_check_rights(self):
        uuid = self.uuid
        vm_ref = self.xen.api.VM.get_by_uuid(uuid)
        self.xen.manage_actions('launch', uuid, force=True, user=self.userid)
        self.assertTrue(self.xen.api.VM.get_xenstore_data(vm_ref))
        self.assertTrue(self.xen.check_rights('launch', uuid=uuid))




class TestXenAdapterRootMethods(unittest.TestCase, XenAdapterSetupMixin):
    # def test_list_vms(self):
    #    vms = self.xen.list_vms()
    #    print(vms)


    @classmethod
    def setUpClass(cls):
        XenAdapterSetupMixin.setUpClass()

    @unittest.skip
    def test_list_srs(self):
        srs = self.xen.list_srs()
        pprint.pprint(srs)

    def test_list_vdis(self):
  #      print('\nList of ALL VDIs')
        keys= ('uuid', 'name_label', 'location')
#        vdis = self.xen.list_vdis()

 #       vdis = {uuid : {k: v for k, v in data.items() if k in keys}
 #             for uuid, data in vdis.items()}
        #vdis = {uuid : {k: v for k, v in data.items()}
#                for uuid, data in vdis.items() if data['name_label'].endswith('.iso') or data['location'].endswith('.iso')}


      #  pprint.pprint(vdis)

   # def test_list_sr_contents(self):
   #     print('\nSMB ISO SR CONTENTS:')
    #    sr_uuid='0997d0ec-8a0b-1678-8e99-ca5754da4c9f'
     #   keys = ('uuid', 'name_label', 'location')
#        vdis = self.xen.list_vdis(sr_uuid)
 #       vdis = {uuid: {k: v for k, v in data.items() if k in keys}
#                for uuid, data in vdis.items()}
  #      pprint.pprint(vdis)


    def test_list_isos(self):
        isos = self.xen.list_isos()
        pprint.pprint(isos)

    def test_list_templates(self):
        tmpls = self.xen.list_templates()
        pprint.pprint(tmpls)