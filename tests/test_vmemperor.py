from unittest import skip
from vmemperor import *
import os
from tornado import  testing
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from urllib.parse import urlencode
from base64 import decodebytes
import pickle
from tornado.web import create_signed_value
import tornado.ioloop
import pprint
from sqlalchemy.exc import InvalidRequestError
from authentication import DebugAuthenticator
from time import sleep
from frozendict import frozendict
from loggable import Loggable

settings_read = False
'''
This test uses SQLAlchemy-based authenticator
'''
class VmEmperorTest(testing.AsyncHTTPTestCase, Loggable):

    def to_hashable(self, x):
        if type(x) == dict:
            return frozendict(x)
        elif type(x) == list:
            #return set((self.to_hashable(i) for i in x))
            return frozenset(x)
        else:
            return x




    def check_lists_equality(self, first, second, msg=None):
        '''
        Return true if lists are equal as if they were unordered
        '''

        return self.assertEqual(self.to_hashable(first), self.to_hashable(second), msg)







    def __init__(self, methodName):
        super().__init__(methodName)


        self.addTypeEqualityFunc(list, self.check_lists_equality)
        self.addTypeEqualityFunc(dict, self.check_lists_equality)

    @classmethod
    def setUpClass(cls):
        global  settings_read
        if not settings_read:
            read_settings()
            settings_read = True
        cls.executor = ThreadPoolExecutor(max_workers=opts.max_workers)

        asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())

        if not hasattr(cls, 'auth_class'):
            from auth.sqlalchemyauthenticator import SqlAlchemyAuthenticator
            cls.auth_class = SqlAlchemyAuthenticator
        cls.app = make_app(cls.executor, debug=True, auth_class=cls.auth_class)
        opts.database = opts.database + '_debug_{0}_{1}'.format(cls.__name__, datetime.datetime.now().strftime("%b_%d_%Y_%H_%M_%S"))
        cls.event_loop = event_loop(cls.executor, cls.app.auth_class)



    def setUp(self):
        super().setUp()
        self.init_log()
        self.log.info("setUp {0}".format(self.id()))
        self.ws_url = "ws://localhost:" + str(self.get_http_port())
        print("\nWebSocket url: %s" % self.ws_url)


    def get_app(self):

        return self.app

    def get_new_ioloop(self):
        return self.event_loop

    @classmethod
    def tearDownClass(cls):
        from auth.sqlalchemyauthenticator import SqlAlchemyAuthenticator
        SqlAlchemyAuthenticator.session.close()
        cls.event_loop.stop()
        super().tearDownClass()

    def tearDown(self):
        self.log.info("tearDown {0}".format(self.id()))




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


    #@tornado.testing.gen_test()
    #def test_vmlist(self):
    #    ws_url =  self.ws_url + "/vmlist"
    #    def msg_callback(text):
    #        with open('file.txt', 'a') as obj:
    #            obj.write(text)

    #    ws_client = yield websocket_connect(HTTPRequest(url=ws_url, headers=self.headers), on_message_callback=msg_callback)

    #    yield ws_client.read_message()
    #    self.wait()



