from vmemperor import *
from tornado import  testing
from tornado.httpclient import HTTPRequest
from urllib.parse import urlencode

class VmEmperorTest(testing.AsyncHTTPTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = read_settings()

    def get_app(self):

        app=make_app(LDAPIspAuthenticator, True)
        return app

    def get_new_ioloop(self):
        delay  = 1000
        if 'ioloop' in self.settings:
            if 'delay' in self.settings['ioloop']:
                delay = int(self.settings['ioloop']['delay'])

        return event_loop(delay)

    def test_ldap_login(self):
        '''
        Tests ldap login using settings -> test -> username and password entries

        :return:
        '''
        config = configparser.ConfigParser()
        config.read('secret.ini')
        body=config._sections['test']


        res = self.fetch(r'/login', method='POST', body=urlencode(body))
        self.assertEqual(res.code, 200)

    def test_ldap_login_incorrect_password(self):
        config = configparser.ConfigParser()
        config.read('secret.ini')
        body=config._sections['test']
        body['password'] = ''

        res = self.fetch(r'/login', method='POST', body=urlencode(body))
        self.assertEqual(res.code, 401)



