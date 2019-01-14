from .xenobject import XenObject


class Host(XenObject):
    db_table_name = 'hosts'
    api_class = 'host'
    EVENT_CLASSES = ['host']
    #PROCESS_KEYS = ['name_label', 'name_description', 'uuid', 'master']

    @classmethod
    def process_event(cls, auth, event, db, authenticator_name):
        super().process_event(auth, event, db, authenticator_name)


