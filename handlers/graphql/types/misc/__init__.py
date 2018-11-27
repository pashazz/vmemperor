import graphene
class AccessEntry(graphene.ObjectType):
    access = graphene.List(graphene.String, required=True)
    userid = graphene.String(required=True)

