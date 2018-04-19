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
from sqlalchemy.exc import InvalidRequestError
from authentication import DebugAuthenticator
from time import sleep
settings_read = False
'''
This test uses SQLAlchemy-based authenticator
'''
class VmEmperorTest(testing.AsyncHTTPTestCase):
    @classmethod
    def setUpClass(cls):
        global  settings_read
        if not settings_read:
            read_settings()
            settings_read = True
        cls.executor = ThreadPoolExecutor(max_workers=opts.max_workers)
        if os.path.exists('/tmp/vmemperor-auth.db'):
            os.remove('/tmp/vmemperor-auth.db')

    def setUp(self):
        super().setUp()
        self.ws_url = "ws://localhost:" + str(self.get_http_port())
        print("WebSocket url: %s" % self.ws_url)


    def get_app(self):


        if not hasattr(self, 'app'):
            from auth.sqlalchemyauthenticator import SqlAlchemyAuthenticator
            self.app = make_app(self.executor, debug=True, auth_class=SqlAlchemyAuthenticator)



        return self.app

    def get_new_ioloop(self):
        self.get_app()
        if not hasattr(self, 'event_loop'):
            self.event_loop = event_loop(self.executor, opts.delay, self.app.auth_class)

        return self.event_loop

    @classmethod
    def tearDownClass(cls):
        from auth.sqlalchemyauthenticator import SqlAlchemyAuthenticator
        ioloop.IOLoop.instance().stop()
        SqlAlchemyAuthenticator.session.close()





class VmEmperorNoLoginTest(VmEmperorTest):
    def test_admin_login(self):
        xen_opts = opts.group_dict('xenadapter')
        #auth_tuple = (xen_opts['username'], xen_opts['password'])
        body = dict(username=xen_opts['username'], password=xen_opts['password'])
        res = self.fetch(r'/adminauth', method='POST', body=urlencode(body))
        self.assertEqual(200, res.code)

    def test_failed_admin_login(self):

        # auth_tuple = (xen_opts['username'], xen_opts['password'])
        body = dict(username='olololo', password='alalala')
        res = self.fetch(r'/adminauth', method='POST', body=urlencode(body))
        self.assertEqual(401, res.code)

    def test_list_pools(self):
        res = self.fetch(r'/list_pools', method='GET')
        self.assertEqual(json.dumps([{'id': 1}]), res.body.decode())


class VmEmperorAfterAdminLoginTest(VmEmperorTest):

    def setUp(self):
        super().setUp()
        xen_opts = opts.group_dict('xenadapter')
        body = dict(username=xen_opts['username'], password=xen_opts['password'])
        res = self.fetch(r'/adminauth', method='POST', body=urlencode(body))
        self.assertEqual(200, res.code)
        self.headers = {'Cookie' : res.headers['Set-Cookie']}


    @tornado.testing.gen_test()
    def test_vmlist(self):
        ws_url =  self.ws_url + "/vmlist"
        def msg_callback(text):
            print(text)
        ws_client = yield websocket_connect(HTTPRequest(url=ws_url, headers=self.headers), on_message_callback=msg_callback)

        yield ws_client.read_message()




