from .xenobject import XenObject

class Pool (XenObject):
    db_table_name = 'pools'
    api_class = 'pool'
    EVENT_CLASSES = ['pool']
