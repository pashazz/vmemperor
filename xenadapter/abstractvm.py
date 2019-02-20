from .xenobject import ACLXenObject

from xenadapter.helpers import use_logger
import XenAPI
from authentication import BasicAuthenticator
import provision
from .xenobjectdict import XenObjectDict

from .osdetect import *

class AbstractVM(ACLXenObject):
    api_class = 'VM'

