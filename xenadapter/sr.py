import graphene

from handlers.graphql.resolvers.diskimage import resolve_vdis, vdiType
from xenadapter.xenobject import XenObject, GXenObject
from handlers.graphql.types.gxenobjecttype import GXenObjectType


class GSR(GXenObjectType):
    class Meta:
        interfaces = (GXenObject,)
    PBDs = graphene.List(graphene.ID)
    VDIs = graphene.Field(graphene.List(vdiType), resolver=resolve_vdis)
    content_type = graphene.Field(graphene.String, required=True)

class SR(XenObject):
    api_class = "SR"
    db_table_name = "srs"
    EVENT_CLASSES=["sr"]
    GraphQLType = GSR

