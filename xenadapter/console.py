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

    @classmethod
    def filter_record(cls, record):
        return record['protocol'] == 'rfb'
