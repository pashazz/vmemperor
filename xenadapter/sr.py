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
    type = graphene.Field(graphene.String, required=True)
    physical_size = graphene.Field(graphene.Float, required=True, description="Physical size in kilobytes")
    virtual_allocation = graphene.Field(graphene.Float, required=True, description="Virtual allocation in kilobytes")
    is_tools_sr = graphene.Field(graphene.Boolean, required=True, description="This SR contains XenServer Tools")
    physical_utilisation = graphene.Field(graphene.Float, required=True, description="Physical utilisation in kilobytes")
    space_available = graphene.Field(graphene.Float, required=True, description="Available space in kilobytes")


class SR(XenObject):
    api_class = "SR"
    db_table_name = "srs"
    EVENT_CLASSES=["sr"]
    GraphQLType = GSR

    @classmethod
    def process_record(cls, auth, ref, record):
        for key in 'physical_size', 'physical_utilisation', 'virtual_allocation':
            record[key] = int(record[key]) / 1024
        record['space_available'] = record['physical_size'] - record['physical_utilisation']
        return super().process_record(auth, ref, record)



