import graphene

from authentication import with_authentication
from handlers.graphql.graphql_handler import ContextProtocol
from handlers.graphql.mutations.base import MutationMethod, MutationHelper
from handlers.graphql.resolvers import with_connection
from handlers.graphql.types.dicttype import InputObjectType
from xenadapter.vm import VM


class StartInput(InputObjectType):
    paused = graphene.InputField(graphene.Boolean, default_value=False, description="Should this VM be started and immidiately paused")
    # todo Implement Host field
    force = graphene.InputField(graphene.Boolean, default_value=False, description="Should this VM be started forcibly")

class VMInput(InputObjectType):
    uuid = graphene.InputField(graphene.ID, required=True, description="VM ID")
    name_label = graphene.InputField(graphene.String, description="VM human-readable name")
    name_description = graphene.InputField(graphene.String, description="VM human-readable description")
    start = graphene.InputField(StartInput, description="Should this VM be started and how")





def set_name_label(ctx : ContextProtocol, vm : VM, changes : VMInput):
    if changes.name_label is not None:
        vm.set_name_label(changes.name_label)


def set_name_description(ctx: ContextProtocol, vm: VM, changes: VMInput):
    if changes.name_description is not None:
        vm.set_name_description(changes.name_description)

def start(ctx: ContextProtocol, vm: VM, changes: VMInput):
    if changes.start is not None:
        vm.start(changes.start.paused, changes.start.force)

class VMMutation(graphene.Mutation):
    success = graphene.Field(graphene.Boolean, required=True)

    class Arguments:
        vm = graphene.Argument(VMInput, description="VM to change", required=True)
        start = graphene.Argument


    @staticmethod
    @with_authentication
    @with_connection
    def mutate(root, info, vm):
        ctx : ContextProtocol = info.context

        m = VM(auth=ctx.user_authenticator, uuid=vm.uuid)


        mutations = [
            MutationMethod(func=set_name_label, action_name='rename'),
            MutationMethod(func=set_name_description, action_name='rename')
            MutationMethod(func=start, action_name='change_power_state')
        ]
        helper = MutationHelper(mutations, ctx, m)
        helper.perform_mutations(vm)

        return VMMutation(success=True)
