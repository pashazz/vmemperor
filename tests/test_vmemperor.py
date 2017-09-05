from vmemperor import *
from tornado import  testing
from tornado.httpclient import HTTPRequest
from urllib.parse import urlencode

class VmEmperorTest(testing.AsyncHTTPTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        read_settings()
        self.executor = ThreadPoolExecutor(max_workers=opts.max_workers)


    def get_app(self):

        app=make_app(self.executor, LDAPIspAuthenticator, True)
        return app

    def get_new_ioloop(self):

        return event_loop(opts.delay)

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

    def test_createvm(self):

        config = configparser.ConfigParser()
        config.read('tests/createvm.ini')
        for body in config._sections.values():
            res = self.fetch(r'/createvm', method='POST', body=urlencode(body))
            self.assertEqual(res.code, 200)



