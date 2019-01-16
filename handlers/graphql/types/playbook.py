import graphene
from graphene.types.resolver import dict_resolver

from authentication import with_authentication, with_default_authentication
from handlers.graphql.resolvers import with_connection
from handlers.graphql.types.dicttype import ObjectType
from xenadapter.vm import OSVersion
import rethinkdb
from tornado.options import options as opts


class PlaybookRequirements(ObjectType):
    class Meta:
        default_resolver = dict_resolver
    os_version = graphene.Field(graphene.List(OSVersion), required=True, description="Minimal supported OS versions")

class GPlaybook(ObjectType):
    id = graphene.Field(graphene.ID, required=True, description="Playbook ID")
    inventory = graphene.Field(graphene.String, description="Inventory file path")
    requires = graphene.Field(PlaybookRequirements, description="Requirements for running this playbook")
    #single = graphene.Field(graphene.Boolean, description="")
    name = graphene.Field(graphene.String, required=True, description="Playbook name")
    variables = graphene.Field(graphene.JSONString, description="Variables available for change to an user")


def _resolve_playbook(data):
    p = GPlaybook(**data)
    return p

@with_default_authentication
@with_connection
def resolve_playbook(root, info, id):
    r = rethinkdb.RethinkDB()
    table = r.db(opts.database).table('playbooks')
    data = table.get(id).pluck(*GPlaybook._meta.fields.keys()).run()
    return _resolve_playbook(data)



@with_default_authentication
@with_connection
def resolve_playbooks(root, info):
    r = rethinkdb.RethinkDB()
    table = r.db(opts.database).table('playbooks')
    data = table.pluck(*GPlaybook._meta.fields.keys()).coerce_to('array').run()

    return [_resolve_playbook(item) for item in data]

