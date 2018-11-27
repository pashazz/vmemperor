from handlers.graphql.resolvers.sr import resolve_sr
from . import Object
import graphene
def srType():
    from ..types.sr import SR
    return SR

def vmType():
    from ..types.vm import VM
    return VM

class DiskImage(Object):
    SR = graphene.Field(srType, resolver=resolve_sr)
    VMs = graphene.List(vmType)
    virtual_size = graphene.Field(graphene.Float, required=True)



