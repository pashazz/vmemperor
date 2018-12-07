import XenAPI
from exc import *
from authentication import BasicAuthenticator, AdministratorAuthenticator, NotAuthenticatedException, \
    with_authentication
from tornado.concurrent import run_on_executor
import traceback
import rethinkdb as r
from typing import List, Dict
from handlers.graphql.resolvers.utils import resolve_one, resolve_many, resolve_all
from handlers.graphql.types.dicttype import ObjectType
from xenadapter.helpers import use_logger
from .xenobjectdict import XenObjectDict
import threading
import graphene

def dict_deep_convert(d):
    def convert_to_bool(v):
        if isinstance(v, str):
            if v.lower() == 'true':
                return True
            elif v.lower() == 'false':
                return False
        elif isinstance(v, dict):
            return dict_deep_convert(v)

        return v

    return {k: convert_to_bool(v) for k, v in d.items()}



class XenObjectMeta(type):
    def __getattr__(cls, item):
        if item[0] == '_':
            item = item[1:]
        def method(auth, *args, **kwargs):

            if not hasattr(cls, 'api_class'):
                raise XenAdapterArgumentError(auth.xen.log, "api_class not specified for XenObject")

            api_class = getattr(cls, 'api_class')
            api = getattr(auth.xen.api, api_class)
            attr = getattr(api, item)
            try:
                ret = attr(*args, **kwargs)
                if isinstance(ret, dict):
                    ret = dict_deep_convert(ret)
                return ret
            except XenAPI.Failure as f:
                raise XenAdapterAPIError(auth.xen.log, f"Failed to execute static method {api_class}::{item}", f.details)
        return method

    def __init__(cls, what, bases=None, dict=None):
        super().__init__(what, bases, dict)
        cls.db_ready = threading.Event()
        cls.db_ready.clear()


class GXenObject(graphene.Interface):
    name_label = graphene.Field(graphene.String, required=True, description="a human-readable name")
    name_description = graphene.Field(graphene.String, required=True, description="a human-readable description")
    ref = graphene.Field(graphene.ID, required=True, description="Unique constant identifier/object reference")
    uuid = graphene.Field(graphene.ID, required=True, description="Unique session-dependent identifier/object reference")

class GXenObjectType(ObjectType):
    @classmethod
    def get_type(cls, field_name: str):
        type = cls._meta.fields[field_name].type
        while True:
            if isinstance(type, graphene.List):
                class ListSerializer:
                    def __init__(self):
                        self.type = type.of_type
                        while True:
                            if not hasattr(self.type, 'of_type'):
                                if hasattr(self.type, 'serialize'):
                                    break
                                else:
                                    self.type = graphene.ID
                            else:
                                self.type = self.type.of_type

                    def serialize(self, value):
                        return [self.type.serialize(item) for item in value]

                return ListSerializer()


            if not hasattr(type, "of_type"):
                if hasattr(type, 'serialize'):
                    return type
                else:
                    return graphene.ID # Complex objects represented in DB by their refs, i.e. unique string IDs
            else:
                type = type.of_type


