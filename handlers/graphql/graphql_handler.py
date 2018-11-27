from graphene_tornado.tornado_graphql_handler import TornadoGraphQLHandler

from handlers.base import BaseHandler

class GraphQLHandler(BaseHandler, TornadoGraphQLHandler):
    def initialize(self, *args, **kwargs):
        BaseHandler.initialize(self, *args, **kwargs)
        del kwargs['pool_executor']
        TornadoGraphQLHandler.initialize(self, *args, **kwargs)

    def prepare(self):
        super().prepare()

        #copy some members to context, we'll use then in a resolvers
        self.request.async_run = self.async_run
        self.request.op = self.op
        self.request._ASYNC_KEY = self._ASYNC_KEY
        self.request.user_authenticator = self.user_authenticator
        self.request.conn = self.conn

