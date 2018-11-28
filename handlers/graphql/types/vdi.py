import graphene

from handlers.graphql.interfaces import ACLObject
from handlers.graphql.interfaces.diskimage import DiskImage, vmType
from handlers.graphql.resolvers.vm import resolve_vms
from handlers.graphql.types.xen import XenObjectType


class VDI(XenObjectType):
    import xenadapter.disk as disk
    XenClass = disk.VDI
    class Meta:
        interfaces = (ACLObject, DiskImage)
    VMs = graphene.Field(graphene.List(vmType), resolver=resolve_vms)


