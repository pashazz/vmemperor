import  graphene

from handlers.graphql.resolvers.vm import resolve_vms
from ..interfaces import ACLObject


def vmType():
    from .vm import VM
    return VM


class Network(graphene.ObjectType):

    class Meta:
        interfaces = (ACLObject, )

    VMs = graphene.List(vmType,resolver=resolve_vms)
    other_config = graphene.JSONString()



