from loggable import Loggable
from rethinkdb_tools.helper import  CHECK_ER
from xenadapter.xenobjectdict import XenObjectDict
from abc import ABC, abstractmethod
from rethinkdb import RethinkDB

r = RethinkDB()

class TaskList(ABC, Loggable):
    db = None

    def __init__(self):
        self.init_log()



    def __repr__(self):
        return self.__class__.__name__

    @classmethod
    def create_db(cls, db):
        if cls.db:
            return
        cls.db = db
        if cls.table_name not in cls.db.table_list().run():
            cls.db.table_create(cls.table_name(), durability='soft').run()
            cls.db.table(cls.table_name()).wait().run()

    @staticmethod
    @abstractmethod
    def table_name():
        ...

    def upsert_task(self, auth, task_data):
        '''
        Inserts a task considering authentication information
        :param auth:
        :param task_data: dict. Use your own class to convert your datatype into a dict and then call upsert_task
        :return:
        '''

        if not isinstance(task_data, XenObjectDict):
            task_data = XenObjectDict(task_data)
        self.log.debug(f"Upserting task: {task_data['id']}")
        if auth:  # replace
            user_id = auth.get_id()
            query = self.db.table(self.table_name()).insert({**task_data, **{'userid': user_id}}, conflict='replace').run()
        else:  # update
            CHECK_ER(self.table().insert({**task_data}, conflict='update').run())
        self.log.debug(f"Task upserted: {task_data['id']}")

    def get_task(self, auth, id) -> dict:
        task = self.table().get(id).run()
        if not task:
            raise KeyError(f"No such task: {id}")
        if auth.get_id() == task['userid'] or auth.get_id() == 'root':
            return task
        else:
            raise ValueError('Authentication failed')

    def get_all_tasks(self, auth):
        """
        :param auth:
        :return:
        """
