from abc import abstractmethod
from typing import Type, Union

import graphene

from tasks import TaskList
from xenadapter.xenobjectdict import XenObjectDict


class ObjectType(graphene.ObjectType):
    '''
    Implements mapping and iterable iterfaces around graphene's ObjectType so
    we could pass our objects to other functions pythonically
    '''

    def __iter__(self):
        for element in self._meta.fields:
            yield element, getattr(self, element)

    def keys(self):
        return self._meta.fields.keys()

    def __getitem__(self, item):
        return getattr(self, item)


class InputObjectType(graphene.InputObjectType):
    '''
    Implements mapping and iterable iterfaces around graphene's ObjectType so
    we could pass our objects to other functions pythonically
    '''

    def __iter__(self):
        for element in self._meta.fields:
            yield element, getattr(self, element)

    def keys(self):
        return self._meta.fields.keys()

    def __getitem__(self, item):
        return getattr(self, item)


class GrapheneTaskList(TaskList):

    @property
    @abstractmethod
    def task_type(self) -> Union[Type[ObjectType], Type[InputObjectType]]:
        """
        A graphene type which is a format for this tasklist.
        Each task has current state represented by this graphene type
        :return: type
        """
        ...

    def upsert_task(self, auth, task_data : task_type):
        assert isinstance(task_data, self.task_type)
        super().upsert_task(auth, XenObjectDict(**task_data))

    def get_task(self, auth, id):
        data = super().get_task(auth, id)
        task = self.task_type()
        for field in task._meta.fields.keys():
            setattr(task, field, data[field])