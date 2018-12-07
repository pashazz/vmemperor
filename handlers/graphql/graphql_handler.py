from __future__ import annotations
from graphene_tornado.tornado_graphql_handler import TornadoGraphQLHandler
import pickle

from authentication import BasicAuthenticator
from connman import ReDBConnection
from handlers.base import BaseHandler
from xenadapter import XenAdapter
from tornado.options import options as opts
from typing import _Protocol, Mapping, Any, ContextManager
from logging import Logger
class ContextProtocol(_Protocol):
    def async_run(self, task_ref : str) -> None:
        '''
        This method awaits for XenAPI task completion in executor
        :param task_ref: XenAPI task reference
        :return: None
        '''
        ...

    log : Logger # XenAdapter log, see loggable.py, logs in vmemperor.log
    actions_log : Logger #XenAdapter actions log, for VM installs, logs in action.log
    conn: ContextManager # RethinkDB connection manager
    user_authenticator: BasicAuthenticator # Current user's authenticator

    def set_task_status(self, **kwargs) -> None:
        '''
        Assigns a new Operation, i.e. a non XenAPI task which need to be cache and subsequently returned to user as part of GraphQL response.
        Example: CreateVM status messages
        Here, the format is free and defined by GraphQL mutations and their underlying methods themselves
        The Operation is user-bound, i.e. no user apart from current user and administrators can view these Operations

        :param kwargs: arguments to insert into a database
        :return:
        '''
        ...

    def get_task_status(self, id) -> Mapping[str, Any]:
        '''
        Get a Task: deserialized JSON data with string keys, the format is not defined here
        :param id: 
        :return: 
        '''
        ...








class GraphQLHandler(BaseHandler, TornadoGraphQLHandler):
    request : ContextProtocol
    def initialize(self, *args, **kwargs):
        BaseHandler.initialize(self, *args, **kwargs)
        del kwargs['pool_executor']
        TornadoGraphQLHandler.initialize(self, *args, **kwargs)

    def prepare(self):
        super().prepare()

        #copy some members to context, we'll use then in a resolvers
        self.request.async_run = self.async_run

        self.request.log = self.log
        self.request.actions_log = self.actions_log
        user = self.get_current_user()
        self.request.executor = self.executor
        if user:
            self.request.user_authenticator = pickle.loads(user)
            self.request.user_authenticator.xen = XenAdapter({**opts.group_dict('xenadapter'), **opts.group_dict('rethinkdb')})

            self.request.set_task_status = lambda **operation: self.op.set_operation(self.request.user_authenticator, operation)
            self.request.get_task_status = lambda id: self.op.get_operation(self.request.user_authenticator, id)
        self.request.conn = self.conn

