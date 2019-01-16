from __future__ import annotations
#from graphene_tornado.tornado_graphql_handler import TornadoGraphQLHandler as BaseGQLHandler
from tornadoql.tornadoql import GraphQLSubscriptionHandler as BaseGQLSubscriptionHandler, GraphQLHandler as BaseGQLHandler
import pickle

from authentication import BasicAuthenticator
from connman import ReDBConnection
from handlers.base import BaseHandler, BaseWSHandler
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




class GraphQLHandler(BaseHandler, BaseGQLHandler):
    request : ContextProtocol
    def initialize(self, *args, **kwargs):
        BaseHandler.initialize(self, *args, **kwargs)
        del kwargs['pool_executor']
        BaseGQLHandler.initialize(self, *args, **kwargs)

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

            self.request.set_task_status = lambda **operation: self.op.upsert_task(self.request.user_authenticator, operation)
            self.request.get_task_status = lambda id: self.op.get_task(self.request.user_authenticator, id)
        self.request.conn = self.conn


class GraphQLSubscriptionHandler(BaseWSHandler, BaseGQLSubscriptionHandler):
    request: ContextProtocol

    def initialize(self, *args, **kwargs):
        BaseWSHandler.initialize(self, *args, **kwargs)
        del kwargs['pool_executor']
        BaseGQLSubscriptionHandler.initialize(self, *args, **kwargs)

    def prepare(self):
        super().prepare()

        # copy some members to context, we'll use then in a resolvers
        #self.request.async_run = self.async_run

        self.request.log = self.log
        self.request.actions_log = self.actions_log
        self.request.executor = self.executor
