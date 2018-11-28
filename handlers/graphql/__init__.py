from graphene_tornado.tornado_graphql_handler import TornadoGraphQLHandler

import graphene

from graphene import ObjectType, Schema

from tornado.escape import to_unicode
from .types.vm import VM
from .types.iso import ISO
from .types.vdi import VDI
import xenadapter.vm
from .resolvers.vm import resolve_all_vms

class QueryRoot(ObjectType):

    thrower = graphene.String(required=True)
    request = graphene.String(required=True)
    test = graphene.String(who=graphene.String())
    vms = graphene.List(VM, required=True, resolver=resolve_all_vms)
    vm = graphene.Field(VM, required=True, uuid=graphene.ID(), resolver=VM.one())



    def resolve_thrower(self, info):
        raise Exception("Throws!")

    def resolve_request(self, info):
        return to_unicode(info.context.arguments['q'][0])

    def resolve_test(self, info, who=None):
        return 'Hello %s' % (who or 'World')




class MutationRoot(ObjectType):
    write_test = graphene.Field(QueryRoot)

    def resolve_write_test(self, info):
        return QueryRoot()


schema = Schema(query=QueryRoot, mutation=MutationRoot, types=[ISO, VDI])