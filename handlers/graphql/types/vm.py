import graphene
from handlers.graphql.resolvers.blockdevice import resolve_disks
from handlers.graphql.resolvers.interface import resolve_interfaces
from handlers.graphql.types.blockdevice import BlockDevice
from handlers.graphql.types.interface import Interface
from ..interfaces import ACLObject
from graphene.types.resolver import dict_resolver

def networkType():
    from .network import Network
    return Network




class PvDriversVersion(graphene.ObjectType):
    '''
    Drivers version. We don't want any fancy resolver except for the thing that we know that it's a dict in VM document
    '''
    class Meta:
        default_resolver = dict_resolver
    major = graphene.Int()
    minor = graphene.Int()
    micro = graphene.Int()
    build = graphene.Int()

class OSVersion(graphene.ObjectType):
    '''
    OS version reported by Xen tools
    '''
    class Meta:
        default_resolver = dict_resolver
    name = graphene.String()
    uname = graphene.String()
    distro = graphene.String()
    major = graphene.Int()
    minor = graphene.Int()



class VM(graphene.ObjectType):

    class Meta:
        interfaces = (ACLObject, )

    # calculated field
    interfaces = graphene.Field(graphene.List(Interface), description="Network adapters connected to a VM", resolver=resolve_interfaces)
    # from http://xapi-project.github.io/xen-api/classes/vm_guest_metrics.html
    PV_drivers_up_to_date = graphene.Field(graphene.Boolean, description="True if PV drivers are up to date, reported if Guest Additions are installed")
    PV_drivers_version = graphene.Field(PvDriversVersion,description="PV drivers version, if available")
    disks = graphene.Field(graphene.List(BlockDevice), resolver=resolve_disks)

    VCPUs_at_startup = graphene.Field(graphene.Int, required=True)
    VCPUs_max = graphene.Field(graphene.Int, required=True)
    domain_type = graphene.Field(graphene.String, required=True)
    guest_metrics = graphene.Field(graphene.ID, required=True)
    install_time = graphene.Field(graphene.DateTime, required=True)
    memory_actual = graphene.Field(graphene.Int, required=True)
    memory_static_min = graphene.Field(graphene.Int, required=True)
    memory_static_max = graphene.Field(graphene.Int, required=True)
    memory_dynamic_min = graphene.Field(graphene.Int, required=True)
    memory_dynamic_max = graphene.Field(graphene.Int, required=True)
    metrics = graphene.Field(graphene.ID, required=True)
    os_version = graphene.Field(OSVersion)
    power_state = graphene.Field(graphene.String, required=True)
    start_time = graphene.Field(graphene.DateTime, required=True)















