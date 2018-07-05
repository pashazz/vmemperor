import unittest
from auth.ispldap import *

class LDAPISpTest(unittest.TestCase):

    def test_ldap_group_name_by_id(self):
        '''
        In our system  there is wifi users
        '''
        self.assertEqual(LDAPIspAuthenticator.get_group_name_by_id("5b8527e5-cff7-403e-bb74-485f3d71c9dd"), "Wifi users")

    def test_get_all_groups(self):
        '''

        '''
        self.assertIn("5b8527e5-cff7-403e-bb74-485f3d71c9dd", LDAPIspAuthenticator.get_all_groups().keys())