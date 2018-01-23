from unittest import skip
from vmemperor import *
import os
from tornado import  testing
from tornado.httpclient import HTTPRequest
from urllib.parse import urlencode
from base64 import decodebytes
import pickle
from tornado.web import create_signed_value
import pprint


settings_read = False
'''
Usage:
create a file named 'secret.ini' with the following structure:


[test]
username = <username> # Dummy authenticator (default) allows any username
password = <password> # Dummy authenticator (default) allows any password
[machines]
uuid = <test machine uuid>


Tests test_startvm, ..., will be performed on VM specified above.

'''
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

    @classmethod
    def tearDownClass(cls):
        ioloop.IOLoop.instance().stop()


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
        cls.uuid = config['machines']['uuid']
        cls.xen_options = {**opts.group_dict('xenadapter'), **opts.group_dict('rethinkdb')}
        cls.xen_options['debug'] = True

    def setUp(self):
        super().setUp()
        #self.auth = self.app.auth_class()
        #self.auth.check_credentials(self.body['password'], self.body['username'])
        #auth_pickled = pickle.dumps(self.auth)
        #secure_cookie = create_signed_value(self.app.settings['cookie_secret'], 'user', auth_pickled)
        #self.headers = {'Cookie' : b'='.join((b'user', secure_cookie))}
        res_login = self.fetch(r'/login', method='POST', body=urlencode(self.body))
        self.assertEqual(res_login.code, 200, "Failed to login")
        self.headers = {'Cookie': res_login.headers['Set-Cookie']}
        print(res_login)



    def createvm(self):
        config = configparser.ConfigParser()
        config.read('tests/createvm.ini')
        #for body in config._sections.values():
        #    res = self.fetch(r'/createvm', method='POST', body=urlencode(body))
        #    self.assertEqual(res.code, 200)
        body  = config._sections['ubuntu']
        res = self.fetch(r'/createvm', method='POST', body=urlencode(body), headers=self.headers)
        self.assertEqual(res.code, 200)
        uuid = res.body.decode()

        #xen = XenAdapter(self.xen_options, authenticator=self.auth)

        actions = ['launch', 'destroy', 'attach']
        #for action in actions:
        #    self.assertTrue(xen.check_rights(action, uuid))

        print(uuid)
        with open('destroy.txt', 'a') as file:
            print(uuid, file=file)



    def test_createvm(self):
        self.createvm()


    def test_startvm(self): #The Great Testing Machine of Dummy Acc.
        # 1. Get VM Info
        print("Entering test_startvm")
        res = self.fetch(r'/vminfo', method='POST', body=urlencode({'uuid':self.uuid}), headers=self.headers)
        res_dict = json.loads(res.body.decode())

        self.assertEqual(res.code, 200)
        enable = res_dict['power_state'] == 'Halted'
        print("System state: %s" % res_dict['power_state'])


        body = {
            'uuid': self.uuid,
            'enable' : enable
        }

        res = self.fetch(r'/startstopvm', method='POST', body=urlencode(body), headers=self.headers)

        self.assertEqual(res.code, 200)

        print("Waiting for state to change (forever loop)...")
        while True:
            res = self.fetch(r'/vminfo', method='POST', body=urlencode({'uuid':self.uuid}), headers=self.headers)
            self.assertEqual(res.code, 200)
            res_dict2 = json.loads(res.body.decode())
            if res_dict['power_state'] != res_dict2['power_state']:
                print("State changed to %s" % res_dict2['power_state'])
                break

        print("Performing reverse action")

        body = {
            'uuid': self.uuid,
            'enable' : not enable
        }

        res = self.fetch(r'/startstopvm', method='POST', body=urlencode(body), headers=self.headers)

        self.assertEqual(res.code, 200)
        print("Waiting for state to change (forever loop)...")
        while True:
            res = self.fetch(r'/vminfo', method='POST', body=urlencode({'uuid':self.uuid}), headers=self.headers)
            self.assertEqual(res.code, 200)
            res_dict3 = json.loads(res.body.decode())
            if res_dict2['power_state'] != res_dict3['power_state']:
                print("State changed to %s" % res_dict3['power_state'])
                break





    @skip
    def test_convert(self):
        uuid = ''
        body = \
        {
            'uuid' :uuid
        }
        res = self.fetch(r'/convertvm', method='POST', body=urlencode(body), headers=self.headers)
        self.assertEqual(res.code, 200)

    def test_vmlist(self):
        res = self.fetch(r'/vmlist', method='GET', headers=self.headers)
        self.assertEqual(res.code, 200)
        vms = json.loads(res.body.decode())
        pprint.pprint(vms)
        for vm in vms:
            if vm['uuid'] == self.uuid:
                return


        self.fail("uuid %s (testing machine) not found in vmlist" % self.uuid)




    def test_isolist(self):
        res = self.fetch(r'/isolist', method='GET', headers=self.headers)
        self.assertEqual(res.code, 200)
        isos = json.loads(res.body.decode())
        pprint.pprint(isos)

    def test_attach_iso(self):
        res = self.fetch(r'/isolist', method='GET', headers=self.headers)
        self.assertEqual(res.code, 200)
        isos = json.loads(res.body.decode())
        for iso in isos:
            if iso['name_label'] == 'guest-tools.iso':
                body = dict(action='attach', uuid=self.uuid, iso_uuid=iso['uuid'])
                print("Attaching ISO guest-tools")
                res = self.fetch(r'/attachdetachiso', method='POST', body=urlencode(body), headers=self.headers)
                self.assertEqual(res.code, 200)
                body['action'] = 'detach'
                print("Detaching ISO guest-tools")
                res = self.fetch(r'/attachdetachiso', method='POST', body=urlencode(body), headers=self.headers)
                self.assertEqual(res.code, 200)
                return

    def test_destroy_vm(self):
        if not os.path.isfile('destroy.txt'):
            self.createvm()

        with open('destroy.txt',mode='r') as file:
            uuid = file.readline().rstrip('\n')
            rest = file.read()

        if not rest.strip():
            os.remove('destroy.txt')
        else:
            with open('destroy.txt', mode='w') as file:
                file.write(rest)


        body=dict(uuid=uuid)
        res = self.fetch(r'/destroyvm', method='POST', body=urlencode(body), headers=self.headers)
        self.assertEqual(res.code, 200)





