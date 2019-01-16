import graphene

from handlers.graphql.types.dicttype import ObjectType, GrapheneTaskList


class CreateVMTask(ObjectType):
    id = graphene.Field(graphene.ID, required=True, description="VM creation task ID")
    uuid = graphene.Field(graphene.ID, description="UUID of created VM")
    state = graphene.Field(graphene.String, description="VM installation state")
    message = graphene.Field(graphene.String, description="Human-readable message")


class CreateVMTaskList(GrapheneTaskList):
    def table(self):
        return self.db.table('tasks_vms_created')

    def task_type(self):
        return CreateVMTask

