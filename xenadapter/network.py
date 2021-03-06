from handlers.graphql.resolvers.vm import resolve_vms, vmType
from .xenobject import *
from xenadapter.helpers import use_logger


class VIF(XenObject, metaclass=XenObjectMeta):
    api_class = 'VIF'
    EVENT_CLASSES = ['vif']
    PROCESS_KEYS = ['uuid', 'currently_attached', 'network', 'status_detail']
    @classmethod
    def create(cls, auth, *args, **kwargs):
        attr = cls.__class__.__getattr__(cls, 'create')
        return VIF(auth, ref=attr(auth, *args, **kwargs))

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
        from rethinkdb_tools.helper import CHECK_ER
        from .vm import VM
        cls.create_db(db)

        if event['class'] in cls.EVENT_CLASSES:
            if event['operation'] == 'del':
                # Find VIF REF on RethinkDB server (fast)
                try:
                    arr = db.table(VM.db_table_name).coerce_to('array').filter(lambda vm: vm['interfaces'].values().get_field('VIF').contains(event['ref'])).run()
                    doc = arr[0]
                except:
                    return

                for k,v in doc['interfaces'].items():
                    if 'VIF' in v and v['VIF'] == event['ref']:
                        del doc['interfaces'][k]
                        break

                CHECK_ER(db.table(VM.db_table_name).insert(doc, conflict='replace').run())
                return

            record = event['snapshot']


            if event['operation'] in ('mod', 'add'):
                vm = VM(auth=auth, ref=record['VM'])
                if vm.get_is_a_snapshot():
                    return #TODO Handle snapshots

                new_rec = {'uuid': vm.uuid, 'interfaces' : {record['device']:
                {'VIF':event['ref'], 'network': record['network'], 'attached': record['currently_attached'], 'MAC': record['MAC'], 'status': record['status_detail']}} }
                CHECK_ER(db.table(VM.db_table_name).insert(new_rec, conflict='update').run())




class GNetwork(GXenObjectType):
    class Meta:
        interfaces = (GAclXenObject,)

    VMs = graphene.List(vmType, resolver=resolve_vms)
    other_config = graphene.JSONString()

class Network(ACLXenObject):
    from .vm import VM
    api_class = "network"
    db_table_name = 'nets'
    EVENT_CLASSES = ['network']
    GraphQLType = GNetwork

    def __init__(self, auth, uuid=None, ref=None):
        super().__init__(auth, uuid=uuid, ref=ref)

    @use_logger
    def attach(self, vm: VM, sync=False) -> VIF:
        args = {'VM': vm.ref, 'network': self.ref , 'device': str(len(vm.get_VIFs())),
                'MAC': '', 'MTU': self.get_MTU() , 'other_config': {},
                'qos_algorithm_type': '', 'qos_algorithm_params': {}}
        try:
            if sync:
                return VIF.create(self.auth, args)
            else:
                return VIF.async_create(self.auth, args)
        except XenAPI.Failure as f:
            raise XenAdapterAPIError(self.auth.xen.log, "Network::attach: Failed to create VIF",f.details)


    @use_logger
    def detach(self, vm: VM):
        for ref in vm.get_VIFs():
            vif = VIF(self.auth, ref=ref)
            if vif.get_network() == self.ref:
                try:
                    return vif.async_destroy()
                except XenAPI.Failure as f:
                    raise XenAdapterAPIError(self.log, "Network::detach: Failed to detach VIF", f.details)
                break
        else:
            self.log.warning(f"Not attached to {vm}")
            return None


    @classmethod
    def filter_record(cls, record):
        return True
        #return record['bridge'] != 'xenapi'



    @classmethod
    def process_record(cls, auth, ref, record):
        '''
        Process as regular object, but replace VIFs with corresponding VMs
        :param auth:
        :param event:
        :param db:
        :param authenticator_name:
        :return:
        '''
        new_rec = super().process_record(auth, ref,record)
        if not new_rec:
            return


        def vif_to_vm_ref(vif_ref):
            vif = VIF(auth=auth, ref=vif_ref)
            return vif.get_VM()

        new_rec['VMs'] = [vif_to_vm_ref(vif_ref) for vif_ref in record['VIFs']]


        return new_rec


