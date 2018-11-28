import graphene




class Interface(graphene.ObjectType):
    from .network import Network
    id = graphene.Field(graphene.ID, required=True)
    MAC = graphene.Field(graphene.String, required=True)
    VIF = graphene.Field(graphene.ID, required=True)
    ip = graphene.Field(graphene.String)
    ipv6 = graphene.Field(graphene.String)
    network = graphene.Field(Network, required=True, resolver=Network.one(field_name="network"))
    status = graphene.Field(graphene.String)
    attached = graphene.Field(graphene.Boolean, required=True)
