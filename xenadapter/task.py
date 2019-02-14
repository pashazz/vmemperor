from xenadapter import XenAdapter, XenAdapterPool
from .xenobject import ACLXenObject, GAclXenObject
from handlers.graphql.types.gxenobjecttype import GXenObjectType
import graphene
from tornado.options import options as opts

class GTask(GXenObjectType):
    class Meta:
        interfaces = (GAclXenObject,)

    created = graphene.Field(graphene.DateTime, required=True, description="Task creation time")
    finished = graphene.Field(graphene.DateTime, required=True, description="Task finish time")
    progress = graphene.Field(graphene.Float, required=True, description="Task progress")
    result = graphene.Field(graphene.ID, description="Task result if available")
    type = graphene.Field(graphene.String, description="Task result type")
    resident_on = graphene.Field(graphene.ID, description="ref of a host that runs this task")
    error_info = graphene.Field(graphene.List(graphene.String), description="Error strings, if failed")
    status = graphene.Field(graphene.String, description="Task status")


class Task(ACLXenObject):
    api_class = 'task'
    EVENT_CLASSES = ['task']
    db_table_name = 'tasks'
    GraphQLType = GTask
    
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
                #CHECK_ER(db.table(cls.db_table_name).get_all(event['ref'], index='ref').delete().run())
                return

            record = event['snapshot']
            if not cls.filter_record(record):
                return

            if event['operation'] in ('mod', 'add'):
                new_rec = cls.process_record(auth, event['ref'], record)
                CHECK_ER(db.table(cls.db_table_name).insert(new_rec, conflict='update').run())
                if record['status'] in ['success', 'failure', 'cancelled'] and new_rec['access']: # only our tasks have non-empty 'access'
                    if not hasattr(auth, 'xen'):
                        auth.log.warning("Creating a XenAdaptor when it's likely should be provided")
                        auth.xen = XenAdapterPool().get()
                    auth.xen.api.task.destroy(event['ref'])
                    if not hasattr(auth, 'xen'):
                        XenAdapterPool().unget(auth.xen)


        
