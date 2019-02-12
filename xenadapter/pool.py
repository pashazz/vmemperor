import graphene

from handlers.graphql.graphql_handler import ContextProtocol
from handlers.graphql.resolvers.sr import srType, resolve_sr
from handlers.graphql.types.gxenobjecttype import GXenObjectType
from handlers.graphql.resolvers.host import hostType, resolve_host
from rethinkdb_helper import CHECK_ER
from .xenobject import XenObject, GXenObject
import json
from json import JSONDecodeError

class GPool(GXenObjectType):
    class Meta:
        interfaces = (GXenObject,)
    master = graphene.Field(hostType, description="Pool master",
                            resolver=lambda *args, **kwargs: resolve_host(field_name='master', *args, **kwargs), required=True)
    default_SR = graphene.Field(srType, description="Default SR", resolver=resolve_sr)


class Pool (XenObject):
    db_table_name = 'pools'
    api_class = 'pool'
    EVENT_CLASSES = ['pool']
    quotas_table_name = 'quotas'
    GraphQLType = GPool

    @classmethod
    def create_db(cls, db, indexes=None):
        '''
        This implementation creates a DB for quotas and then runs parent implementation
        The quotas table has the following document structure:
        {
        "userid": "users/1" (user id/ group id with user/group mark)
        "storage": 9007199254740992 (How many storage bytes this user is allowed to have)
        }
        :param db:
        :param indexes:
        :return:
        '''

        if not cls.db:
            table_list = db.table_list().run()
            if cls.quotas_table_name not in table_list:
                db.table_create(cls.quotas_table_name, durability='soft', primary_key='userid').run()

        super().create_db(db, indexes)



    @classmethod
    def process_event(cls, auth, event, db, authenticator_name):
        '''
        Calls parent implementation and then inserts JSON documents from Pool's
        other_config field named vmemperor_quotas_$authenticator_name
        Reads fields with JSON.reads

        :param auth:
        :param event:
        :param db:
        :param authenticator_name:
        :return:
        '''
        super().process_event(auth, event, db, authenticator_name)

        if 'snapshot' not in event:
            return
        field_name = f'vmemperor_quotas_{authenticator_name}'
        record =  event['snapshot']
        if field_name not in record['other_config']:
            return

        json_string = record['other_config'][field_name]
        try:
            json_doc = json.loads(json_string)
        except JSONDecodeError as e:
            auth.log.error(f"Error while loading JSON quota info for {authenticator_name}: {e}")
            return
        for doc in json_doc:
            if 'userid' not in doc:
                auth.log.error(f"Malformed JSON quota document in {field_name}: {doc}")
                return


        CHECK_ER(db.table(cls.quotas_table_name).insert(json_doc, conflict='update').run())

    def __init__(self, auth):
        records = Pool.get_all(auth)
        assert len(records) == 1
        super().__init__(auth, ref=records[0])







