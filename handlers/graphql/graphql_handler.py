from graphene_tornado.tornado_graphql_handler import TornadoGraphQLHandler
import pickle
from handlers.base import BaseHandler
from xenadapter import XenAdapter
from tornado.options import options as opts

class GraphQLHandler(BaseHandler, TornadoGraphQLHandler):
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
        self.request._ASYNC_KEY = self._ASYNC_KEY
        user = self.get_current_user()
        self.request.executor = self.executor
        if user:
            self.request.user_authenticator = pickle.loads(user)
            self.request.user_authenticator.xen = XenAdapter({**opts.group_dict('xenadapter'), **opts.group_dict('rethinkdb')})
            self.request.op = self.op

            self.request.set_task_status = lambda **operation: self.op.set_operation(self.request.user_authenticator, operation)
            self.request.get_task_status = lambda **operation: self.op.get_operation(self.request.user_authenticator, operation)
        self.request.conn = self.conn

