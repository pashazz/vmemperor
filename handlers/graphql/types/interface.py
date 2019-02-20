import graphene

from handlers.graphql.resolvers.network import networkType, resolve_network


class Interface(graphene.ObjectType):

    id = graphene.Field(graphene.ID, required=True)
    MAC = graphene.Field(graphene.String, required=True)
    VIF = graphene.Field(graphene.ID, required=True)
    ip = graphene.Field(graphene.String)
    ipv6 = graphene.Field(graphene.String)
    network = graphene.Field(networkType, required=True, resolver=resolve_network)
    status = graphene.Field(graphene.String)
    attached = graphene.Field(graphene.Boolean, required=True)
