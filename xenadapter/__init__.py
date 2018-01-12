import XenAPI
from loggable import Loggable
from .singleton import Singleton
from exc import *
import logging
import rethinkdb as r


def use_logger(method):
    def decorator(self, *args, **kwargs):
        oldFormatter = self.xen.fileHandler.formatter
        self.xen.fileHandler.setFormatter(
            logging.Formatter(
                "%(levelname)-10s [%(asctime)s] (type: {0}; uuid: {1}) : %(message)s".format(self.__class__.__name__,
                                                                                             self.uuid))
        )
        ret = method(self, *args, **kwargs)
        self.xen.fileHandler.setFormatter(oldFormatter)
        return ret

    return decorator




class XenAdapter(Loggable, metaclass=Singleton):
    AUTOINSTALL_PREFIX = '/autoinstall'
    VMEMPEROR_ACCESS_PREFIX='vm-data/vmemperor/access'

    from .vm import VM
    from .template import Template


    def __init__(self, settings):
        """creates session connection to XenAPI. Connects using admin login/password from settings
        :param authenticator: authorized authenticator object
    """

        #if isinstance(authenticator, tuple):
#            settings['username'] = authenticator[0]
#            settings['password'] = authenticator[1]
#            self.vmemperor_user = authenticator[0]
#        else:
#            try:
#                self.vmemperor_user = authenticator.get_id()
#            except:
#                self.vmemperor_user = 'root'



 #       self.authenticator = authenticator
        if 'debug' in settings:
               self.debug = bool(settings['debug'])

        self.init_log()



        try:
            url = settings['url']
            username = settings['username']
            password = settings['password']
        except KeyError as e:
            raise XenAdapterArgumentError(self.log, 'Failed to parse settings: {0}'.format(str(e)))

        try:
            self.session = XenAPI.Session(url)
            self.session.xenapi.login_with_password(username, password)
            self.log.info ('Authentication is successful. XenAdapter object created')
            self.api = self.session.xenapi
        except OSError as e:
            raise XenAdapterConnectionError(self.log, "Unable to reach XenServer at {0}: {1}".format(url, str(e)))
        except XenAPI.Failure as e:
            raise XenAdapterConnectionError(self.log, 'Failed to login: url: "{1}"; username: "{2}"; password: "{3}"; error: {0}'.format(str(e), url, username, password))


        self.conn = r.connect(settings['host'], settings['port'], db=settings['database']).repl()
        if not settings['database'] in r.db_list().run():
            r.db_create('vmemperor').run()

        self.db  = r.db(settings['database'])

        if  'vm_logs' not in self.db.table_list().run():
            self.db.table_create('vm_logs', durability='soft').run()
            self.db.table('vm_logs').index_create('uuid').run()
            self.db.table('vm_logs').index_wait('uuid').run()

        self.table = self.db.table('vm_logs')





    def get_all_records(self, subject) -> dict :
        """
        return get_all_records call in a dict format without opaque object references
        :param subject: XenAPI subject (VM, VDI, etc)
        :return: dict in format : { uuid : dict of object fields }
        """
        return {item['uuid'] : item for item in subject.get_all_records().values()}

    def uuid_by_name(self, subject,  name) -> str:
        """
        Obtain uuid by human readable name
        :param subject: Xen API subject
        :param name: name_label
        :return: uuid (str) or empty string if no object with that name
        """
        try:
            return next((key for key, value in self.get_all_records(subject).items()
                     if value['name_label'] == name))
        except StopIteration:
            return ""


    assets = [VM, Template]


    def access_list(self, authenticator_name) -> list:
        from .xenobject import ACLXenObject
        def read_xenstore_access_rights(xenstore_data : dict, asset : ACLXenObject):
            filtered_iterator = filter(lambda keyvalue : keyvalue[1] and  keyvalue[0].startswith(self.VMEMPEROR_ACCESS_PREFIX),
                                       xenstore_data.items())

            for k, v in filtered_iterator:
                key_components= k[len(self.VMEMPEROR_ACCESS_PREFIX) + 1:].split('/')
                if key_components[0] == authenticator_name:

                    yield {'userid' :  '%s/%s' % (key_components[1], key_components[2]), 'access' : v}

            else:
                if asset.ALLOW_EMPTY_XENSTORE:
                    yield  {'userid' : 'any', 'access' : 'all'}

        # Repeat procedure for VM objects and VDI objects
        final_list = []
        for asset in self.assets:

            recs = asset.get_all_records(self)
            result_dict = {}
            for k,v in recs.items():
                xenstore_data = v['xenstore_data']
                for d in read_xenstore_access_rights(xenstore_data, asset):
                    if d['userid'] in result_dict:
                        result_dict[d['userid']].append({'uuid' : v['uuid'], 'access' : d['access']})
                    else:
                        result_dict[d['userid']] = [{'uuid' : v['uuid'], 'access' : d['access']}]


            print(asset.api_class)
            final_list.extend([{'userid' : k, 'type' : asset.api_class, 'items' : v} for k, v in result_dict.items()])
        return final_list


    def insert_log_entry(self, uuid, state, message):

        #r.now() is rethink-compatible datetime.datetime.now()
        self.table.insert(dict(uuid=uuid, state=state, message=message, time=r.now()), durability='soft').run(self.conn)






    def enable_disable_template(self, vm_uuid, enable):
        """
        Adds/removes tag vmemperor"
        :param vm_uuid:
        :param enable:
        :return: dict, code_status
        """
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        try:
            if enable:
                self.api.VM.add_tags(vm_ref, 'vmemperor_enabled')
                self.log.info ("Enable template UUID {0}".format(vm_uuid))
            else:
                self.api.VM.remove_tags(vm_ref, 'vmemperor_enabled')
                self.log.info ("Disable template UUID {0}".format(vm_uuid))
        except XenAPI.Failure as f:
            raise XenAdapterAPIError (self, "Failed to enable/disable template: {0}".format(f.details))



    def get_vnc(self, vm_uuid) -> str:
        """
        Get VNC Console
        :param vm_uuid: VM UUID
        :return: URL console location
        """
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        self.start_stop_vm(True)
        consoles = self.api.VM.get_consoles(vm_ref) #references
        if (len(consoles) == 0):
            self.log.error('Failed to find console of VM UUID {0}'.format(vm_uuid))
            return ""
        try:
            cons_ref = consoles[0]
            console = self.api.console.get_record(cons_ref)
            url = self.api.console.get_location(cons_ref)
            self.log.info ("Console location {0} of VM UUID {1}".format(url, vm_uuid))
        except XenAPI.Failure as f:
            raise XenAdapterAPIError(self, "Failed to get console location: {0}".format(f.details))

        return url







    def hard_shutdown(self, vm_uuid):
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        if self.api.VM.get_power_state(vm_ref) != 'Halted':
            self.api.VM.hard_shutdown(vm_ref)


    def set_other_config(self, subject, uuid, name, value=None, overwrite=True):
        '''
        Set value of other_config field
        :param subject: API subject
        :param uuid:
        :param name:
        :param value: none if you wish to remove field
        :return:
        '''
        ref = subject.get_by_uuid(uuid)
        if value is not None:
            if overwrite:
                try:
                    subject.remove_from_other_config(ref, name)
                except XenAPI.Failure as f:
                    self.log.debug("set_other_config: failed to remove entry %s from other_config (overwrite=True): %s" % (name, f.details))
            try:
                subject.add_to_other_config(ref, name, value)
            except XenAPI.Failure as f:
                raise XenAdapterAPIError(self, "Failed to add tag '{0}' with value '{1}' to subject '{2}'s other_config field {3}': {4}".format(
                    name, value, subject, uuid, f.details))
        else:
            try:
                subject.remove_from_other_config(ref, name, value)
            except XenAPI.Failure as f:
                raise XenAdapterAPIError(self,
                                         "Failed to remove tag '{0}' from subject '{1}'s other_config field {2}': {3}".format(
                                             name, subject, uuid, f.details))


