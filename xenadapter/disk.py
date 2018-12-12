import graphene

from handlers.graphql.resolvers.sr import resolve_sr, srType
from handlers.graphql.resolvers.vm import resolve_vms, vmType
from xenadapter.sr import SR
from xenadapter.vbd import VBD
from xenadapter.xenobject import GXenObject
from .xenobject import *
from xenadapter.helpers import use_logger
from exc import *
import XenAPI


class Attachable:
    import xenadapter.vm
    @use_logger
    def _attach(self : XenObject, vm: xenadapter.vm.VM, type : str, mode: str, empty=False) -> str:
        '''
        Attach self (XenObject - either ISO or Disk) to vm VM with disk type type
        :param vm:VM to attach to
        :param mode: 'RO'/'RW'
        :param type: 'CD'/'Disk'/'Floppy'
        :return: VBD UUID
        '''
        #vm.check_access('attach') #done by vmemperor

        vm_vbds = vm.get_VBDs()
        my_vbds = self.get_VBDs()

        userdevice_max = -1
        for vm_vbd in vm_vbds:
            for vdi_vbd in my_vbds:
                if vm_vbd == vdi_vbd:
                    vbd_uuid = self.auth.xen.api.VBD.get_uuid(vm_vbd)
                    self.log.warning (f"Disk is already attached with VBD UUID {vbd_uuid}")
                    return vbd_uuid
            try:
                userdevice = int(self.auth.xen.api.VBD.get_userdevice(vm_vbd))
            except ValueError:
                userdevice = -1

            if userdevice_max < userdevice:
                userdevice_max = userdevice

        userdevice_max += 1

        args = {'VM': vm.ref, 'VDI': self.ref,
                'userdevice': str(userdevice_max),
        'bootable' : True, 'mode' :mode, 'type' : type, 'empty' : empty,
        'other_config' : {},'qos_algorithm_type': '', 'qos_algorithm_params': {}}

        try:
            vbd_ref = self.auth.xen.api.VBD.create(args)
        except XenAPI.Failure as f:
            raise XenAdapterAPIError(self.auth.xen.log, "Failed to create VBD", f.details)

        vbd_uuid = self.auth.xen.api.VBD.get_uuid(vbd_ref)
        if (vm.get_power_state() == 'Running'):
            try:
                self.auth.xen.api.VBD.plug(vbd_ref)
            except Exception as e:
                self.auth.xen.log.warning(f"Disk will be attached after reboot with VBD UUID {vbd_uuid}")
                return vbd_uuid

        self.auth.xen.log.info (f"Disk is attached with VBD UUID: {vbd_uuid}")

        return vbd_uuid

    @use_logger
    def _detach(self : XenObject, vm):
        #vm.check_access('attach') #done by vmemperor
        vbds = vm.get_VBDs()
        for vbd_ref in vbds:

            vdi = self.auth.xen.api.VBD.get_VDI(vbd_ref)
            if vdi == self.ref:
                vbd_uuid = self.auth.xen.api.VBD.get_uuid(vbd_ref)
                break
        else:
            vbd_uuid = None
        if not vbd_uuid:
            raise XenAdapterAPIError(self.log, "Failed to detach disk: Disk isn't attached")

        vbd = VBD(auth=self.auth, uuid=vbd_uuid)

        if vm.get_power_state() == 'Running':
            try:
                vbd.unplug()
            except Exception as e:
                self.log.warning("Failed to detach disk from running VM")
                return

        try:
            vbd.destroy()
            self.log.info("VBD UUID {0} is destroyed".format(vbd_uuid))
        except XenAPI.Failure as f:
            raise XenAdapterAPIError(self.log, "Failed to detach disk: {0}".format(f.details))



    @classmethod
    def get_vbd_vms(self, record, auth):

        def vbd_to_vm_ref(vbd_ref):
            from .vbd import VBD

            vbd = VBD(auth=auth, ref=vbd_ref)
            return vbd.get_VM()

        return [vbd_to_vm_ref(ref) for ref in record['VBDs']]

class DiskImage(GXenObject):
    SR = graphene.Field(srType, resolver=resolve_sr)
    VMs = graphene.List(vmType)
    virtual_size = graphene.Field(graphene.Float, required=True)

class GISO(GXenObjectType):
    class Meta:
        interfaces = (GAclXenObject, DiskImage)

    from handlers.graphql.resolvers.vm import resolve_vms
    VMs = graphene.Field(graphene.List(vmType), resolver=resolve_vms)
    location = graphene.Field(graphene.String, required=True)