class VmEmperorAfterLoginTest(VmEmperorTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        config = configparser.ConfigParser()
        config.read('tests/secret.ini')
        cls.body = {'username' : 'john', 'password' : 'john' }
        cls.uuid = config[opts.authenticator]['uuid']

        cls.xen_options = {**opts.group_dict('xenadapter'), **opts.group_dict('rethinkdb')}
        cls.xen_options['debug'] = True

        cls.vms_created = []


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

    @classmethod
    def tearDownClass(cls):
        auth = DebugAuthenticator()
        for uuid in cls.vms_created:
            try:
                vm = VM(auth=auth, uuid=uuid)
                print("Deleting created VM %s" % uuid)
                vm.destroy_vm()
            except:
                continue




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

        body = {'uuid': uuid}
        res = self.fetch(r'/installstatus', method='POST', body=urlencode(body), headers=self.headers)
        self.assertEqual(200, res.code)
        json_res = json.loads(res.body.decode())
        self.assertNotEqual(json_res['state'],'failed', msg=json_res['message'])


        #xen = XenAdapter(self.xen_options, authenticator=self.auth)

        actions = ['launch', 'destroy', 'attach']
        #for action in actions:
        #    self.assertTrue(xen.check_rights(action, uuid))

        print(uuid)
        with open('destroy.txt', 'a') as file:
            print(uuid, file=file)
        self.vms_created.append(uuid)
        return uuid

    @gen.coroutine
    def createvm_gen(self):
        config = configparser.ConfigParser()
        config.read('tests/createvm.ini')
        #for body in config._sections.values():
        #    res = self.fetch(r'/createvm', method='POST', body=urlencode(body))
        #    self.assertEqual(res.code, 200)
        body  = config._sections['ubuntu']
        res = yield self.http_client.fetch(self.get_url(r'/createvm'), method='POST', body=urlencode(body), headers=self.headers)
        self.assertEqual(res.code, 200)
        uuid = res.body.decode()

        body = {'uuid': uuid}
        res = yield self.http_client.fetch(self.get_url(r'/installstatus'), method='POST', body=urlencode(body), headers=self.headers)
        self.assertEqual(200, res.code)
        json_res = json.loads(res.body.decode())
        self.assertNotEqual(json_res['state'],'failed', msg=json_res['message'])


        #xen = XenAdapter(self.xen_options, authenticator=self.auth)

        actions = ['launch', 'destroy', 'attach']
        #for action in actions:
        #    self.assertTrue(xen.check_rights(action, uuid))

        print(uuid)
        with open('destroy.txt', 'a') as file:
            print(uuid, file=file)
        self.vms_created.append(uuid)
        return uuid


    def test_createvm(self):
        self.createvm()

    @tornado.testing.gen_test()
    def test_vmlist(self):
        ws_url =  self.ws_url + "/vmlist"

        ws_client = yield websocket_connect(HTTPRequest(url=ws_url, headers=self.headers))


        uuid = yield self.createvm_gen()
        #new_message = yield websocket_connect(HTTPRequest(url=ws_url, headers=self.headers))
#        print(new_message)
        while True:
            new_message = yield ws_client.read_message()
            if not new_message:
                break
            print(json.loads(new_message))






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




    def test_get_set_access(self):
        uuid = self.createvm()
        body={'uuid': uuid, 'type': 'VM'}
        res = self.fetch(r'/getaccess', method='POST', body=urlencode(body), headers=self.headers)
        self.assertEqual(res.code, 200)
        ans = json.loads(res.body.decode())
        self.assertEqual(ans['access'][0]['userid'], 'users/1')
        self.assertEqual(ans['access'][0]['access'], ['all'])
        body_set = {'uuid': uuid, 'type': 'VM', 'group': '1', 'action': 'launch'}
        # login as eva, not in group
        login_body_eva={'username':'eva', 'password': 'eva'}
        res_login = self.fetch(r'/login', method='POST', body=urlencode(login_body_eva))

        self.assertEqual(res_login.code, 200, "Failed to login")
        headers_eva = {'Cookie': res_login.headers['Set-Cookie']}

        login_body_mike = {'username': 'mike', 'password': 'mike'}
        res_login = self.fetch(r'/login', method='POST', body=urlencode(login_body_mike))
        self.assertEqual(res_login.code, 200, "Failed to login")
        headers_mike = {'Cookie': res_login.headers['Set-Cookie']}

        res = self.fetch(r'/getaccess', method='POST', body=urlencode(body), headers=headers_mike)
        self.assertEqual(res.code, 403, "Access system hijacked by mike: {0}".format(res.body.decode()))
        res = self.fetch(r'/getaccess', method='POST', body=urlencode(body), headers=headers_eva)
        self.assertEqual(res.code, 403, "Access system hijacked by eva")
        res = self.fetch(r'/setaccess', method='POST', body=urlencode(body_set), headers=self.headers)
        self.assertEqual(res.code, 200, "John is unable to grant launch rights to his group")
        res = self.fetch(r'/getaccess', method='POST', body=urlencode(body), headers=headers_mike)
        self.assertEqual(res.code, 200, "Mike should get access rights cause he's in john's group")
        res = self.fetch(r'/getaccess', method='POST', body=urlencode(body), headers=headers_eva)
        self.assertEqual(res.code, 403, "Eva still shouldn't have  obtained access rights")
        res = self.fetch(r'/vminfo', method='POST', body=urlencode(body), headers=headers_eva)
        self.assertEqual(res.code, 403, "Eva shouldn't have got an access info")
        res = self.fetch(r'/vminfo', method='POST', body=urlencode(body), headers=headers_mike)
        self.assertEqual(res.code, 200, "Mike has Launch rights, he must have an ability to get VM info")
        sleep(2)
        res = self.fetch(r'/destroyvm', method='POST', body=urlencode(body), headers=headers_mike)
        self.assertEqual(res.code, 403, "Mike shouldn't have destroyed a VM")
        res = self.fetch(r'/destroyvm', method='POST', body=urlencode(body), headers=headers_eva)
        self.assertEqual(res.code, 403, "Eva shouldn't have destroyed a VM")
        res = self.fetch(r'/destroyvm', method='POST', body=urlencode(body), headers=self.headers)
        self.assertEqual(res.code, 200, "John should destroy test VM")




