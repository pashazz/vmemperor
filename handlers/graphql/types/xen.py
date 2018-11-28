import graphene
from handlers.graphql.resolvers.utils import *
class XenObjectType(graphene.ObjectType):
    XenClass = None
    @classmethod
    def one(cls):
        return resolve_one(cls.XenClass, cls)