class ISO(XenObject, Attachable):
    api_class = 'VDI'
    db_table_name = 'isos'
    EVENT_CLASSES = ['vdi']
    #PROCESS_KEYS = ['uuid', 'name_label', 'name_description', 'location', 'virtual_size', 'physical_utilization']
    GraphQLType = GISO

    from .vm import VM

    @classmethod
    def filter_record(cls, record, return_SR_record=False):
        query = cls.db.table(SR.db_table_name).get_all(record['SR'], index='ref').run()
        if len(query.items) != 1:
            raise XenAdapterAPIError("Unable to get SR for ISO {0}".format(record['uuid']),
                                     "No such SR: {0}".format(record['SR']))
        if return_SR_record:
            return query.items[0]['content_type'] == 'iso', query.items[0]
        else:
            return query.items[0]['content_type'] == 'iso'


    @classmethod
    def process_event(cls, auth, event, db, authenticator_name):
        cls.create_db(db)

        if event['class'] == 'vdi': #get SR
            if event['operation'] in ('add', 'mod'):
                record = event['snapshot']

                filtered, SR = cls.filter_record(record, return_SR_record=True)
                if not filtered:
                    return

                new_rec = cls.process_record(auth, event['ref'], record)
                # We need SR information
                new_rec['SR'] = SR['uuid']
                new_rec['VMs'] = Attachable.get_vbd_vms(record, auth)

                from rethinkdb_helper import CHECK_ER
                CHECK_ER(db.table(cls.db_table_name).insert(new_rec, conflict='update').run())



    def attach(self, vm : VM) -> VBD:
        '''
        Attaches VDI to a vm as RW
        :param vm:
        WARNING: It does not check whether self is a real ISO, do it for yourself.

        '''
        return VBD(auth=self.auth, uuid=self._attach(vm, 'CD', 'RO'))

    def detach(self, vm: VM):
        self._detach(vm)


class GVDI(GXenObjectType):
    class Meta:
        interfaces = (GAclXenObject, DiskImage)
    VMs = graphene.Field(graphene.List(vmType), resolver=resolve_vms)



class VDI(ACLXenObject, Attachable):
    api_class = 'VDI'
    db_table_name = 'vdis'
    EVENT_CLASSES = ['vdi']
    GraphQLType = GVDI

    @classmethod
    def create(cls, auth, sr_uuid, size, name_label = None):
        """
        Creates a VDI of a certain size in storage repository
        :param sr_uuid: Storage Repository UUID
        :param size: Disk size
        :param name_label: Name of created disk
        :return: Virtual Disk Image object
        """
        sr_ref = auth.xen.api.SR.get_by_uuid(sr_uuid)
        if not (name_label):
            sr = auth.xen.api.SR.get_record(sr_ref)
            name_label = sr['name_label'] + ' disk'

        other_config = {}
        if auth.get_id():
            other_config['vmemperor_user'] = auth.get_id()

        args = {'SR': sr_ref, 'virtual_size': str(size), 'type': 'system', \
                'sharable': False, 'read_only': False, 'other_config': other_config, \
                'name_label': name_label}
        try:
            vdi_ref = auth.xen.api.VDI.create(args)
            vdi_uuid = auth.xen.api.VDI.get_uuid(vdi_ref)
            auth.log.info("VDI is created: UUID {0}".format(vdi_uuid))
        except XenAPI.Failure as f:
            raise XenAdapterAPIError(auth.log, "Failed to create VDI: {0}".format(f.details))

        return vdi_uuid

    @classmethod
    def filter_record(cls, record, return_SR_record=False):
        query = cls.db.table(SR.db_table_name).get_all(record['SR'], index='ref').run()
        if len(query.items) != 1:
            raise XenAdapterAPIError("Unable to get SR for ISO {0}".format(record['uuid']),
                                     "No such SR: {0}".format(record['SR']))
        if return_SR_record:
            return query.items[0]['content_type'] != 'iso', query.items[0]
        else:
            return query.items[0]['content_type'] != 'iso'

    @classmethod
    def process_event(cls, auth, event, db, authenticator_name):

        if event['class'] == 'vdi':
            cls.create_db(db)
            if event['operation'] in ('add', 'mod'):
                record = event['snapshot']

                filtered, SR = cls.filter_record(record, return_SR_record=True)
                if not filtered:
                    return

                # get access information
                new_rec = cls.process_record(auth, event['ref'], record)
                new_rec['SR'] = SR['uuid']
                new_rec['VMs'] = Attachable.get_vbd_vms(record, auth)

                from rethinkdb_helper import CHECK_ER
                CHECK_ER(db.table(cls.db_table_name).insert(new_rec, conflict='update').run())


    def destroy(self):
        sr = SR(auth=self.auth, ref=self.get_SR())
        if 'vdi_destroy' in sr.get_allowed_operations():
            self._destroy()
            return True
        else:
            return False


    def attach(self, vm) -> VBD:
        '''
        Attaches ISO to a vm
        :param vm:
        :return:
        '''
        return VBD(auth=self.auth, uuid=self._attach(vm, 'Disk', 'RW'))

    def detach(self, vm):
        self._detach(vm)


class VDIorISO:
    def __new__(cls, auth, uuid=None, ref=None):
        db = auth.xen.db

        if uuid:
            if db.table(ISO.db_table_name).get(uuid).run():
                return ISO(auth, uuid, ref)
            elif db.table(VDI.db_table_name).get(uuid).run():
                return VDI(auth, uuid, ref)
            else:
                return None
        elif ref:
            if len(db.table(ISO.db_table_name).get_all(ref, index='ref').run().items) == 1:
                return ISO(auth, uuid, ref)
            elif len(db.table(VDI.db_table_name).get_all(ref, index='ref').run().items) == 1:
                return VDI(auth, uuid, ref)
            else:
                return None


