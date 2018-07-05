import collections
from xmlrpc.client import DateTime as xmldt
from datetime import datetime
import pytz

class XenObjectDict(collections.UserDict):
    '''
    This dict converts XMLRPC datetime to Python (UTC) datetime when inserted
    Only insert UTC times. Create your own implementation for localtimes using tzlocal if you want
    '''
    def __setitem__(self, key, value):

        value = self.get_value(value)
        self.data.__setitem__(key, value)


    def get_value(self, value):
        if isinstance(value, xmldt):
            try:  # XenAPI standard time format. Z means strictly UTC
                time =  datetime.strptime(value.value, "%Y%m%dT%H:%M:%SZ")
            except ValueError:  # try Python time format
                time =  datetime.strptime(value.value, "%Y%m%dT%H:%M:%S")

            time = time.replace(tzinfo=pytz.utc)
            return time

        elif isinstance(value, dict):
            return XenObjectDict(value)
        elif isinstance(value, list):
            return [self.get_value(item) for item in value]
        else:
            return value

