import graphene

from authentication import with_authentication
from handlers.graphql.graphql_handler import ContextProtocol
from xenadapter.disk import VDI, VDIorISO
from xenadapter.vm import VM


class AttachVDIMutation(graphene.Mutation):
    taskId = graphene.ID(description="Attach/Detach task ID. If already attached/detached, returns null")

    class Arguments:
        vdi_uuid = graphene.ID(required=True)
        vm_uuid = graphene.ID(required=True)
        is_attach = graphene.Boolean(required=True, description="True if attach, False if detach")

    @staticmethod
    @with_authentication(access_class=VDIorISO, access_action='attach', id_field='vdi_uuid')
    @with_authentication(access_class=VM, access_action='attach', id_field='vm_uuid')
    def mutate(root, info, vdi_uuid, vm_uuid, is_attach):
        ctx: ContextProtocol = info.context
        vdi = VDIorISO(uuid=vdi_uuid, auth=ctx.user_authenticator)
        if is_attach:
            taskId = vdi.attach(VM(uuid=vm_uuid, auth=ctx.user_authenticator))
        else:
            taskId = vdi.detach(VM(uuid=vm_uuid, auth=ctx.user_authenticator))
        return AttachVDIMutation(taskId=taskId)
