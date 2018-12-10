import graphene

from authentication import with_authentication
from handlers.graphql.graphql_handler import ContextProtocol
from handlers.graphql.mutations.base import MutationMethod, MutationHelper
from handlers.graphql.resolvers import with_connection
from handlers.graphql.types.dicttype import InputObjectType
from xenadapter.vm import VM


class VMInput(InputObjectType):
    uuid = graphene.InputField(graphene.ID, required=True, description="VM ID")
    name_label = graphene.InputField(graphene.String, description="VM human-readable name")
    name_description = graphene.InputField(graphene.String, description="VM human-readable description")
    

def set_name_label(ctx : ContextProtocol, vm : VM, changes : VMInput):
    if changes.name_label is not None:
        vm.set_name_label(changes.name_label)


def set_name_description(ctx: ContextProtocol, vm: VM, changes: VMInput):
    if changes.name_description is not None:
        vm.set_name_description(changes.name_description)

class VMMutation(graphene.Mutation):
    success = graphene.Field(graphene.Boolean, required=True)

    class Arguments:
        vm = graphene.Argument(VMInput, description="VM to change")


    @staticmethod
    @with_authentication
    @with_connection
    def mutate(root, info, vm):
        ctx : ContextProtocol = info.context

        m = VM(auth=ctx.user_authenticator, uuid=vm.uuid)


        mutations = [
            MutationMethod(func=set_name_label, action_name='rename'),
            MutationMethod(func=set_name_description, action_name='rename')
        ]
        helper = MutationHelper(mutations, ctx, m)
        helper.perform_mutations(vm)

        return VMMutation(success=True)
