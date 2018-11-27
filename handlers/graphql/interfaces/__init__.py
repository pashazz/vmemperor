import graphene

from handlers.graphql.types.misc import AccessEntry


class Object(graphene.Interface):
    name_label = graphene.Field(graphene.String, required=True, description="a human-readable name")
    name_description = graphene.Field(graphene.String, required=True, description="a human-readable description")
    ref = graphene.Field(graphene.ID, required=True, description="Unique constant identifier/object reference")
    uuid = graphene.Field(graphene.ID, required=True, description="Unique session-dependent identifier/object reference")

class ACLObject(Object):
    access = graphene.List(AccessEntry, required=True)