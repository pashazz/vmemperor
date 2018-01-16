from .xenobject import *
from . import use_logger
from exc import *
import XenAPI


class VBD(XenObject):
    api_class = 'VBD'

  #  @classmethod
  #  def process_event(cls, xen, event, db):
  #      from vmemperor import CHECK_ER
  #      if event['class'] != 'vbd':
  #          raise XenAdapterArgumentError(xen.log, "this method accepts only 'vbd' events")

        #record = event['snapshot']
        #if event['operation'] == 'add':





class Attachable:
    from .vm import VM

    @use_logger
    def _attach(self : XenObject, vm: VM, type : str, mode: str, empty=False) -> str:
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

        for vm_vbd in vm_vbds:
            for vdi_vbd in my_vbds:
                if vm_vbd == vdi_vbd:
                    vbd_uuid = self.auth.xen.api.VBD.get_uuid(vm_vbd)
                    self.log.warning ("Disk is already attached with VBD UUID {0}".format(vbd_uuid))
                    return vbd_uuid

        args = {'VM': vm.ref, 'VDI': self.ref, 'userdevice': str(len(vm_vbds)),
        'bootable' : True, 'mode' :mode, 'type' : type, 'empty' : empty,
        'other_config' : {},'qos_algorithm_type': '', 'qos_algorithm_params': {}}

        try:
            vbd_ref = self.auth.xen.api.VBD.create(args)
        except XenAPI.Failure as f:
            raise XenAdapterAPIError(self.auth.xen.log, "Failed to create VBD: {0}".format(f.details))

        vbd_uuid = self.auth.xen.api.VBD.get_uuid(vbd_ref)
        if (vm.get_power_state() == 'Running'):
            try:
                self.auth.xen.api.VBD.plug(vbd_ref)
            except Exception as e:
                self.auth.xen.log.warning("Disk will be attached after reboot with VBD UUID {0}".format(vbd_uuid))
                return vbd_uuid

        self.auth.xen.log.info ("Disk is attached with VBD UUID: {0}".format(vbd_uuid))

        return vbd_uuid

    @use_logger
    def _detach(self : XenObject, vm : VM):
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
                return 1

        try:
            vbd.destroy()
            self.log.info("VBD UUID {0} is destroyed".format(vbd_uuid))
        except XenAPI.Failure as f:
            raise XenAdapterAPIError(self.log, "Failed to detach disk: {0}".format(f.details))

        return



class ISO(XenObject, Attachable):
    api_class = 'VDI'


    from .vm import VM

    @classmethod
    def get_all_records(cls, xen):
        iso_dict = {}
        for k, v in xen.api.SR.get_all_records().items():
            if 'content_type' not in v or  v['content_type'] != 'iso':
                continue


            for vdi_ref in xen.api.SR.get_VDIs(k):
                rec = xen.api.VDI.get_record(vdi_ref)
                #fields = {'uuid', 'name_label', 'name_description', 'location'}
                #rec = {key: value for key, value in rec.items() if key in fields}
                iso_dict[vdi_ref] = rec
        return iso_dict

    @classmethod
    def process_record(cls, xen, record):
        fields = {'uuid', 'name_label', 'name_description', 'location'}
        return  {key: value for key, value in record.items() if key in fields}

    def attach(self, vm : VM) -> VBD:
        '''
        Attaches ISO to a vm
        :param vm:
        :return:
        WARNING: It does not check whether self is a real ISO, do it for yourself.
        '''
        return VBD(auth=self.auth, uuid=self._attach(vm, 'CD', 'RO'))

    def detach(self, vm: VM):
        self._detach(vm)



class VDI(ACLXenObject):
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

