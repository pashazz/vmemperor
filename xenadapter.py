import XenAPI
import json
import hooks
import provision


import sys

class XenAdapter:


    def get_all_records(self, subject):
        """
        return get_all_records call in a dict format without opaque object references
        :param subject: XenAPI subject (VM, VDI, etc)
        :return:
        """
        return list(subject.get_all_records().values())


    def uuid_by_name(self, subject,  name):
        """
        Obtain uuid by human readable name
        :param subject: Xen API subject
        :param name: name_label
        :return: uuid (str) or empty string if no object with that name
        """
        try:
            return next((i['uuid'] for i in self.get_all_records(subject)
                     if i['name_label'] == name))
        except StopIteration:
            return ""

    def __init__(self, settings):
        """creates session connection to XenAPI. Connects using admin login/password from settings"""
        try:
            url = settings['url']
            login = settings['login']
            password = settings['password']
        except KeyError:
            raise ValueError('Error login session')

        self.session = XenAPI.Session(url)
        self.session.xenapi.login_with_password(login, password)
        self.api = self.session.xenapi
        return

    def list_pools(self):
        '''
        :return: list of pool records
        '''
        return self.get_all_records(self.api.pool)

    def list_vms(self):
        '''
        :return: list of vm records except dom0 and templates
        '''
        return [vm for vm in self.get_all_records(self.api.VM)
                if not vm['is_a_template'] and not vm['is_control_domain']]

    def list_srs(self):
        '''
        :return: list of storage repositories' records
        '''
        return self.get_all_records(self.api.SR)


    def list_vdis(self):
        '''
        :return: list of virtual disk images' records
        '''
        return self.get_all_records(self.api.VDI)

    def list_networks(self):
        '''
        list of network interfaces' records
        :return:
        '''
        return self.get_all_records(self.api.network)

    def list_templates(self):
        '''
        list of VM templates' records
        :return:
        '''
        return [record for record in self.get_all_records(self.api.VM)
                  if record['is_a_template']]

    def create_vm(self, tmpl_uuid, sr_uuid, net_uuid, vdi_size, name_label = ''):
        '''
        Creates a virtual machine and install an OS
        :param tmpl_uuid:
        :param sr_uuid:
        :param net_uuid:
        :param vdi_size:
        :param name_label:
        :return:
        '''
        try:
            tmpl_ref = self.api.VM.get_by_uuid(tmpl_uuid)
            new_vm_ref = self.api.VM.clone(tmpl_ref, name_label)
        except Exception as e:
            print ("XenAPI Error failed to clone template:", str(e))

        try:
            specs = provision.ProvisionSpec()
            specs.disks.append(provision.Disk("0", vdi_size, sr_uuid, True))
            provision.setProvisionSpec(self.session, new_vm_ref, specs)
        except Exception as e:
            print("Error provision:", str(e))
            sys.exit(1)

        new_vm_uuid = self.api.VM.get_uuid(new_vm_ref)
        try:
            self.api.VM.provision(new_vm_ref)
        except Exception as e:
            print("XenAPI failed to finish creation:", str(e))
            sys.exit(1)

        self.connect_vm(new_vm_uuid, net_uuid)

        self.api.VM.start(new_vm_ref, False, True) # args: VM reference, start in paused state, force start

        return new_vm_uuid

    def create_disk(self, sr_uuid, size, name_label = None):
        sr_ref = self.api.SR.get_by_uuid(sr_uuid)
        if not (name_label):
            sr = self.api.SR.get_record(sr_ref)
            name_label = sr['name_label'] + ' disk'

        args = {'SR': sr_ref, 'virtual_size': str(size), 'type': 'system', \
                'sharable': False, 'read_only': False, 'other_config': {}, \
                'name_label': name_label}
        try:
            vdi_ref = self.api.VDI.create(args)
        except Exception as e:
            print("Failed to create VDI:", str(e))
            sys.exit(1)
        vdi_uuid = self.api.VDI.get_uuid(vdi_ref)

        return vdi_uuid

    def create_network(self, name_label = None):
        """

        :param name_label:
        :return:
        """
        # todo какие тут должны быть аргументы, это работает, но что-то маловато требуется
        if not(name_label):
            records = self.api.network.get_all_records()
            name_label = 'network_' + str(len(records))
        args = {'other_config': {}, 'name_label': name_label}
        net_ref = self.api.network.create(args)
        net_uuid = self.api.network.get_uuid(net_ref)

        return net_uuid

    def start_stop_vm(self, vm_uuid, enable):
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        vm = self.api.VM.get_record(vm_ref)
        if vm['power_state'] != 'Running' and enable == True:
            self.api.VM.start (vm_ref, False, True)
        if vm['power_state'] == 'Running' and enable == False:
            self.api.VM.shutdown(vm_ref)

        return

    def connect_vm(self, vm_uuid, net_uuid):
        net_ref = self.api.network.get_by_uuid(net_uuid)
        net = self.api.network.get_record(net_ref)
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        args = {'VM': vm_ref, 'network': net_ref, 'device': '0',\
                'MAC': '', 'MTU': net['MTU'], 'other_config': {}, \
                'qos_algorithm_type': '', 'qos_algorithm_params': {}}
        try:
            vif_ref = self.api.VIF.create(args)
        except Exception as e:
            print("XenAPI failed to create VIF:", str(e))
            sys.exit(1)

        return

    def enable_disable_template(self, vm_uuid, enable):
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        try:
            if enable:
                self.api.VM.add_tags(vm_ref, 'vmemperor_old_ver')
            else:
                self.api.VM.remove_tags(vm_ref, 'vmemperor_old_ver')
            return {'status': 'success', 'details': 'template modified', 'reason': ''}, 200
        except XenAPI.Failure as e:
            return {'status': 'error', 'details': 'can not modify template', 'reason': e.details}, 409
        except Exception as e:
            return {'status': 'error', 'details': 'can not modify template', 'reason': str(e)}, 500


        return

    def get_power_state(self, vm_uuid):
        '''
        Returns a power state of the VM
        :param vm_uuid: VM UUID
        :return: VM State string
        '''
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        return self.api.VM.get_power_state(vm_ref)


    def get_vnc(self, vm_uuid):
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        if (self.api.VM.get_power_state(vm_ref) != 'Running'):
            self.start_stop_vm(vm_uuid, True)
        consoles = self.api.VM.get_consoles(vm_ref) #references
        if (len(consoles) == 0):
            print('Failed to find console')
        else:
            cons_ref = consoles[0]
            console = self.api.console.get_record(cons_ref)
            url = self.api.console.get_location(cons_ref)
        return url

    def attach_disk(self, vm_uuid, vdi_uuid):
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
                    return vbd_uuid

        args = {'VM': vm_ref, 'VDI': vdi_ref, 'userdevice': str(len(vm['VBDs'])), 'bootable': True, \
                'mode': 'RW', 'type': 'Disk', 'empty': False, 'other_config': {}, \
                'qos_algorithm_type': '', 'qos_algorithm_params': {}}
        vbd_ref = self.api.VBD.create(args)
        vbd_uuid = self.api.VBD.get_uuid(vbd_ref)
        if (self.api.VM.get_power_state(vm_ref) == 'Running'):
            try:
                self.api.VBD.plug(vbd_ref)
            except XenAPI.Failure as f:
                if f.details[0] == 'VM_MISSING_PV_DRIVERS':
                    print("Please reboot")
                else:
                    raise f

        return vbd_uuid

    def detach_disk(self, vbd_uuid):
        '''
        Detach a VBD object while trying to eject it if the machine is running
        :param vbd_uuid: virtual block device UUID to detach
        :return:
        '''
        vbd_ref = self.api.VBD.get_by_uuid(vbd_uuid)
        self.api.VBD.destroy(vbd_ref)
        return

    def destroy_vm(self, vm_uuid):
        try:
            vm_ref = self.api.VM.get_by_uuid(vm_uuid)
            vm = self.api.VM.get_record(vm_ref)

            vbds = vm['VBDs']
            vdis = [self.api.VBD.get_record(vbd_ref)['VDI'] for vbd_ref in vbds]

            self.api.VM.destroy(vm_ref)
            for vdi_ref in vdis:
                self.api.VDI.destroy(vdi_ref)
        except Exception as e:
            print ("XenAPI Error failed to destroy vm:", str(e))

            sys.exit(1)

        return

    def destroy_disk(self, vdi_uuid):
        vdi_ref = self.api.VDI.get_by_uuid(vdi_uuid)
        self.api.VDI.destroy(vdi_ref)

        return

    def hard_shutdown(self, vm_uuid):
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        if self.api.VM.get_power_state(vm_ref) != 'Halted':
            self.api.VM.hard_shutdown(vm_ref)