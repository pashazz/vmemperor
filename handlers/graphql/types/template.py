import graphene
import xenadapter.template
from handlers.graphql.types.xen import XenObjectType


class Template(XenObjectType):

    XenClass = xenadapter.template.Template

