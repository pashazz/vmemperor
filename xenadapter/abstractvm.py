from .xenobject import ACLXenObject


class AbstractVM(ACLXenObject):
    api_class = 'VM'

    def insert_log_entry(self, *args, **kwargs):
        self.auth.xen.insert_log_entry(self.uuid, *args, **kwargs)

