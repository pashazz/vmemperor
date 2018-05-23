import unittest
from xenadapter.xenobjectdict import XenObjectDict
from datetime import datetime
from xmlrpc.client import DateTime
import pytz

class XenObjectDictTest(unittest.TestCase):

    def test_conversion(self):
        now = datetime.utcnow().replace(microsecond=0, tzinfo=pytz.utc)
        # XML Datetime doesnt care about microseconds
        now_xml = DateTime(now)

        old_d = {'value' : now_xml }
        new_d = XenObjectDict(old_d)

        self.assertEqual(now, new_d['value'])
        self.assertEqual(pytz.utc, new_d['value'].tzinfo)