class XenObject(metaclass=XenObjectMeta):
    api_class = None
    GraphQLType : GXenObjectType = None # Specify GraphQL type to access Rethinkdb cache
    REF_NULL = "OpaqueRef:NULL"
    db_table_name = ''
    EVENT_CLASSES=[]
    _db_created = False
    db = None
    FAIL_ON_NON_EXISTENCE = True # Fail if object does not exist in cache database. Usable if you know for sure that filter_record is always true


    def __str__(self):
        return f"<{self.__class__.__name__} \"{self.uuid}\">"

    def __init__(self, auth : BasicAuthenticator,  uuid:str=None , ref : str =None):
        '''

        :param auth: authenticator
        either
        :param uuid: object uuid
        :param ref: object ref or object
        '''
        self.auth = auth
        # if not isinstance(xen, XenAdapter):
        #          raise AttributeError("No XenAdapter specified")
        self.log = self.auth.xen.log
        self.xen = self.auth.xen

        if uuid:
            if isinstance(uuid, str):
                self.uuid = uuid
            else:
                raise XenAdapterAPIError(auth.xen.log,
                                         f"Failed to initialize object of type {self.__class__.__name__}: invalid type of uuid. Expected: str, got {uuid.__class__.__name__}: {uuid}")
            try:
                getattr(self, 'ref') #uuid check
            except XenAPI.Failure as f:
                raise  XenAdapterAPIError(auth.xen.log,
                                          f"Failed to initialize object of type {self.__class__.__name__} with UUID {self.uuid}",f.details)
        elif ref:
            if isinstance(ref, str):
                self.ref = ref
            else:
                raise XenAdapterAPIError(auth.xen.log,
                                         f"Failed to initialize object of type {self.__class__.__name__}: invalid type of ref. Expected: str, got {ref.__class__.__name__}")

        else:
            raise AttributeError("Not uuid nor ref not specified")



        self.access_prefix = 'vm-data/vmemperor/access'


    @classmethod
    def resolve_one(cls, field_name=None, index=None):
        '''
        Use this method to resolve one XenObject that appears in tables as its uuid under its name
        :param field_name: root's field name to use (by default - this class' name)
        :return resolver for one object that either gets one named argument uuid or
        gets uuid from root's field named after XenObject class, e.g. for VM it will be
        root.VM
        :param index - table's index to use. OVERRIDE WITH CARE, internally we use refs as links between docs, so to use with linked field, call
        resolve_one(index='ref'). Default is resolving via uuid, as uuid is a primary key there
        :sa handlers/graphql/resolvers directory - they use index='ref' and load object classes in them to avoid circular dependencies
        '''

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
                obj = cls(uuid=uuid, auth=info.context.user_authenticator)
            except AttributeError:
                raise NotAuthenticatedException()

            obj.check_access(action=None)

            if index is None:
                record = cls.db.table(cls.db_table_name).get(uuid).run()
            else:
                record = cls.db.table(cls.db_table_name).get_all(uuid, index=index).coerce_to('array').run()[0]

            return cls.GraphQLType(**record)

        return resolver

    @classmethod
    def resolve_many(cls,field_name=None, index=None):
        '''
           Use this method to many one XenObject that appears in tables as their  uuids under its name
           :param cls: XenObject class
           :param graphql_type: graphene type
           :return resolver for many object that either gets one named argument uuids with list of uuids or
           gets uuids from root's field named after XenObject class in plural form , e.g. for VM it will be
           root.VMs

           If user does not have access for one of these objects, returns None in its place
           '''

        if not field_name:
            field_name = f'{cls.__name__}s'
        from handlers.graphql.resolvers import with_connection
        @with_connection
        @with_authentication
        def resolver(root, info, **kwargs):
            if 'uuids' in kwargs:
                uuids = kwargs['uuids']
            else:
                uuids = getattr(root, field_name)
            if not index:
                records = cls.db.table(cls.db_table_name).get_all(*uuids).coerce_to('array').run()
            else:
                records = cls.db.table(cls.db_table_name).get_all(*uuids, index=index).coerce_to('array').run()

            def create_graphql_type(record):
                try:
                    obj = cls(uuid=record['uuid'], auth=info.context.user_authenticator)
                except AttributeError:
                    raise NotAuthenticatedException()
                try:
                    obj.check_access(action=None)
                except:
                    return None
                return cls.GraphQLType(**record)

            return [create_graphql_type(record) for record in records]

        return resolver

    @classmethod
    def resolve_all(cls):
        '''
        Resolves all objects belonging to a user
        :param cls:

        :return:
        '''
        assert issubclass(cls.GraphQLType, GXenObjectType)
        from handlers.graphql.resolvers import with_connection
        @with_connection
        @with_authentication
        def resolver(root, info, **kwargs):
            '''

            :param root:
            :param info:
            :param kwargs: Optional keyword arguments for pagination: "page" and "page_size"

            :return:
            '''

            query =  cls.db.table(cls.db_table_name).coerce_to('array')


            if 'page' in kwargs:
                page_size = kwargs['page_size']
                query = query.slice((kwargs['page'] - 1) * page_size, page_size)

            records = query.run()
            return [cls.GraphQLType(**record) for record in records]

        return resolver


    def check_access(self,  action):
        return True

    def manage_actions(self, action,  revoke=False, user=None, group=None):
        pass

    @classmethod
    def process_event(cls, auth, event, db, authenticator_name):
        '''
        Make changes to a RethinkDB-based cache, processing a XenServer event
        :param auth: auth object
        :param event: event dict
        :param db: rethinkdb DB
        :param authenticator_name: authenticator class name - used by access control
        :return: nothing
        '''
        from rethinkdb_helper import CHECK_ER

        cls.create_db(db)

        if event['class'] in cls.EVENT_CLASSES:
            if event['operation'] == 'del':
                CHECK_ER(db.table(cls.db_table_name).get_all(event['ref'], index='ref').delete().run())
                return

            record = event['snapshot']
            if not cls.filter_record(record):
                return

            if event['operation'] in ('mod', 'add'):
                new_rec = cls.process_record(auth, event['ref'], record)
                CHECK_ER(db.table(cls.db_table_name).insert(new_rec, conflict='update').run())

    @classmethod
    def create_db(cls, db, indexes=None):
        '''
        Creates a DB table named cls.db_table_name and specified indexes
        :param db:
        :param indexes:
        :return:
        '''
        if not cls.db_table_name:
            return
        def index_yielder():
            yield 'ref'
            if hasattr(indexes, '__iter__'):
                for y in indexes:
                    yield y


        if not cls.db:

            table_list = db.table_list().run()
            if cls.db_table_name not in table_list:
                db.table_create(cls.db_table_name, durability='soft', primary_key='uuid').run()
            index_list = db.table(cls.db_table_name).index_list().coerce_to('array').run()
            for index in index_yielder():
                if not index in index_list:
                    db.table(cls.db_table_name).index_create(index).run()
                    db.table(cls.db_table_name).index_wait(index).run()
                    db.table(cls.db_table_name).wait().run()

            cls.db = db
            cls.db_ready.set()




    @classmethod
    def process_record(cls, auth, ref, record):
        '''
        Used by init_db. Should return dict with info that is supposed to be stored in DB
        :param auth: current authenticator
        :param record:
        :return: dict suitable for document-oriented DB
        : default: return record as-is, adding a 'ref' field with current opaque ref
        '''
        if cls.GraphQLType:
            new_record = {k:cls.GraphQLType.get_type(k).serialize(v) for k,v in record.items() if k in cls.GraphQLType._meta.fields.keys()}
        else:
            new_record = record

        new_record['ref'] = ref



        return new_record

    @classmethod
    def filter_record(cls, record):
        '''
        Returns true if record is suitable for a class
        :param record: record from get_all_records (pure XenAPI method)
        :return: true if record is suitable for this class
        '''
        return True

    @classmethod
    def get_all_records(cls, auth):
        method = getattr(cls, '_get_all_records')
        return {k: v for k, v in method(auth).items()
                if cls.filter_record(v)}

    @classmethod
    def init_db(cls, auth):
        return [cls.process_record(auth, ref, record) for ref, record in cls.get_all_records(auth).items()]

    def set_other_config(self, config):
        config = {k : str(v) for k,v in config.items()}
        self.__getattr__('set_other_config')(config)


    def __getattr__(self, name):
        api = getattr(self.xen.api, self.api_class)
        if name == 'uuid': #ленивое вычисление uuid по ref
            def fallback():
                self.uuid = api.get_uuid(self.ref)
                self.db_table_name = ""
            if self.db_table_name:
                try:
                    self.uuid = self.db.table(self.db_table_name).get_all(self.ref, index='ref').pluck('uuid').coerce_to('array').run()[0]['uuid']
                except IndexError as e: # this object is filtered out by DB cache (i.e. for VM can be filtered for being a control domain)
                    if not self.FAIL_ON_NON_EXISTENCE:
                        fallback()
                    else:
                        raise e
            else:
                self.uuid = api.get_uuid(self.ref)

            return self.uuid
        elif name == 'ref': #ленивое вычисление ref по uuid
            def fallback():
                self.ref = api.get_by_uuid(self.uuid)
                self.db_table_name = ""
            if self.db_table_name:
                try:
                    self.ref = self.db.table(self.db_table_name).get(self.uuid).pluck('ref').run()['ref']
                except r.ReqlNonExistenceError as e:
                    if not self.FAIL_ON_NON_EXISTENCE:
                        fallback()
                    else:
                        raise e
                if not self.ref:
                    fallback()
            else:
                self.ref = api.get_by_uuid(self.uuid)
            return self.ref
        if self.GraphQLType: #возьми из базы
            if name in self.GraphQLType._meta.fields:
                return self.db.table(self.db_table_name).get(self.uuid).pluck(name).run()[name]






        if name.startswith('async_'):
            async_method = getattr(self.xen.api, 'Async')
            api = getattr(async_method, self.api_class)
            name = name[6:]


        if name[0] == '_':
            name=name[1:]
        attr = getattr(api, name)
        def method (*args, **kwargs):
            try:
                ret =  attr(self.ref, *args, **kwargs)
                if isinstance(ret, dict):
                    ret = dict_deep_convert(ret)

                return ret
            except XenAPI.Failure as f:
                raise XenAdapterAPIError(self.log, "Failed to execute {0}::{1}".format(self.api_class, name), f.details)
        return method


