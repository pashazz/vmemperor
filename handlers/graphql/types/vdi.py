import graphene

from handlers.graphql.interfaces import ACLObject
from handlers.graphql.interfaces.diskimage import DiskImage, vmType



class VDI(graphene.ObjectType):
    class Meta:
        interfaces = (ACLObject, DiskImage)

    from handlers.graphql.resolvers.vm import resolve_vms
    VMs = graphene.Field(graphene.List(vmType), resolver=resolve_vms)


