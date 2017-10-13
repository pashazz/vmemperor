from unittest import skip
from vmemperor import *
from tornado import  testing
from tornado.httpclient import HTTPRequest
from urllib.parse import urlencode
from base64 import decodebytes
import pickle
from tornado.web import create_signed_value

settings_read = False
class VmEmperorTest(testing.AsyncHTTPTestCase):
    @classmethod
    def setUpClass(cls):
        global  settings_read
        if not settings_read:
            read_settings()
            settings_read = True
        cls.executor = ThreadPoolExecutor(max_workers=opts.max_workers)

    def get_app(self):
        if not hasattr(self, 'app'):
            self.app = make_app(self.executor, debug=True)
        return self.app

    def get_new_ioloop(self):
        self.get_app()
        return event_loop(self.executor, opts.delay, self.app.auth_class)


class VmEmperorNoLoginTest(VmEmperorTest):
    def test_admin_login(self):
        xen_opts = opts.group_dict('xenadapter')
        #auth_tuple = (xen_opts['username'], xen_opts['password'])
        body = dict(username=xen_opts['username'], password=xen_opts['password'])
        res = self.fetch(r'/adminauth', method='POST', body=urlencode(body))
        self.assertEqual(res.code, 200)

    def test_failed_admin_login(self):

        # auth_tuple = (xen_opts['username'], xen_opts['password'])
        body = dict(username='olololo', password='alalala')
        res = self.fetch(r'/adminauth', method='POST', body=urlencode(body))
        self.assertEqual(res.code, 401)





class VmEmperorAfterLoginTest(VmEmperorTest):


    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        config = configparser.ConfigParser()
        config.read('tests/secret.ini')
        cls.body = config._sections['test']
        cls.xen_options = opts.group_dict('xenadapter')
        cls.xen_options['debug'] = True


    def setUp(self):
        super().setUp()
        self.auth = self.app.auth_class()
        self.auth.check_credentials(self.body['password'], self.body['username'])
        auth_pickled = pickle.dumps(self.auth)
        secure_cookie = create_signed_value(self.app.settings['cookie_secret'], 'user', auth_pickled)
        self.headers = {'Cookie' : b'='.join((b'user', secure_cookie))}



    def test_createvm(self):
        config = configparser.ConfigParser()
        config.read('tests/createvm.ini')
        #for body in config._sections.values():
        #    res = self.fetch(r'/createvm', method='POST', body=urlencode(body))
        #    self.assertEqual(res.code, 200)
        body  = config._sections['ubuntu']
        res = self.fetch(r'/createvm', method='POST', body=urlencode(body), headers=self.headers)
        self.assertEqual(res.code, 200)
        uuid = res.body.decode()

        xen = XenAdapter(self.xen_options, authenticator=self.auth)

        actions = ['launch', 'destroy', 'attach']
        for action in actions:
            self.assertTrue(xen.check_rights(action, uuid))

        print(uuid)

    @skip
    def test_startvm(self, uuid='ololo'):
        xen = XenAdapter(self.xen_options)
        body = {
            'uuid': uuid,
            'enable': True
        }
        res = self.fetch(r'/startstopvm', method='POST', body=urlencode(body), headers=self.headers)
        self.assertEqual(res.code, 200)
        vm_ref = xen.api.VM.get_by_uuid(uuid)
        ps = xen.api.VM.get_power_state(vm_ref)
        self.assertEqual(ps, 'Running')


    def test_vmlist(self):
        res = self.fetch(r'/vmlist', method='GET', headers=self.headers)
        self.assertEqual(res.code, 200)
        vms = json.loads(res.body.decode())


        print(res.body)
