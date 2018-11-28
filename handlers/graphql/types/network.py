import  graphene

from handlers.graphql.resolvers.vm import resolve_vms
from handlers.graphql.types.xen import XenObjectType
from ..interfaces import ACLObject



def vmType():
    from .vm import VM
    return VM


class Network(XenObjectType):
    import xenadapter.network as net
    XenClass = net.Network
    class Meta:
        interfaces = (ACLObject, )

    VMs = graphene.List(vmType,resolver=resolve_vms)
    other_config = graphene.JSONString()



