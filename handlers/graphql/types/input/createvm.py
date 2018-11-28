import graphene

class CreateVM(graphene.Mutation):
    task_id = graphene.Field(graphene.ID, required=True, description="Installation task ID")

    class Arguments:
        template = graphene.Field(graphene.ID, required=True, description="Template ID")

    @staticmethod
    def mutate(root, info, task_id=None):
        return CreateVM(task_id=1)
