import graphene

class CreateVMTask(graphene.ObjectType):
    id = graphene.Field(graphene.ID, required=True, description="VM creation task ID")
    uuid = graphene.Field(graphene.ID, description="UUID of created VM")
    state = graphene.Field(graphene.String, description="VM installation state")
    message = graphene.Field(graphene.String, description="Human-readable message")

