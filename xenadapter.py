import XenAPI
import json
import hooks
import provision

import logging
import sys

#do the same for all the modules


class XenAdapter:

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

    def __init__(self, settings):
        """creates session connection to XenAPI. Connects using admin login/password from settings"""

        self.log = logging.getLogger(__class__.__name__)
        self.log.setLevel(logging.DEBUG)

        fileHandler = logging.FileHandler("{0}.log".format(__class__.__name__))
        formatter = logging.Formatter("(levelname)-8s [%(asctime)s] %(message)s")
        fileHandler.setLevel(logging.DEBUG)
        fileHandler.setFormatter(formatter)
        self.log.addHandler(fileHandler)
        if 'debug' in settings:
            debugHandler = logging.StreamHandler()
            debugHandler.setLevel(logging.ERROR)
            self.log.addHandler(debugHandler)
            self.log.error("Running in debug mode: all errors are in stderr, for further info check log file")

        try:
            url = settings['url']
            login = settings['login']
            password = settings['password']
        except Exception as e:
            self.log.error('Failed to parse settings: {0}'.format(str(e)))
            sys.exit(1)

        try:
            self.session = XenAPI.Session(url)
            self.session.xenapi.login_with_password(login, password)
            self.log.info ('Authentication is successful')
            self.api = self.session.xenapi
        except Exception as e:
            self.log.error('Failed to login: url: "{1}"; login: "{2}"; password: "{3}"; error: {0}'.format(str(e), url, login, password))
            sys.exit(1)

        return

    def list_pools(self) -> dict:
        '''
        :return: dict of pool records
        '''
        return self.get_all_records(self.api.pool)

    def list_vms(self) -> dict:
        '''
        :return: dict of vm records except dom0 and templates
        '''
        return {key : value for key, value in self.get_all_records(self.api.VM).items()
                if not value['is_a_template'] and not value['is_control_domain']}

    def list_srs(self) -> dict:
        '''
        :return: dict of storage repositories' records
        '''
        return self.get_all_records(self.api.SR)


    def list_vdis(self) -> dict:
        '''
        :return: dict of virtual disk images' records
        '''
        return self.get_all_records(self.api.VDI)

    def list_networks(self) -> dict:
        '''
        dict of network interfaces' records
        :return:
        '''
        return self.get_all_records(self.api.network)

    def list_templates(self) -> dict:
        '''
        dict of VM templates' records
        :return:
        '''
        return {key : value for key, value in self.get_all_records(self.api.VM).items()
                  if value['is_a_template']}

    def create_vm(self, tmpl_uuid, sr_uuid, net_uuid, vdi_size, name_label = '', start=True) -> str:
        '''
        Creates a virtual machine and installs an OS
        :param tmpl_uuid: Template UUID
        :param sr_uuid: Storage Repository UUID
        :param net_uuid: Network UUID
        :param vdi_size: Size of disk
        :param name_label: Name for created VM
        :return: VM UUID
        '''
        try:
            tmpl_ref = self.api.VM.get_by_uuid(tmpl_uuid)
            new_vm_ref = self.api.VM.clone(tmpl_ref, name_label)
            new_vm_uuid = self.api.VM.get_uuid(new_vm_ref)
            self.log.info ("New VM is created: UUID {0}".format(new_vm_uuid))
        except Exception as e:
            self.log.error ("Failed to clone template: {0}".format(str(e)))
            sys.exit(1)

        try:
            specs = provision.ProvisionSpec()
            specs.disks.append(provision.Disk("0", vdi_size, sr_uuid, True))
            provision.setProvisionSpec(self.session, new_vm_ref, specs)
        except Exception as e:
            self.log.error("Failed to setting disk: {0}".format(str(e)))
            self.destroy_vm(new_vm_uuid)
            sys.exit(1)

        try:
            self.api.VM.provision(new_vm_ref)
        except Exception as e:
            self.log.error("Failed to provision: {0}".format(str(e)))
            self.destroy_vm(new_vm_uuid)
            sys.exit(1)

        self.connect_vm(new_vm_uuid, net_uuid)

        if start:
            self.api.VM.start(new_vm_ref, False, True) # args: VM reference, start in paused state, force start
            self.log.info ("Created VM is started")
        else:
            self.log.warning('Created VM is off')

        return new_vm_uuid


    def create_disk(self, sr_uuid, size, name_label = None) -> str:
        """
        Creates a VDI of a certain size in storage repository
        :param sr_uuid: Storage Repository UUID
        :param size: Disk size
        :param name_label: Name of created disk
        :return: Virtual Disk Interface UUID
        """

        sr_ref = self.api.SR.get_by_uuid(sr_uuid)
        if not (name_label):
            sr = self.api.SR.get_record(sr_ref)
            name_label = sr['name_label'] + ' disk'

        args = {'SR': sr_ref, 'virtual_size': str(size), 'type': 'system', \
                'sharable': False, 'read_only': False, 'other_config': {}, \
                'name_label': name_label}
        try:
            vdi_ref = self.api.VDI.create(args)
            vdi_uuid = self.api.VDI.get_uuid(vdi_ref)
            self.log.info ("VDI is created: UUID {0}".format(vdi_uuid))
        except Exception as e:
            self.log.error("Failed to create VDI: {0}".format(str(e)))
            sys.exit(1)

        return vdi_uuid

    def start_stop_vm(self, vm_uuid, enable):
        """
        Starts and stops VM if required
        :param vm_uuid:
        :param enable:
        :return:
        """
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        vm = self.api.VM.get_record(vm_ref)
        try:
            if vm['power_state'] != 'Running' and enable == True:
                self.api.VM.start (vm_ref, False, True)
                self.log.info ("Started VM UUID {0}".format(vm_uuid))
            if vm['power_state'] == 'Running' and enable == False:
                self.api.VM.shutdown(vm_ref)
                self.log.info("Shutted down VM UUID {0}".format(vm_uuid))
        except Exception as e:
            self.log.error ("Failed to start/stop VM: {0}".format(str(e)))

        return

    def connect_vm(self, vm_uuid, net_uuid):
        """
        Creates VIF to connect VM to network
        :param vm_uuid:
        :param net_uuid:
        :return: vif_uuid
        """
        net_ref = self.api.network.get_by_uuid(net_uuid)
        net = self.api.network.get_record(net_ref)
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        vm = self.api.VM.get_record(vm_ref)
        args = {'VM': vm_ref, 'network': net_ref, 'device': str(len(vm['VIFs'])), \
                'MAC': '', 'MTU': net['MTU'], 'other_config': {}, \
                'qos_algorithm_type': '', 'qos_algorithm_params': {}}
        try:
            vif_ref = self.api.VIF.create(args)
            vif_uuid = self.api.VIF.get_uuid(vif_ref)
            self.log.info ("VM is connected to network: VIF UUID {0}".format(vif_uuid))
        except Exception as e:
            self.log.error("Failed to create VIF: {0}".format(str(e)))
            return

        return vif_uuid

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
        except Exception as e:
            self.log.error ("Failed to enable/disable template: {0}".format(str(e)))

    def get_power_state(self, vm_uuid) -> str:
        '''
        Returns a power state of the VM
        :param vm_uuid: VM UUID
        :return: VM State string
        '''
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        return self.api.VM.get_power_state(vm_ref)


    def get_vnc(self, vm_uuid) -> str:
        """
        Get VNC Console
        :param vm_uuid: VM UUID
        :return: URL console location
        """
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        self.start_stop_vm(vm_uuid, True)
        consoles = self.api.VM.get_consoles(vm_ref) #references
        if (len(consoles) == 0):
            self.log.error('Failed to find console of VM UUID {0}'.format(vm_uuid))
            return
        try:
            cons_ref = consoles[0]
            console = self.api.console.get_record(cons_ref)
            url = self.api.console.get_location(cons_ref)
            self.log.info ("Console location {0} of VM UUID {1}".format(url, vm_uuid))
        except Exception as e:
            self.log.error("Failed to get console location: {0}".format(str(e)))
            sys.exit(1)
        return url

    def attach_disk(self, vm_uuid, vdi_uuid) -> str:
        '''
        Attach a VDI object to a VM by creating a VBD object and attempting to hotplug it if the machine is running        if VM is running
        :param vm_uuid: VM UUID
        :param vdi_uuid: virtual disk image UUID
        :return: Virtual block device UUID
        '''
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        vm = self.api.VM.get_record(vm_ref)
        vdi_ref = self.api.VDI.get_by_uuid(vdi_uuid)
        vdi = self.api.VDI.get_record(vdi_ref)

        vm_vbds = vm['VBDs']
        vdi_vbds = vdi['VBDs']
        for vm_vbd in vm_vbds:
            for vdi_vbd in vdi_vbds:
                if vm_vbd == vdi_vbd:
                    vbd_uuid = self.api.VBD.get_uuid(vm_vbd)
                    self.log.warning ("Disk is already attached with VBD UUID {0}".format(vbd_uuid))
                    return vbd_uuid

        args = {'VM': vm_ref, 'VDI': vdi_ref, 'userdevice': str(len(vm['VBDs'])), 'bootable': True, \
                'mode': 'RW', 'type': 'Disk', 'empty': False, 'other_config': {}, \
                'qos_algorithm_type': '', 'qos_algorithm_params': {}}
        try:
            vbd_ref = self.api.VBD.create(args)
        except Exception as e:
            self.log.error("Failed to create VBD: {0}".format(str(e)))
            sys.exit(1)

        vbd_uuid = self.api.VBD.get_uuid(vbd_ref)
        if (self.api.VM.get_power_state(vm_ref) == 'Running'):
            try:
                self.api.VBD.plug(vbd_ref)
            except Exception as e:
                self.log.warning("Disk will be attached after reboot with VBD UUID {0}".format(vbd_uuid))
                return vbd_uuid

        self.log.info ("Disk is attached with VBD UUID: {0}".format(vbd_uuid))

        return vbd_uuid


    def detach_disk(self, vbd_uuid):
        '''
        Detach a VBD object while trying to eject it if the machine is running
        :param vbd_uuid: virtual block device UUID to detach
        :return:
        '''
        vbd_ref = self.api.VBD.get_by_uuid(vbd_uuid)
        vbd = self.api.VBD.get_record(vbd_ref)
        vm_ref = vbd['VM']
        if self.api.VM.get_power_state(vm_ref) == 'Running':
            try:
                self.api.VBD.unplug(vbd_ref)
            except Exception as e:
                self.log.error ("Failed to detach disk from running VM")
                return 1
            
        try:
            self.api.VBD.destroy(vbd_ref)
            self.log.info("VBD UUID {0} is destroyed".format(vbd_uuid))
        except Exception as e:
            self.log.error("Failed to detach disk: {0}".format(str(e)))
        return

    def destroy_vm(self, vm_uuid):
        self.start_stop_vm(vm_uuid, False)
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        vm = self.api.VM.get_record(vm_ref)

        vbds = vm['VBDs']
        vdis = [self.api.VBD.get_record(vbd_ref)['VDI'] for vbd_ref in vbds]

        try:
            self.api.VM.destroy(vm_ref)
            for vdi_ref in vdis:
                self.api.VDI.destroy(vdi_ref)
        except Exception as e:
            self.log.error ("Failed to destroy VM: {0}".format(str(e)))

        return

    def destroy_disk(self, vdi_uuid):
        vdi_ref = self.api.VDI.get_by_uuid(vdi_uuid)
        try:
            self.api.VDI.destroy(vdi_ref)
        except Exception as e:
            self.log.error("Failed to destroy VDI: {0}".format(str(e)))

        return

    def hard_shutdown(self, vm_uuid):
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        if self.api.VM.get_power_state(vm_ref) != 'Halted':
            self.api.VM.hard_shutdown(vm_ref)