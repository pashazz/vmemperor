import graphene
import xenadapter.template
from handlers.graphql.interfaces import ACLObject
from handlers.graphql.types.xen import XenObjectType


class Template(XenObjectType):

    XenClass = xenadapter.template.Template

    class Meta:
        interfaces = (ACLObject, )

    os_kind = graphene.Field(graphene.String, description="If a template supports auto-installation, here a distro name is provided")
    hvm = graphene.Field(graphene.Boolean, required=True, description="True if this template works with hardware assisted virtualization")
