import graphene

from handlers.graphql.interfaces import Object
from handlers.graphql.resolvers.diskimage import resolve_vdis
from handlers.graphql.types.xen import XenObjectType


def vdiType():
    from .vdi import DiskImage
    return DiskImage


class SR(XenObjectType):
    import xenadapter.sr as sr

    XenClass = sr.SR
    class Meta:
        interfaces = (Object, )
    PBDs = graphene.List(graphene.ID)
    VDIs = graphene.Field(graphene.List(vdiType), resolver=resolve_vdis)
    content_type = graphene.Field(graphene.String, required=True)
