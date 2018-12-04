import graphene

from authentication import AdministratorAuthenticator, NotAuthenticatedException
import rethinkdb as r


def resolve_one(cls, graphql_type, field_name=None, index=None):
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

    if not field_name:
        field_name = cls.__name__

    from handlers.graphql.resolvers import with_connection
    @with_connection
    def resolver(root, info, **kwargs):
        if 'uuid' in kwargs:
            uuid = kwargs['uuid']
        else:
            uuid = getattr(root, field_name)
        try:
            obj = cls(uuid=uuid,auth=info.context.user_authenticator)
        except AttributeError:
            raise NotAuthenticatedException()


        obj.check_access(action=None)

        if index is None:
            record = cls.db.table(cls.db_table_name).get(uuid).run()
        else:
            record = cls.db.table(cls.db_table_name).get_all(uuid, index=index).coerce_to('array').run()[0]

        return graphql_type(**record)

    return resolver


def resolve_many(cls, graphql_type, field_name=None, index=None):
    '''
    Use this method to many one XenObject that appears in tables as their  uuids under its name
    :param cls: XenObject class
    :param graphql_type: graphene type
    :return resolver for many object that either gets one named argument uuids with list of uuids or
    gets uuids from root's field named after XenObject class in plural form , e.g. for VM it will be
    root.VMs

    If user does not have access for one of these objects, returns None in its place
    '''
    if not issubclass(graphql_type, graphene.ObjectType):
        raise AttributeError(f"No GraphQL type given to resolve_many({cls})")

    if not field_name:
        field_name = f'{cls.__name__}s'
    from handlers.graphql.resolvers import with_connection
    @with_connection
    def resolver(root, info, **kwargs):
        if 'uuids' in kwargs:
            uuids = kwargs['uuids']
        else:
            uuids = getattr(root, field_name)
        if not index:
            records = cls.db.table(cls.db_table_name).get_all(*uuids).run()
        else:
            records = cls.db.table(cls.db_table_name).get_all(*uuids, index=index).run()


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

def resolve_all(cls, graphql_type):
    '''
    Resolves all objects belonging to a user
    :param cls:
    :param graphql_type:
    :return:
    '''
    if not issubclass(graphql_type, graphene.ObjectType):
        raise AttributeError(f"No GraphQL type given to resolve_all({cls})")

    from handlers.graphql.resolvers import with_connection
    @with_connection
    def resolver(root, info, **kwargs):
        '''

        :param root:
        :param info:
        :param kwargs: Optional keyword arguments for pagination: "page" and "page_size"

        :return:
        '''
        from constants import user_table_ready



        from xenadapter.xenobject import ACLXenObject
        auth = info.context.user_authenticator
        if not issubclass(cls, ACLXenObject) or isinstance(auth, AdministratorAuthenticator): #return all
            query = \
            cls.db.table(cls.db_table_name).coerce_to('array')
        else:
            user_table_ready.wait()
            user_id = auth.get_id()
            entities = (f'users/{user_id}', 'any', *(f'groups/{group_id}' for group_id in auth.get_user_groups()))
            query = \
            cls.db.table(f'{cls.db_table_name}_user').get_all(*entities, index='userid'). \
                pluck('uuid').coerce_to('array'). \
                merge(cls.db.table(cls.db_table_name).get(r.row['uuid']).without('uuid'))

        if 'page' in kwargs:
            page_size = kwargs['page_size']
            query = query.slice((kwargs['page'] - 1) * page_size, page_size)

        records = query.run()
        return [graphql_type(**record) for record in records]

    return resolver