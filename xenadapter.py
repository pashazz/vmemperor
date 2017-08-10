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
        return self.get_all_records(self.api.pool)

    def list_vms(self):
        return [vm for vm in self.get_all_records(self.api.VM)
                if not vm['is_a_template'] and not vm['is_control_domain']]


    def list_vdis(self):
        return self.get_all_records(self.api.VDI)

    def list_networks(self):
        return self.get_all_records(self.api.network)

    def list_templates(self):
          return [record for record in self.get_all_records(self.api.VM)
                  if record['is_a_template']]

    def create_vdi(self, sr_ref, name_label = None, name_description = None):
        self.api.VDI.create(self.session, sr = sr_ref, name_label = name_label, name_description = name_description)

        return

    def create_network(self):
        self.api.network.create(self.session)

        return

    def create_vm(self, tmpl_uuid, sr_uuid, net_uuid, vdi_size, name_label = ''):
        try:
            tmpl_ref = self.api.VM.get_by_uuid(tmpl_uuid)
            new_vm_ref = self.api.VM.clone(tmpl_ref, name_label)
        except XenAPI.Failure as f:
            print ("XenAPI Error failed to clone template: %s" % f.details)

        try:
            specs = provision.getProvisionSpec(self.session, new_vm_ref)
            specs.setSR(sr_uuid)
            provision.setProvisionSpec(self.session, new_vm_ref, specs)
        except:
            print("Error provision")

        new_vm_uuid = self.api.VM.get_uuid(new_vm_ref)
        try:
            self.api.VM.provision(new_vm_ref)
        except Exception as e:
            print("XenAPI failed to finish creation:", str(e))

        self.start_stop_vm(new_vm_ref, True)

        # self.connect_vm(new_vm_ref, net_uuid)

        return

    def create_vbd(self, vdi_ref):
        self.api.VBD.create(self.session, VM = self.vm_ref, VDI = vdi_ref)

        return

    def start_stop_vm(self, vm_ref, enable):
        if enable:
            self.api.VM.start (vm_ref, False, True)
        else:
            self.api.VM.shutdown(vm_ref)

        return

    def connect_vm(self, vm_ref, net_uuid):
        net_ref = self.api.network.get_by_uuid(net_uuid)
        net = self.api.network.get_record(net_ref)
        args = {'VM': vm_ref, 'network': net_ref, 'device': '0',\
                'MAC': '', 'MTU': net['MTU'], 'other_config': {}, \
                'qos_algorithm_type': '', 'qos_algorithm_params': {}}
        try:
            vif_ref = self.api.VIF.create(args)
            self.api.VIF.plug(vif_ref)
        except Exception as e:
            print("XenAPI failed to create VIF: %s", str(e))
            sys.exit(1)

        return

    def enable_disable_template(self):

        return

    def get_vnc(self):

        return

    def attach_vbd(self):
        self.api.VBD.plug()

        return

    def detach_vbd(self):
        self.api.VBD.unplug()

        return


    def destroy_vbd(self, vbd_uuid = None, vbd_ref = None):
        if (vbd_ref == None):
            if (vbd_uuid == None):
                raise ValueError("No vbd to destroy")
            vbd_ref = self.api.VBD.get_by_uuid(vbd_uuid)
        self.api.VBD.destroy(vbd_ref)

        return

    def destroy_vm(self, vm_uuid):
        try:
            vm_ref = self.api.VM.get_by_uuid(vm_uuid)
            vm = self.api.VM.get_record(vm_ref)

            # no need
            # vbds = vm['VBDs']
            #
            # for vbd_ref in vbds:
            #     self.destroy_vbd(vbd_ref = vbd_ref)
            # vifs = vm['VIFs']
            # for vif_ref in vifs:
            #
            #     self.api.VIF.destroy(vif_ref)
            # need ?????

            self.api.VM.destroy(vm_ref)
        except Exception as e:
            print ("XenAPI Error failed to destroy vm: %s" % str(e))

            sys.exit(1)

        return

    def destroy_vdi(self, vdi_ref):
        self.api.VDI.destroy(vdi_ref)

        return
