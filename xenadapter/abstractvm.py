from .xenobject import ACLXenObject

from . import use_logger
import XenAPI
from authentication import BasicAuthenticator
import provision
from .xenobjectdict import XenObjectDict

from .os import *

class AbstractVM(ACLXenObject):
    api_class = 'VM'

    def insert_log_entry(self, *args, **kwargs):
        self.auth.xen.insert_log_entry(self.uuid, *args, **kwargs)


    @classmethod
    def update_control_domain(cls, record, db):
        '''
        Handle updates of control domain data
        :param record:
        :return:
        '''
        pass

    @classmethod
    def update_db(cls, auth, event, db, record):
        from vmemperor import CHECK_ER
        if not cls.filter_record(record):
            CHECK_ER(db.table(cls.db_table_name).get_all(event['ref'], index='ref').delete().run())
            return

        if event['operation'] in ('mod', 'add'):
            new_rec = cls.process_record(auth, event['ref'], record)
            CHECK_ER(db.table(cls.db_table_name).insert(new_rec, conflict='update').run())

    @classmethod
    def process_event(cls, auth, event, db, authenticator_name):

        from vmemperor import CHECK_ER
        from .template import Template
        from .vm import VM

        if event['class'] == 'vm':

            if event['operation'] == 'del':
                # Here we can't distinguish between tmpls and vms
                CHECK_ER(db.table('vms').get_all(event['ref'], index='ref').delete().run())
                CHECK_ER(db.table('tmpls').get_all(event['ref'], index='ref').delete().run())
                return

            record = event['snapshot']
            if record['is_a_template']:
                Template.update_db(auth, event,db, record)
            elif record['is_control_domain']:
                cls.update_control_domain(record, db)
            else:
                VM.update_db(auth, event, db, record)