import graphene
from handlers.graphql.resolvers.utils import *
class XenObjectType(graphene.ObjectType):
    XenClass = None
    @classmethod
    def one(cls, field_name=None, index=None):
        return resolve_one(cls.XenClass, cls, field_name, index)

    @classmethod
    def many(cls, field_name=None, index=None):
        return resolve_many(cls.XenClass, cls, field_name, index)

    @classmethod
    def all(cls):
        return resolve_all(cls.XenClass, cls)


