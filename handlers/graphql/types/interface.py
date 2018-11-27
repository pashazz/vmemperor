import graphene




class Interface(graphene.ObjectType):
    from .network import Network
    from handlers.graphql.resolvers.network import resolve_network
    id = graphene.Field(graphene.ID, required=True)
    MAC = graphene.Field(graphene.String, required=True)
    VIF = graphene.Field(graphene.ID, required=True)
    ip = graphene.Field(graphene.String)
    ipv6 = graphene.Field(graphene.String)
    network = graphene.Field(Network, required=True, resolver=resolve_network)
    status = graphene.Field(graphene.String)
    attached = graphene.Field(graphene.Boolean, required=True)
