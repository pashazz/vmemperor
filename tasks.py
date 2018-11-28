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
            user_id = auth.get_id()

            CHECK_ER(self.table.insert({**XenObjectDict(operation), **{'userid': user_id}}, conflict='replace').run())
        else: # update
            CHECK_ER(self.table.insert(XenObjectDict(operation), conflict='update').run())

    def get_operation(self, auth, id):
        operation = self.table.get(id).run()
        if not operation:
            raise KeyError("No operation")
        if auth.get_id() == operation['userid']:
            del operation['userid']
            return operation
        else:
            raise KeyError('Wrong authentication object')



