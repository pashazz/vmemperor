import unittest
from authentication import *
from dynamicloader import DynamicLoader
from auth.ispldap import LDAPIspAuthenticator

class DynamicLoaderTest(unittest.TestCase):
    def setUp(self):
        self.loader = DynamicLoader('auth')

    def test_load_isp_ldap(self):
        classes = self.loader.load_class(class_base=BasicAuthenticator)
        self.assertIsInstance(classes, list)
        #self.assertNotIn(DummyAuth, classes)
        self.assertIn( LDAPIspAuthenticator.__name__, (cl.__name__ for cl in classes))