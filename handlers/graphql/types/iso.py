import graphene

from handlers.graphql.interfaces import ACLObject
from handlers.graphql.interfaces.diskimage import DiskImage, vmType
from handlers.graphql.types.xen import XenObjectType


class ISO(XenObjectType):
    import xenadapter.disk as disk
    XenClass = disk.ISO
    class Meta:
        interfaces = (ACLObject, DiskImage)

    from handlers.graphql.resolvers.vm import resolve_vms
    VMs = graphene.Field(graphene.List(vmType), resolver=resolve_vms)
    location = graphene.Field(graphene.String, required=True)