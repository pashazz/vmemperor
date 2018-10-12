import rethinkdb as r
import pickle
from rethinkdb_helper import  CHECK_ER
from copy import copy
from xenadapter.xenobjectdict import XenObjectDict
from connman import ReDBConnection

class Operations:
    def __init__(self, db):
        self.db = db
        self.table = db.table('tasks')


    def set_operation(self, auth, operation):
        if auth: # replace
            dump_auth = copy(auth)
            del dump_auth.xen
            auth_s = pickle.dumps(dump_auth)

            CHECK_ER(self.table.insert({**XenObjectDict(operation), **{'auth': auth_s}}, conflict='replace').run())
        else: # update
            CHECK_ER(self.table.insert(XenObjectDict(operation), conflict='update').run())

    def get_operation(self, auth, id):
        operation = self.table.get(id).run()
        if not operation:
            raise KeyError("No operation")
        auth_op = pickle.loads(operation['auth'])
        if auth.get_id() == auth_op.get_id() and type(auth) == type(auth_op):
            del operation['auth']
            return operation
        else:
            raise KeyError('Wrong authentication object')



