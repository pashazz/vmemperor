import graphene

from handlers.graphql.types.dicttype import ObjectType
from rethinkdb_helper import CHECK_ER


class CreateVMTask(ObjectType):
    id = graphene.Field(graphene.ID, required=True, description="VM creation task ID")
    uuid = graphene.Field(graphene.ID, description="UUID of created VM")
    state = graphene.Field(graphene.String, description="VM installation state")
    message = graphene.Field(graphene.String, description="Human-readable message")
