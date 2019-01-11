import XenAPI
from loggable import Loggable
from .singleton import Singleton
from exc import *
import threading
from rethinkdb import RethinkDB
r = RethinkDB()




class XenAdapter(Loggable, metaclass=Singleton):
    AUTOINSTALL_PREFIX = '/autoinstall'
    VMEMPEROR_ACCESS_PREFIX='vm-data/vmemperor/access'



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
            self.log.info ('Authentication is successful. XenAdapter object created in thread {0}'.format(threading.get_ident()))
            self.api = self.session.xenapi
        except OSError as e:
            raise XenAdapterConnectionError(self.log, "Unable to reach XenServer at {0}: {1}".format(url, str(e)))
        except XenAPI.Failure as e:
            raise XenAdapterConnectionError(self.log, 'Failed to login: url: "{1}"; username: "{2}"; password: "{3}"; error: {0}'.format(str(e), url, username, password))


        self.conn = r.connect(settings['host'], settings['port'], db=settings['database']).repl()
        if not settings['database'] in r.db_list().run():
            r.db_create(settings['database']).run()

        self.db  = r.db(settings['database'])
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



    log_entry_init = False
    def insert_log_entry(self, uuid, state, message):

        if not self.log_entry_init:
            if 'vm_logs' not in self.db.table_list().run():
                self.db.table_create('vm_logs').run()

            self.log_entry_init = True


        self.table.wait().run()
        #r.now() is rethink-compatible datetime.datetime.now()
        self.table.insert(dict(uuid=uuid, state=state, message=message, time=r.now()), durability='soft').run()






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


class XenAdapterPool(metaclass=Singleton):
    def __init__(self, qty=200):
        self._xens = []
        self.qty = qty
    def get(self):
        if len(self._xens) == self.qty:
            #waiting for lock to be unlocked in at least one XenAdapter
           for xen in self._xens:
               if not xen.session.locked:
                   return xen
        else:
            from vmemperor import opts
            self._xens.append(XenAdapter({**opts.group_dict('xenadapter'), **opts.group_dict('rethinkdb')}, nosingleton=True))
            return self._xens[-1]

        #TODO dont know what to do if limit exceeded