class VmEmperorAfterLoginTest(VmEmperorTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        config = configparser.ConfigParser()
        config.read('tests/secret.ini')
        cls.login_body = {'username' : 'john', 'password' : 'john' }
        cls.uuid = config[opts.authenticator]['uuid']

        cls.xen_options = {**opts.group_dict('xenadapter'), **opts.group_dict('rethinkdb')}
        cls.xen_options['debug'] = True

        cls.vms_created = []

        config = configparser.ConfigParser()
        config.read('tests/createvm.ini')
        # for body in config._sections.values():
        #    res = self.fetch(r'/createvm', method='POST', body=urlencode(body))
        #    self.assertEqual(res.code, 200)
        cls.body = config._sections['ubuntu']



    def setUp(self):
        super().setUp()

        res_login = self.fetch(r'/login', method='POST', body=urlencode(self.login_body))
        self.assertEqual(res_login.code, 200, "Failed to login")
        self.headers = {'Cookie': res_login.headers['Set-Cookie']}

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
        super().tearDownClass()




    def createvm(self, return_name_label=False):
        body = self.body.copy()
        body['name_label'] = body['name_label'] + ' ' + self.id() + ' ' +  datetime.datetime.now().strftime('%D %H:%M:%S')
        name_label = body['name_label']
        res = self.fetch(r'/createvm', method='POST', body=urlencode(body), headers=self.headers)
        self.assertEqual(res.code, 200)
        uuid = res.body.decode()

        body = {'uuid': uuid}
        res = self.fetch(r'/installstatus', method='POST', body=urlencode(body), headers=self.headers)
        self.assertEqual(200, res.code)
        json_res = json.loads(res.body.decode())
        self.assertNotEqual(json_res['state'],'failed', msg=json_res['message'])


        actions = ['launch', 'destroy', 'attach']

        print(uuid)

        self.vms_created.append(uuid)
        if return_name_label:
            return uuid, name_label
        else:
            return uuid

    @gen.coroutine
    def createvm_gen(self, return_name_label=False):
        body = self.body.copy()
        body['name_label'] = body['name_label'] + ' ' + self.id() + datetime.datetime.now().strftime(
            '%D %H:%M:%S')
        name_label = body['name_label']
        res = yield self.http_client.fetch(self.get_url(r'/createvm'), method='POST', body=urlencode(body), headers=self.headers, request_timeout=9999)
        self.assertEqual(res.code, 200)
        uuid = res.body.decode()

        body = {'uuid': uuid}
        res = yield self.http_client.fetch(self.get_url(r'/installstatus'), method='POST', body=urlencode(body), headers=self.headers)
        self.assertEqual(200, res.code)
        json_res = json.loads(res.body.decode())
        self.assertNotEqual(json_res['state'],'failed', msg=json_res['message'])



        actions = ['launch', 'destroy', 'attach']


        print(uuid)
        self.vms_created.append(uuid)
        if return_name_label:
            return uuid, name_label
        else:
            return uuid


    def test_createvm(self):
        self.createvm()

    @tornado.testing.gen_test()
    def test_vmlist(self):

        '''
        This test opens a connection to vmlist, creates a new VM and tests if the
        behaviour of this method during createVM, access rights changing and destroying
        is valid

        TODO: determine which disk is attached in an independent way
        '''

        ws_url =  self.ws_url + "/vmlist"

        ws_client = yield websocket_connect(HTTPRequest(url=ws_url, headers=self.headers, request_timeout=9999, connect_timeout=9999))

        step = 0
        expected = {
                      'disks' : [],
                      'network' : [],
                      'power_state' : 'Halted',
                      'type': 'add',
                      'access' :
                      [
                          {
                              'access' : ['all'],
                              'userid' : 'users/1' # todo переделать
                          }
                      ]

                  }
        # step 0 is performed before the loop
        expected['uuid'], expected['name_label'] = yield self.createvm_gen(return_name_label=True)
        self.log.info("creating test VM {0}".format(expected['uuid']))
        step += 1

        while True:
            new_message = yield ws_client.read_message()
            obj = json.loads(new_message)
            if not obj:
                self.fail("JSON parsing error: " + new_message)




            if  ('uuid' in obj and obj['uuid'] != expected['uuid']) or\
                ('new_val'in obj and obj['new_val']['uuid'] != expected['uuid']) or\
                ('old_val' in obj and obj['old_val']['uuid'] != expected['uuid']):
                self.log.debug("dropped object (my uuid is {1}): {0}".format(new_message, expected['uuid']))
                continue

            self.log.debug(new_message)


            try:
                if  obj['new_val']['memory_actual'] != obj['old_val']['memory_actual']:
                    self.log.info("checking that RAM size is reported right")
                    self.assertEqual(str(int(self.body['ram_size'])*1024*1024),
                                     obj['new_val']['memory_actual'],
                                     "check that RAM size is real")

            except KeyError:
                pass

            if 'new_val' in obj and  'memory_actual' in obj['new_val']:
                del obj['new_val']['memory_actual']

            if 'old_val' in obj and 'memory_actual' in obj['old_val']:
                del obj['old_val']['memory_actual']

            if 'new_val' in obj and 'old_val' in obj and\
                self.to_hashable(obj['new_val']) == self.to_hashable(obj['old_val']):
                continue




            if step == 1:
                self.log.info("checking that VM is created")
                expected['ref'] = obj['ref'] # ref should be set on step one and be constant
                expected['metrics'] = obj['metrics'] # metrics too
                del expected['type'] # from now on we will compare expected with obj['new_val'] and 'new_val' does not have 'type' field
                #type field is always on outermost level
            elif step == 2: ## Checking if installation is started
                self.log.info("checking if installation is started")
                self.assertTrue('install_time' in obj['new_val'])
                self.assertTrue('start_time' in obj['new_val'])
                expected['install_time'] = obj['new_val']['install_time']
                expected['start_time'] = obj['new_val']['start_time']



            elif step == 3: ## attaching disk
                self.log.info("checking that disk is attached")
                if len(obj['new_val']['disks']) != 1:
                    self.fail("Failed to attach disk: field 'disks' has {0} entries, expected: 1 entry".format(len(obj['disks'])))
                expected['disks'] = obj['new_val']['disks']


            elif step == 4: ## attaching network
                self.log.info("checking that network is connected")
                expected['network'] = [ self.body['network'] ]
                self.assertEqual(expected, obj['new_val'], "failed to attach network")

            elif step == 5: #turning vm on
                self.log.info("checking that VM is turning on")
                expected['power_state'] = 'Running'
                self.assertEqual(expected, obj['new_val'], 'Failed to launch VM')
                ## grant launch access to group 1 & move to step 5
                body_set = {'uuid': expected['uuid'], 'type': 'VM', 'group': '1', 'action': 'launch'}

            elif step == 6: #checking start_time
                self.log.info("checking that VM is turned on and granting launch rights to group 1")
                self.assertNotEqual(expected['start_time'], obj['new_val']['start_time'])
                expected['start_time'] = obj['new_val']['start_time']

                # this line is influenced by http://www.tornadoweb.org/en/stable/testing.html#tornado.testing.gen_test
                # regular self.fetch doesn't support a coroutine yield
                res = yield self.http_client.fetch(self.get_url(r'/setaccess'), method='POST', body=urlencode(body_set),
                                                   headers=self.headers,
                                                   request_timeout=9999)
                self.assertEqual(res.code, 200, "John is unable to grant launch rights to his group")
            elif step == 7: #launch to group 1
                self.log.info("checking that launch rights are granted and granting destroy rights to group 1")
                expected['access'].append( {'userid' : 'groups/1', 'access' : ['launch']})
                self.assertEqual(expected, obj['new_val'], "Failed to inspect VM state change after setting launch rights to the group 1")
                body_set['action'] = 'destroy'
                res = yield self.http_client.fetch(self.get_url(r'/setaccess'), method='POST', body=urlencode(body_set),
                                                   headers = self.headers, request_timeout=9999)
                self.assertEqual(res.code, 200, "John is unable to give destroy rights to group 1")
            elif step == 8:
                self.log.info("checking that destroy rights are granted and revoking destroy rights from group 1")
                for access in expected['access']:
                    if access['userid'] == 'groups/1':
                        access['access'].append('destroy')
                self.assertEqual(expected, obj['new_val'], 'Failed to inspect that destroy is added to group 1 ')

                yield gen.sleep(1)
                body_set = {'uuid': expected['uuid'], 'type': 'VM', 'group': 1, 'action': 'destroy', 'revoke': True }
                res = yield self.http_client.fetch(self.get_url(r'/setaccess'), method='POST', body=urlencode(body_set),
                                                   headers=self.headers, request_timeout=9999)
                self.assertEqual(res.code, 200, "John is unable to revoke destroy rights from group 1")
            elif step == 9:# revoke destroy from group 1
                self.log.info("checking that destroy rights are revoked and revoking launch rights from group 1")
                for access in expected['access']:
                    if access['userid'] == 'groups/1':
                        access['access'].remove('destroy')
                self.assertEqual(expected, obj['new_val'], 'Failed to inspect that destroy is removed from group 1')

                body_set = {'uuid': expected['uuid'], 'type': 'VM', 'group': 1, 'action': 'launch', 'revoke': True}
                res = yield self.http_client.fetch(self.get_url(r'/setaccess'), method='POST', body=urlencode(body_set),
                                                   headers=self.headers)
                self.assertEqual(res.code, 200, "John is unable to revoke launch rights from group 1")

            elif step == 10:
                self.log.info("checking that launch rights are revoked and request to destroy VM")
                k = 0
                for i, access in enumerate(expected['access']):
                    if access['userid'] == 'groups/1':
                        k = i
                        break
                else:
                    self.fail()

                del expected['access'][k]

                self.assertEqual(expected, obj['new_val'], 'Failed to inspect that launch  is removed from group 1')

                yield gen.sleep(1)
                res = yield self.http_client.fetch(self.get_url(r'/destroyvm'), method='POST', body=urlencode(body_set),
                                                   headers=self.headers)
                self.assertEqual(200, res.code, "John is unable to destroy machine")


            elif step == 11:
                self.log.info("checking that VM is halted")
                expected['power_state'] = 'Halted'
                self.assertEqual(expected, obj['new_val'], "Failed to inspect that VM is halted after destroyvm")
            elif step == 12:
                self.log.info('checking that start_time is set to 0 UNIX')
                expected['start_time'] = "01.01.1970, 00:00:00"
                self.assertEqual(expected, obj['new_val'], "Failed to inspect that start_time is 0 UNIX")

            elif step == 13:
                self.log.info("checking that VM is deleted")
                self.assertEqual(expected, obj['old_val'], "Failed to inspect VM is deleted")
                self.assertEqual('remove', obj['type'])
                break

            step += 1



        self.vms_created.clear()
        yield gen.sleep(1)
        ws_client.close()
        return

    @skip
    def test_startvm(self):
        # 1. Get VM Info
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


    @skip
    def test_isolist(self):
        res = self.fetch(r'/isolist', method='GET', headers=self.headers)
        self.assertEqual(res.code, 200)
        isos = json.loads(res.body.decode())
        pprint.pprint(isos)

    @skip
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
        uuid = self.createvm()


        body=dict(uuid=uuid)
        res = self.fetch(r'/destroyvm', method='POST', body=urlencode(body), headers=self.headers)
        self.assertEqual(res.code, 200)
        self.vms_created.clear()




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

        self.assertEqual(res_login.code, 200, "Failed to login as Eva")
        headers_eva = {'Cookie': res_login.headers['Set-Cookie']}

        login_body_mike = {'username': 'mike', 'password': 'mike'}
        res_login = self.fetch(r'/login', method='POST', body=urlencode(login_body_mike))
        self.assertEqual(res_login.code, 200, "Failed to login as Mike")
        headers_mike = {'Cookie': res_login.headers['Set-Cookie']}

        res = self.fetch(r'/getaccess', method='POST', body=urlencode(body), headers=headers_mike)
        self.assertEqual(res.code, 403, "Access system hijacked by mike: {0}".format(res.body.decode()))
        res = self.fetch(r'/getaccess', method='POST', body=urlencode(body), headers=headers_eva)
        self.assertEqual(res.code, 403, "Access system hijacked by eva")
        res = self.fetch(r'/setaccess', method='POST', body=urlencode(body_set), headers=self.headers)
        self.assertEqual(res.code, 200, "John is unable to grant launch rights to his group")
        sleep(1)
        res = self.fetch(r'/getaccess', method='POST', body=urlencode(body), headers=headers_mike)
        self.assertEqual(200, res.code, "Mike should get access rights cause he's in john's group")
        res = self.fetch(r'/getaccess', method='POST', body=urlencode(body), headers=headers_eva)
        self.assertEqual(res.code, 403, "Eva still shouldn't have  obtained access rights")
        res = self.fetch(r'/vminfo', method='POST', body=urlencode(body), headers=headers_eva)
        self.assertEqual(res.code, 403, "Eva shouldn't have got an access info")
        res = self.fetch(r'/vminfo', method='POST', body=urlencode(body), headers=headers_mike)
        self.assertEqual(res.code, 200, "Mike has Launch rights, he must have an ability to get VM info")
        sleep(1)
        res = self.fetch(r'/destroyvm', method='POST', body=urlencode(body), headers=headers_mike)
        self.assertEqual(res.code, 403, "Mike shouldn't have destroyed a VM")
        res = self.fetch(r'/destroyvm', method='POST', body=urlencode(body), headers=headers_eva)
        self.assertEqual(res.code, 403, "Eva shouldn't have destroyed a VM")
        res = self.fetch(r'/destroyvm', method='POST', body=urlencode(body), headers=self.headers)
        self.assertEqual(res.code, 200, "John should destroy test VM")

        self.vms_created.clear()



