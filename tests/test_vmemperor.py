from vmemperor import *
from tornado import  testing
from tornado.httpclient import HTTPRequest
from urllib.parse import urlencode
from base64 import decodebytes
class VmEmperorTest(testing.AsyncHTTPTestCase):

    @classmethod
    def setUpClass(cls):
        read_settings()
        cls.executor = ThreadPoolExecutor(max_workers=opts.max_workers)

    def get_app(self):

        app=make_app(self.executor, LDAPIspAuthenticator, True)
        return app

    def get_new_ioloop(self):

        return event_loop(self.executor, opts.delay)

    def test_ldap_login(self):
        '''
        Tests ldap login using settings -> test -> username and password entries

        :return:
        '''
        config = configparser.ConfigParser()
        config.read('tests/secret.ini')
        body=config._sections['test']


        res = self.fetch(r'/login', method='POST', body=urlencode(body))
        self.assertEqual(res.code, 200)


    def test_ldap_login_incorrect_password(self):
        config = configparser.ConfigParser()
        config.read('tests/secret.ini')
        body=config._sections['test']
        body['password'] = ''

        res = self.fetch(r'/login', method='POST', body=urlencode(body))
        self.assertEqual(res.code, 401)

    def test_ldap_group_name_by_id(self):
        '''
        In our system  there is wifi users
        '''
        self.assertEqual(LDAPIspAuthenticator.get_group_name_by_id("5b8527e5-cff7-403e-bb74-485f3d71c9dd"), "Wifi users")

    def test_get_all_groups(self):
        '''

        '''
        self.assertIn("5b8527e5-cff7-403e-bb74-485f3d71c9dd", LDAPIspAuthenticator.get_all_groups().keys())


    def test_createvm(self):
        config = configparser.ConfigParser()
        config.read('tests/createvm.ini')
        #for body in config._sections.values():
        #    res = self.fetch(r'/createvm', method='POST', body=urlencode(body))
        #    self.assertEqual(res.code, 200)
        body  = config._sections['ubuntu']
        res = self.fetch(r'/createvm', method='POST', body=urlencode(body))
        self.assertEqual(res.code, 200)

    def test_startvm(self):
        vm_uuid = '79408dde-d420-0b5b-3f97-fa87715a9da4'
        enable = True
        body = {
            'vm_uuid': vm_uuid,
            'enable': enable
        }
        xen = XenAdapter(opts.group_dict('xenadapter'))
        res = self.fetch(r'/startstopvm', method='POST', body=urlencode(body))
        self.assertEqual(res.code, 200)
        vm_ref = xen.api.VM.get_by_uuid(vm_uuid)
        ps = xen.api.VM.get_power_state(vm_ref)
        if enable:
            self.assertEqual(ps, 'Running')
        else:
            self.assertEqual(ps, 'Halted')

