import graphene

from handlers.graphql.interfaces import Object
from handlers.graphql.resolvers.diskimage import resolve_vdis
from handlers.graphql.types.vdi import VDI


def vdiType():
    from .vdi import DiskImage
    return DiskImage


class SR(graphene.ObjectType):
    class Meta:
        interfaces = (Object, )
    PBDs = graphene.List(graphene.ID)
    VDIs = graphene.Field(graphene.List(VDI), resolver=resolve_vdis)
    content_type = graphene.Field(graphene.String, required=True)
