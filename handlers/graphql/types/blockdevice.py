import graphene



from handlers.graphql.resolvers.diskimage import resolve_vdi

def diskImageType():
    from xenadapter.disk import DiskImage
    return DiskImage


class BlockDevice(graphene.ObjectType):
    id = graphene.Field(graphene.ID, required=True)
    attached = graphene.Field(graphene.Boolean, required=True)
    bootable = graphene.Field(graphene.Boolean, required=True)
    device = graphene.Field(graphene.String, required=True)
    mode = graphene.Field(graphene.String, required=True)
    type = graphene.Field(graphene.String, required=True)
    VDI = graphene.Field(diskImageType, resolver=resolve_vdi)