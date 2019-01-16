
import pickle
from rethinkdb_helper import  CHECK_ER
from copy import copy
from xenadapter.xenobjectdict import XenObjectDict
from connman import ReDBConnection
from abc import ABC, abstractmethod



class TaskList(ABC):
    def __init__(self, db):
        self.db = db

    @property
    @abstractmethod
    def table(self):
        ...

    def upsert_task(self, auth, task_data):
        '''
        Inserts a task considering authentication information
        :param auth:
        :param task_data: dict. Use your own class to convert your datatype into a dict and then call upsert_task
        :return:
        '''
        if auth:  # replace
            user_id = auth.get_id()

            CHECK_ER(self.table.insert({**XenObjectDict(task_data), **{'userid': user_id}}, conflict='replace').run())
        else:  # update
            CHECK_ER(self.table.insert(XenObjectDict(task_data), conflict='update').run())

    def get_task(self, auth, id) -> dict:
        task = self.table.get(id).run()
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


