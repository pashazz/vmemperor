import graphene
class NotAuthenticatedException(Exception):
    def __init__(self):
        super().__init__("You are not authenticated")

def resolve_one(cls, graphql_type):
    '''
    Use this method to resolve one XenObject that appears in tables as its uuid under its name
    :param cls: XenObject class
    :param graphql_type: graphene type
    :return resolver for one object that either gets one named argument uuid or
    gets uuid from root's field named after XenObject class, e.g. for VM it will be
    root.VM
    '''
    if not issubclass(graphql_type, graphene.ObjectType):
        raise AttributeError(f"No GraphQL type given to resolve_one({cls})")

    from handlers.graphql.resolvers import with_connection
    @with_connection
    def resolver(root, info, **kwargs):
        if 'uuid' in kwargs:
            uuid = kwargs['uuid']
        else:
            uuid = getattr(root, cls.__name__)
        try:
            obj = cls(uuid=uuid,auth=info.context.user_authenticator)
        except AttributeError:
            raise NotAuthenticatedException()


        obj.check_access(action=None)

        record = cls.db.table(cls.db_table_name).get(uuid).run()
        return graphql_type(**record)

    return resolver


def resolve_many(cls, graphql_type):
    '''
    Use this method to many one XenObject that appears in tables as their  uuids under its name
    :param cls: XenObject class
    :param graphql_type: graphene type
    :return resolver for many object that either gets one named argument uuids with list of uuids or
    gets uuids from root's field named after XenObject class in plural form , e.g. for VM it will be
    root.VMs
    '''
    if not issubclass(graphql_type, graphene.ObjectType):
        raise AttributeError(f"No GraphQL type given to resolve_many({cls})")

    from handlers.graphql.resolvers import with_connection
    @with_connection
    def resolver(root, info, **kwargs):
        if 'uuids' in kwargs:
            uuids = kwargs['uuids']
        else:
            uuids = getattr(root, f'{cls.__name__}s')
        records = cls.db.table(cls.db_table_name).get_all(*uuids).run()

        def create_graphql_type(record):
            try:
                obj = cls(uuid=record['uuid'], auth=info.context.user_authenticator)
            except AttributeError:
                raise NotAuthenticatedException()
            try:
                obj.check_access(action=None)
            except:
                return None
            return graphql_type(**record)

        return [create_graphql_type(record) for record in records]

    return resolver