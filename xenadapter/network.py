from .xenobject import *
from . import use_logger

class VIF(XenObject, metaclass=XenObjectMeta):
    api_class = 'VIF'
    EVENT_CLASSES = ['vif']
    PROCESS_KEYS = ['uuid', 'currently_attached', 'network', 'status_detail']
    @classmethod
    def create(cls, auth, *args, **kwargs):
        attr = cls.__class__.__getattr__(cls, 'create')
        return VIF(auth, ref=attr(auth.xen, *args, **kwargs))

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
        from vmemperor import CHECK_ER
        from .vm import VM
        from .network import Network
        cls.create_db(db)

        if event['class'] in cls.EVENT_CLASSES:
            if event['operation'] == 'del':
                #handled by VM
                return

            record = event['snapshot']


            if event['operation'] in ('mod', 'add'):
                vm = VM(auth=auth, ref=record['VM'])
                net = Network(auth=auth, ref=record['network'])
                new_rec = {'uuid': vm.uuid, 'networks' : {record['device']:
                {'VIF': record['uuid'], 'network': net.uuid, 'attached': record['currently_attached'], 'MAC': record['MAC'], 'status': record['status_detail']}} }
                CHECK_ER(db.table(vm.db_table_name).insert(new_rec, conflict='update').run())





class Network(ACLXenObject):
    from .vm import VM
    api_class = "network"
    db_table_name = 'nets'
    EVENT_CLASSES = ['network']
    PROCESS_KEYS =  ['name_label', 'name_description', 'PIFs', 'VIFs', 'uuid', 'ref', 'other_config']

    def __init__(self, auth, uuid=None, ref=None):
        super().__init__(auth, uuid=uuid, ref=ref)

    @use_logger
    def attach(self, vm: VM) -> VIF:
        self.check_access('attach')

        args = {'VM': vm.ref, 'network': self.ref , 'device': str(len(vm.get_VIFs())),
                'MAC': '', 'MTU': self.get_MTU() , 'other_config': {},
                'qos_algorithm_type': '', 'qos_algorithm_params': {}}
        try:

            vif = VIF.create(self.auth, args)
            #vif_uuid = self.auth.xen.api.VIF.get_uuid(vif_ref)

            self.log.info("VM is connected to network: VIF UUID {0}".format(vif.uuid))
        except XenAdapterAPIError as f:
            raise XenAdapterAPIError(self.auth.xen.log, "Failed to create VIF: {0}".format(f.details))

        return vif

    @classmethod
    def filter_record(cls, record):
        return record['bridge'] != 'xenapi'

    @classmethod
    def get_access_data(cls, record, authenticator_name):
        '''
        Obtain access data
        :param record:
        :param authenticator_name:
        :return:
        '''
        other_config = record['other_config']
        def read_other_config_access_rights(other_config):
            from json import JSONDecodeError
            if 'vmemperor' in other_config:
                try:
                    emperor = json.loads(other_config['vmemperor'])
                except JSONDecodeError:
                    emperor = {}

                if 'access' in emperor:
                    if authenticator_name in emperor['access']:
                        auth_dict = emperor['access'][authenticator_name]
                        for k,v in auth_dict.items():
                            yield {'userid': k, 'access': v}
                        else:
                            if cls.ALLOW_EMPTY_XENSTORE:
                                yield {'userid': 'any', 'access': ['all']}

        return list(read_other_config_access_rights(other_config))



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
        from json import JSONDecodeError
        if all((user,group)) or not any((user, group)):
            raise XenAdapterArgumentError(self.log, 'Specify user OR group for Network::manage_actions')




        if user:
            real_name = 'users/' + user
        elif group:
            real_name = 'groups/' + group





        other_config = self.get_other_config()
        auth_name = self.auth.class_name()
        if 'vmemperor' not in other_config:
            emperor = {'access': {auth_name : {}}}
        else:

            try:
                emperor = json.loads(other_config['vmemperor'])
            except JSONDecodeError:
                emperor = {'access': {auth_name: {}}}


        if auth_name in emperor['access']:
            auth_list = emperor['access'][auth_name]
        else:
            auth_list = []
            emperor['access'][auth_name] = {}


        if real_name in auth_list and isinstance(auth_list[real_name], list) and action != 'all':
            action_list = auth_list[real_name]
        else:
            action_list = []


        if revoke:
            if action in action_list:
                action_list.remove(action)
        else:
            if action not in action_list:
                action_list.append(action)

        if action_list:
            emperor['access'][auth_name][real_name] = action_list
        else:
            del emperor['access'][auth_name][real_name]

        if not emperor['access'][auth_name]:
            del emperor['access'][auth_name]


        other_config['vmemperor'] = json.dumps(emperor)
        self.set_other_config(other_config)






