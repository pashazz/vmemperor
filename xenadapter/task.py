from .xenobject import ACLXenObject, GXenObjectType, GAclXenObject
import graphene

class GTask(GXenObjectType):
    class Meta:
        interfaces = (GAclXenObject,)

    created = graphene.Field(graphene.DateTime, required=True, description="Task creation time")
    finished = graphene.Field(graphene.DateTime, required=True, description="Task finish time")
    progress = graphene.Field(graphene.Float, required=True, description="Task progress")
    result = graphene.Field(graphene.ID, description="Task result if available")
    type = graphene.Field(graphene.String, description="Task result type")
    resident_on = graphene.Field(graphene.ID, description="ref of a host that runs this task")
    error_info = graphene.Field(graphene.List(graphene.String), description="Error strings, if failed")


class Task(ACLXenObject):
    api_class = 'task'
    EVENT_CLASSES = ['task']
    db_table_name = 'tasks'
    GraphQLType = GTask
