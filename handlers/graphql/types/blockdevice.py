import graphene

from handlers.graphql.interfaces.diskimage import DiskImage
from handlers.graphql.resolvers.diskimage import resolve_vdi


class BlockDevice(graphene.ObjectType):
    id = graphene.Field(graphene.ID, required=True)
    attached = graphene.Field(graphene.Boolean, required=True)
    bootable = graphene.Field(graphene.Boolean, required=True)
    device = graphene.Field(graphene.String, required=True)
    mode = graphene.Field(graphene.String, required=True)
    type = graphene.Field(graphene.String, required=True)
    VDI = graphene.Field(DiskImage, resolver=resolve_vdi)