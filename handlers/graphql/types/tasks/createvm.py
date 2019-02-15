import graphene

from db_classes import create_db_for_me
from handlers.graphql.types.objecttype import ObjectType
from handlers.graphql.types.tasks.graphenetasklist import GrapheneTaskList


class CreateVMTask(ObjectType):
    id = graphene.Field(graphene.ID, required=True, description="VM creation task ID")
    uuid = graphene.Field(graphene.ID, description="UUID of created VM")
    state = graphene.Field(graphene.String, description="VM installation state")
    message = graphene.Field(graphene.String, description="Human-readable message")


class CreateVMTaskList(GrapheneTaskList):

    @staticmethod
    def table_name():
        return 'tasks_vms_created'

    @staticmethod
    def task_type():
        return CreateVMTask

create_db_for_me(CreateVMTaskList)