class GAccessEntry(graphene.ObjectType):
    access = graphene.List(graphene.String, required=True)
    userid = graphene.String(required=True)

class GAclXenObject(GXenObject):
    access = graphene.List(GAccessEntry, required=True)



class ACLXenObject(XenObject):
    VMEMPEROR_ACCESS_PREFIX = 'vm-data/vmemperor/access'

    def get_access_path(self, username=None, is_group=False):
        '''
        used by manage_actions' default implementation
        :param username:
        :param is_group:
        :return:
        '''
        return f'{self.access_prefix}/{self.auth.class_name()}/{"groups" if is_group else "users"}/{username}'

    ALLOW_EMPTY_XENSTORE = False # Empty xenstore for some objects might treat them as for-all-by-default

    @classmethod
    def resolve_all(cls):
        '''
        Resolves all objects belonging to a user
        :param cls:
        :return:
        '''

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

            auth = info.context.user_authenticator
            if isinstance(auth, AdministratorAuthenticator):  # return all
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
            return [cls.GraphQLType(**record) for record in records]

        return resolver
    @classmethod
    def process_record(cls, auth, ref, record):
        '''
        Adds an 'access' field to processed record containing access rights
        :param auth:
        :param ref:
        :param record:
        :return:
        '''
        new_rec = super().process_record(auth, ref, record)
        new_rec['access'] = cls.get_access_data(record, auth.__name__)
        return new_rec

    @classmethod
    def get_access_data(cls, record, authenticator_name) -> List[Dict]:
        '''
        Obtain access data
        :param record:
        :param authenticator_name:
        :return:
        '''
        xenstore = record['xenstore_data']
        def read_xenstore_access_rights(xenstore_data):
            filtered_iterator = filter(
                lambda keyvalue: keyvalue[1] and keyvalue[0].startswith(cls.VMEMPEROR_ACCESS_PREFIX),
                xenstore_data.items())

            for k, v in filtered_iterator:
                key_components = k[len(cls.VMEMPEROR_ACCESS_PREFIX) + 1:].split('/')
                if key_components[0] == authenticator_name:
                    yield {'userid': f'{key_components[1]}/{key_components[2]}', 'access': v.split(';')}

            else:
                if cls.ALLOW_EMPTY_XENSTORE:
                    yield {'userid': 'any', 'access': ['all']}

        return list(read_xenstore_access_rights(xenstore))
    @use_logger
    def check_access(self,  action):
        '''
        Check if it's possible to do 'action' with specified Xen Object
        :param action: action to perform. If action is None, check for the fact that user can view this Xen object
        for 'Xen object'  these are

        - launch: can start/stop vm
        - destroy: can destroy vm
        - attach: can attach/detach disk/network interfaces
        :return: True if access granted, False if access denied, None if no info

        Implementation details:
        looks for self.db_table_name and then in db to table $(self.db_table_name)_access
        '''
        if issubclass(self.auth.__class__, AdministratorAuthenticator):
            return True # admin can do it all

        self.log.info(
            f"Checking {self.__class__.__name__} {self.uuid} rights for user {self.auth.get_id()}: action {action}")
        from rethinkdb.errors import ReqlNonExistenceError

        db = self.auth.xen.db
        try:
            access_info = db.table(self.db_table_name).get(self.uuid).pluck('access').run()
        except ReqlNonExistenceError:
            access_info = None
            
        access_info = access_info['access'] if access_info else None
        if not access_info:
            if self.ALLOW_EMPTY_XENSTORE:
                    return True
            raise XenAdapterUnauthorizedActionException(self.log,
                                                        f"Unauthorized attempt "
                                                        f"on object {self} (no info on access rights) by {self.auth.get_id()}: {'requested action {action}' if action else ''}")


        username = f'users/{self.auth.get_id()}'
        groupnames = [f'groups/{group}' for group in self.auth.get_user_groups()]
        for item in access_info:
            if ((action in item['access'] or 'all' in item['access'])\
                    or (action is None and len(item['access']) > 0))and\
                    (username == item['userid'] or (item['userid'].startswith('groups/') and item['userid'] in groupnames)):
                self.log.info(
                    f'User {self.auth.get_id()} is allowed to perform action {action} on {self.__class__.__name__} {self.uuid}')
                return True



        raise XenAdapterUnauthorizedActionException(self.log,
            f"Unauthorized attempt on object {self} by {self.auth.get_id()}{': requested action {action}' if action else ''}")


    def manage_actions(self, action,  revoke=False, user=None, group=None):
        '''
        Changes action list for a Xen object
        :param action:
        :param revoke:
        :param user: User ID as returned from authenticator.get_id()
        :param group:
        :param force: Change actionlist even if user do not have sufficient permissions. Used by CreateVM
        :return: False if failed
        '''

        if all((user,group)) or not any((user, group)):
            raise XenAdapterArgumentError(self.log, 'Specify user or group for XenObject::manage_actions')


        if user:
            real_name = self.get_access_path(user, False)
        elif group:
            real_name = self.get_access_path(group, True)



        xenstore_data = self.get_xenstore_data()
        if real_name in xenstore_data:
            actionlist = xenstore_data[real_name].split(';')
        else:
            actionlist = []

        if revoke and action == 'all':
            for name in xenstore_data:
                if name == real_name:
                    continue

                actionlist = xenstore_data[real_name].split(';')
                if 'all' in actionlist:
                    break
            else:
                raise XenAdapterArgumentError('I cannot revoke "all" from {0} because there are no other admins of the resource'.format(real_name))


        if revoke:
            if action in actionlist:
                actionlist.remove(action)
        else:
            if action not in actionlist:
                actionlist.append(action)

        actions = ';'.join(actionlist)

        xenstore_data[real_name] = actions

        self.set_xenstore_data(xenstore_data)


