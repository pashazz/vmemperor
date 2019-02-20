import graphene

from authentication import with_authentication
from handlers.graphql.graphql_handler import ContextProtocol
from xenadapter.disk import ISO
from xenadapter.vm import VM


class AttachISOMutation(graphene.Mutation):
    taskId = graphene.ID(description="Attach/Detach task ID. If already attached/detached, returns null")

    class Arguments:
        iso_uuid = graphene.ID(required=True)
        vm_uuid = graphene.ID(required=True)
        is_attach = graphene.Boolean(required=True, description="True if attach, False if detach")

    @staticmethod
    @with_authentication(access_class=ISO, access_action='attach', id_field='iso_uuid')
    @with_authentication(access_class=VM, access_action='attach', id_field='vm_uuid')
    def mutate(root, info, iso_uuid, vm_uuid, is_attach):
        ctx: ContextProtocol = info.context
        iso = ISO(uuid=iso_uuid, auth=ctx.user_authenticator)
        if is_attach:
            taskId = iso.attach(VM(uuid=vm_uuid, auth=ctx.user_authenticator))
        else:
            taskId = iso.detach(VM(uuid=vm_uuid, auth=ctx.user_authenticator))
        return AttachISOMutation(taskId=taskId)
