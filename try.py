from configparser import ConfigParser
from xenadapter import XenAdapter

config = ConfigParser()
config.read('login.ini')
settings = config['settings']
print(settings['login'])
xen = XenAdapter(settings)