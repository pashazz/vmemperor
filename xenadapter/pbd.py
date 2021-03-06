import graphene

from handlers.graphql.resolvers.host import hostType, resolve_host
from handlers.graphql.resolvers.sr import srType, resolve_sr
from handlers.graphql.types.gxenobjecttype import GXenObjectType
from xenadapter.xenobject import XenObject

class GPBD(GXenObjectType):
    '''
    Fancy name for a PBD. Not a real Xen object, though a connection
    between a host and a SR
    '''
    ref = graphene.Field(graphene.ID, required=True, description="Unique constant identifier/object reference")
    uuid = graphene.Field(graphene.ID, required=True,
                          description="Unique session-dependent identifier/object reference")
    host = graphene.Field(hostType, required=True, description="Host to which the SR is supposed to be connected to", resolver=resolve_host)
    device_config = graphene.Field(graphene.JSONString, required=True)
    SR = graphene.Field(srType, required=True, resolver=resolve_sr)
    currently_attached = graphene.Field(graphene.Boolean, required=True)


class PBD (XenObject):
    db_table_name = 'pbds'
    api_class = 'pbd'
    EVENT_CLASSES = ['pbd']
    GraphQLType = GPBD
