import XenAPI
import json
import hooks
import provision

import sys

class XenAdapter:

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

        return

    def list_vms(self):
        list = []
        records = self.api.VM.get_all_records()
        for vm in records.values():
            if vm['is_a_template'] == False and vm['is_control_domain'] == False:
                list.append(vm)

        return list

    def list_vdis(self):
        all_vdis = self.api.VDI.get_all()['Value']

        return all_vdis

    def create_vdi(self, sr_ref, name_label = None, name_description = None):
        self.api.VDI.create(self.session, sr = sr_ref, name_label = name_label, name_description = name_description)

        return

    def list_networks(self):

        return

    def create_network(self):
        self.api.network.create(self.session)

        return

    def create_vm(self, tmpl_uuid, name_label, sr_uuid):
        sr = self.api.SR.get_by_uuid(sr_uuid)
        tmpl_ref = self.api.VM.get_by_uuid(tmpl_uuid)
        new_vm_ref = self.api.VM.clone(tmpl_ref, name_label)

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
        self.api.VBD.create(self.session, VM = self.vm_ref, VDI = vdi_ref)

        return

    def attach_vbd(self):
        self.api.VBD.plug()

        return

    def detach_vbd(self):
        self.api.VBD.unplug()

        return

    def destroy_vbd(self, vbd_uuid):
        vbd_ref = self.api.VBD.get_by_uuid(vbd_uuid)
        self.api.VBD.destroy(vbd_ref)

        return

    def destroy_vm(self, vm_uuid):
        try:
            vm_ref = self.api.VM.get_by_uuid(vm_uuid)
            vm = self.api.VM.get_record(vm_ref)

            # need ???
            vbds = vm['VBDs']
            for vbd in vbds:
                self.destroy_vbd(vbd['uuid'])
            vifs = vm['VIFs']
            for vif in vifs:
                vif_ref = self.api.VIF.get_by_uuid(vif['uuid'])
                self.api.VIF.destroy(vif_ref)
            # need ?????

            self.api.VM.destroy(vm_ref)
        except XenAPI.Failure as f:
            print "XenAPI Error failed to destroy vm: %s" % f.details()
            sys.exit(1)

        return

    def destroy_vdi(self, vdi_ref):
        self.api.VDI.destroy(vdi_ref)

        return

    def connect_vm(self, network):
        self.api.VIF.create(self.session, VM = self.vm_ref, network = network)
        self.api.VIF.plug()

        return

    def list_templates(self):
        list = []
        records = self.api.VM.get_all_records()
        for record in records.values():
            if record['is_a_template'] == True:
                list.append(record)

        return list

    def enable_disable_template(self):

        return