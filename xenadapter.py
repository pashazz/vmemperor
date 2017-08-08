import XenAPI
import json
import hooks
import provision


class XenAdapter:

    def __init__(self, settings):
        """creates session connection to XenAPI. Connects using admin login/password from settings"""

        url = settings['url']
        login = settings['login']
        password = settings['password']

        self.session = XenAPI.Session(url)
        self.session.xenapi.login_with_password(login, password)
        self.api = self.session.xenapi
        return

    def list_pools(self):

        return

    def list_vms(self):
        all_vms = XenAPI.VM.get_all(self.session)['Value']

        return all_vms

    def list_vdis(self):
        all_vdis = XenAPI.VDI.get_all(self.session)['Value']

        return all_vdis

    def create_vdi(self, sr_ref, name_label = None, name_description = None):
        XenAPI.VDI.create(self.session, sr = sr_ref, name_label = name_label, name_description = name_description)

        return

    def list_networks(self):

        return

    def create_network(self):
        XenAPI.network.create(self.session)

        return

    def create_vm(self, t_ref, name_label, sr):
        new_vm_ref = XenAPI.VM.clone(self.session, t_ref, name_label)

        # other_config = XenAPI.VM.get_other_config(self.session, self.vm_ref)
        # other_config['disks'].sr = sr
        # XenAPI.VM.set_other_config(self.session, self.vm_ref, other_config)
        # XenAPI.VM.provision(self.session, self.vm_ref)

        specs = provision.getProvisionSpec(self.session, new_vm_ref)
        specs.setSR(sr)
        provision.setProvisionSpec(self.session, new_vm_ref, specs)

        return

    def start_stop_vm(self, vm_ref, enable):
        if enable:
            self.api.VM.start (vm_ref)
        else:
            self.api.VM.shutdown(vm_ref)

        return

    def get_vnc(self):

        return

    def create_vbd(self, vdi_ref):
        XenAPI.VBD.create(self.session, VM = self.vm_ref, VDI = vdi_ref)

        return

    def attach_vbd(self):
        XenAPI.VBD.plug()

        return

    def detach_vbd(self):
        XenAPI.VBD.unplug()

        return

    def destroy_vbd(self, vbd_ref):
        XenAPI.VBD.destroy(vbd_ref)

        return

    def destroy_vm(self):

        return

    def destroy_vdi(self, vdi_ref):
        XenAPI.VDI.destroy(vdi_ref)

        return

    def connect_vm(self, network):
        XenAPI.VIF.create(self.session, VM = self.vm_ref, network = network)
        XenAPI.VIF.plug()

        return

    def list_templates(self):
        list = []
        records = XenAPI.VM.get_all_records(self.session)
        for record in records:
            if record['is_a_template'] == True:
                list.append(record)

        return list

    def enable_disable_template(self):

        return