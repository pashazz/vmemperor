from rethinkdb_helper import CHECK_ER
from xenadapter.vm import VM
from xenadapter.xenobject import XenObject

from rethinkdb import RethinkDB
r = RethinkDB()

class Console(XenObject):
    api_class = 'console'
    EVENT_CLASSES = ['console']
    db_table_name = "consoles"

    @classmethod
    def create_db(cls, db, indexes=None):
        super().create_db(db, indexes=['VM'])
