import graphene

from handlers.graphql.graphql_handler import ContextProtocol
from handlers.graphql.resolvers import with_connection
from authentication import with_authentication
from handlers.graphql.types.dicttype import InputObjectType
from xenadapter.template import Template

class TemplateInput(InputObjectType):
    uuid = graphene.InputField(graphene.ID, required=True, description="Template ID")
    enabled = graphene.InputField(graphene.Boolean,
                                description="Should this template be enabled, i.e. used in VMEmperor by users")

class TemplateMutation(graphene.Mutation):
    success = graphene.Field(graphene.Boolean, required=True)

    class Arguments:
        template = graphene.Argument(TemplateInput, description="Template to change")

    @staticmethod
    @with_authentication
    @with_connection
    def mutate(root, info, template):
        ctx : ContextProtocol = info.context

        t = Template(auth=ctx.user_authenticator, uuid=template.uuid)

        return TemplateMutation(success=True)



