from tornado import  testing
from vmemperor import *
from urllib.parse import urlencode
from tests.test_vmemperor import  VmEmperorTest
from auth.ispldap import LDAPIspAuthenticator

class VmEmperorLoginTest(VmEmperorTest):
    auth_class = LDAPIspAuthenticator
    def test_ldap_login(self):
        '''
        Tests ldap login using settings -> test -> username and password entries

        :return:
        '''
        config = configparser.ConfigParser()
        config.read('tests/secret.ini')
        body=config._sections['ispldap']


        res = self.fetch(r'/login', method='POST', body=urlencode(body))
        self.assertEqual(res.code, 200)


    def test_ldap_login_incorrect_password(self):
        config = configparser.ConfigParser()
        config.read('tests/secret.ini')
        body=config._sections['ispldap']
        body['password'] = ''

        res = self.fetch(r'/login', method='POST', body=urlencode(body))
        self.assertEqual(res.code, 401)
