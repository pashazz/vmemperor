from .abstractvm import AbstractVM
from . import use_logger
import XenAPI
from authentication import BasicAuthenticator
import provision
import pprint

from .os import *


class VM (AbstractVM):

    db_table_name = 'vms'

    def __init__(self, auth, uuid=None, ref=None):
        super().__init__(auth, uuid, ref)

    @classmethod
    def process_event(cls,  auth, event, db, authenticator_name):

        from vmemperor import CHECK_ER

        if event['class'] != 'vm':
            raise XenAdapterArgumentError(auth.xen.log, "this method accepts only 'vm' events")

        if event['operation'] == 'del':
            CHECK_ER(db.table('vms').get(event['ref']).delete().run())
            return

        record = event['snapshot']
        if not cls.filter_record(record):
            return
        try:
            if event['operation'] in ('mod', 'add'):
                new_rec = cls.process_record(auth, record)
                new_rec['ref'] = event['ref']
                CHECK_ER(db.table('vms').insert(new_rec, conflict='update').run())

        except XenAPI.Failure as f:
            if f.details == ["EVENTS_LOST"]:
                auth.xen.log.warning("VM: Reregistering for events")
                auth.xen.api.event.register(["*"])


    @classmethod
    def process_xenstore(cls, xenstore, authenticator_name):

        def read_xenstore_access_rights(xenstore_data):
            filtered_iterator = filter(
                lambda keyvalue: keyvalue[1] and keyvalue[0].startswith(cls.VMEMPEROR_ACCESS_PREFIX),
                xenstore_data.items())

            for k, v in filtered_iterator:
                key_components = k[len(cls.VMEMPEROR_ACCESS_PREFIX) + 1:].split('/')
                if key_components[0] == authenticator_name:
                    yield {'userid': '%s/%s' % (key_components[1], key_components[2]), 'access': v.split(';')}

            else:
                if cls.ALLOW_EMPTY_XENSTORE:
                    yield {'userid': 'any', 'access': ['all']}

        return list(read_xenstore_access_rights(xenstore))


    @classmethod
    def filter_record(cls, record):
        return not (record['is_a_template'] or record['is_control_domain'])

    @classmethod
    def process_record(cls, auth,  record):
        '''
        Creates a (shortened) dict record from long XenServer record. If no record could be created, return false
        :param record:
        :return:
        '''
        if not cls.filter_record(record):
            return False
        keys = ['power_state', 'name_label', 'uuid']
        new_rec = {k: v for k, v in record.items() if k in keys}
        new_rec['access'] = cls.process_xenstore(record['xenstore_data'], auth.__name__)
        new_rec['network'] = []
        for vif in record['VIFs']:
            net_ref = auth.xen.api.VIF.get_network(vif)
            new_rec['network'].append(net_ref)

        new_rec['disks'] = []
        for vbd in record['VBDs']:
            vdi_ref = auth.xen.api.VBD.get_VDI(vbd)
            try:
                new_rec['disks'].append(vdi_ref)
            except XenAPI.Failure as f:
                if f.details[1] != 'VDI':
                    raise f
        return new_rec

    @classmethod
    def create(self, auth, new_vm_ref, sr_ref, net_ref, vdi_size, ram_size, hostname, mode, os_kind=None, ip=None, install_url=None, scenario_url=None, name_label = '', start=True, override_pv_args=None):
        '''
        Creates a virtual machine and installs an OS

        :param new_vm_ref: Cloned template ref (use clone_templ)
        :param sr_ref: Storage Repository ref
        :param net_ref: Network ref
        :param vdi_size: Size of disk
        :param hostname: Host name
        :param os_kind: OS kind (used for automatic installation. Default: manual installation)
        :param ip: IP configuration. Default: auto configuration. Otherwise expects a tuple of the following format
        (ip, mask, gateway, dns1(optional), dns2(optional))
        :param install_url: URL to install OS from
        :scenario_url: preseed/kickstart file url. It's Preseed for debian-based systems, Kickstart for RedHat. If os_kind is ubuntu and scenario_url is kickstart, provide a tuple (url, 'ks')
        :param mode: 'pv' or 'hvm'. Refer to http://xapi-project.github.io/xen-api/vm-lifecycle
        :param name_label: Name for created VM
        :param start: if True, start VM immediately
        :param override_pv_args: if specified, overrides all pv_args for Linux kernel
        :return: VM ref
        '''
        #new_vm_ref = self.clone_tmpl(tmpl_ref, name_label, os_kind)

        vm = VM(auth, ref=new_vm_ref)
        vm.install = True
        if isinstance(auth, BasicAuthenticator):
            vm.manage_actions('all',  user=auth.get_id())

        vm.set_ram_size(ram_size)
        vm.set_disks(sr_uuid, vdi_size)





        #self.connect_vm(new_vm_uuid, net_uuid, ip)
        vm.convert('pv')

        try:
            from .network import Network
            net = Network(auth, uuid=net_uuid)
        except XenAdapterAPIError as e:
            auth.xen.insert_log_entry(new_vm_uuid, state="failed", message="Failed to connect VM to a network: %s" % e.message )
            return

        net.attach(vm)
        #self.convert_vm(new_vm_uuid, 'pv')

        vm.os_detect(os_kind, ip, hostname, scenario_url, override_pv_args)
        vm.os_install(install_url)
        vm.convert(mode)
        #self.convert_vm(new_vm_uuid, mode)
        #self.start_stop_vm(new_vm_uuid, start)

        del vm.install
        #subscribe to changefeed

        return vm

    @use_logger
    def set_ram_size(self,  mbs):
        try:
            bs = str(1048576 * int(mbs))
            #vm_ref = self.api.VM.get_by_uuid(vm_uuid)
            self.set_memory(bs)
        except Exception as e:
            #self.destroy_vm(vm_uuid, force=True)
            try:
                raise e
            except XenAPI.Failure as f:
                self.insert_log_entry('failed', 'Failed to assign %s Mb of memory: %s' % (self.uuid, f.details))
                raise XenAdapterAPIError(self.log, "Failed to set ram size: {0}".format(f.details))




    @use_logger
    def set_disks(self, sr_uuid, sizes):
        if type(sizes) != list:
            sizes = [sizes]
        for size in sizes:
            try:

                specs = provision.ProvisionSpec()
                size = str(1048576 * int(size))
                specs.disks.append(provision.Disk('0', size, sr_uuid, True))
                provision.setProvisionSpec(self.auth.xen.session, self.ref, specs)
            except Exception as e:
                try:
                    raise e
                except XenAPI.Failure as f:
                    self.insert_log_entry('failed', 'Failed to assign provision specification: %s' % f.details)
                    raise XenAdapterAPIError(self.log, "Failed to set disk: {0}".format(f.details))
                finally:
                    pass
                    #self.destroy_vm(vm_uuid, force=True)


        try:
            self.provision()
        except Exception as e:

            try:
                raise e
            except XenAPI.Failure as f:
                self.insert_log_entry('failed', 'Failed to perform provision: %s' % f.details)
                raise XenAdapterAPIError(self.log, "Failed to provision: {0}".format(f.details))
            finally:
                pass
                #self.destroy_vm(vm_uuid, force=True)
        else:
            self.insert_log_entry('provisioned',str(specs))


    @use_logger
    def os_detect(self, os_kind, ip, hostname, scenario_url, override_pv_args):
        '''
        call only during install
        :param os_kind:
        :param ip:
        :param hostname:
        :param scenario_url:
        :param override_pv_args:
        :return:
        '''
        #vm_ref = self.api.VM.get_by_uuid(vm_uuid)

        if not hasattr(self, 'install'):
            raise RuntimeError("Not an installation process")
        os = None
        if 'ubuntu' in os_kind:
            os = UbuntuOS()
        if 'debian' in os_kind:
            os = DebianOS()

        if os:
            try:
                debian_release = os.get_release(os_kind.split()[1])
            except IndexError:
                debian_release = None
            if debian_release:
                config = self.get_other_config()
                config['debian-release'] = debian_release
                self.set_other_config(config)

        if 'centos' in os_kind:
            os = CentOS()

        if os:
            if ip:
                os.set_network_parameters(*ip)
            else:
                os.set_network_parameters()

            os.set_hostname(hostname)
            os.set_scenario(scenario_url)

            if not override_pv_args:
                pv_args = os.pv_args()
            else:
                pv_args = override_pv_args
            self.set_PV_args(pv_args)

    @use_logger
    def os_install(self,  install_url):
        '''
        call only during install
        :param install_url:
        :return:
        '''
        if not hasattr(self, 'install'):
            raise RuntimeError("Not an installation process")
        message = 'Installing OS'
        if install_url:
            config = self.get_other_config()
            config['install-repository'] = install_url
            config['default-mirror'] = install_url
            self.set_other_config( config)
            self.log.info("Adding Installation URL: %s" % install_url)
            message += ' from URL: %s' % install_url

        self.insert_log_entry('installing', message)


        try:
            self.start(False, True)
        except Exception as e:
            try:
                raise e
            except XenAPI.Failure as f:
                self.insert_log_entry('failed', 'Failed to start OS installation:  %s' % f.details)


    def convert(self,  mode):
        """
        convert vm from/to hvm
        :param vm_uuid:
        :param mode: pv/hvm
        :return:
        """

        hvm_boot_policy = self.get_HVM_boot_policy()
        if hvm_boot_policy and mode == 'pv':
            self.set_HVM_boot_policy('')
        if hvm_boot_policy == '' and mode == 'hvm':
            self.set_HVM_boot_policy('BIOS order')



    @use_logger
    def start_stop_vm(self, enable):

        """
        Starts and stops VM if required
        :param enable: True = start; False = stop
        :return:
        """
        try:
            ps = self.get_power_state()
            if ps != 'Running' and enable:
                self.start( False, True)
                self.log.info("Started".format(self.uuid))
            if ps == 'Running' and not enable:
                self.shutdown()
                self.xen.log.info("Shutted down".format(self.uuid))
        except XenAPI.Failure as f:
            raise XenAdapterAPIError(self.log, "Failed to start/stop VM: {0}".format(f.details))

    @use_logger
    def get_vnc(self):
        self.start_stop_vm(True)
        consoles = self.get_consoles()  # references
        if (len(consoles) == 0):
            self.log.error('Failed to find console')
            return
        try:
            cons_ref = consoles[0]
            console = self.xen.api.console.get_record(cons_ref)
            url = self.xen.api.console.get_location(cons_ref)
            self.xen.log.info("Console location: {0}".format(url))
        except XenAPI.Failure as f:
            raise XenAdapterAPIError(self.log, "Failed to get console location: {0}".format(f.details))

        return url

    @use_logger
    def destroy_vm(self):
        from .disk import VBD

        self.start_stop_vm(False)

        vbds = self.get_VBDs()
        vdis = [VBD(self.auth, ref=vbd_ref).get_VDI() for vbd_ref in vbds]

        try:
            self.destroy()
            for vdi_ref in vdis:
                self.xen.api.VDI.destroy(vdi_ref) #????
        except XenAPI.Failure as f:
            raise XenAdapterAPIError(self.log, "Failed to destroy VM: {0}".format(f.details))

        return

    @use_logger
    def destroy_disk(self, vdi_uuid):
        vdi_ref = self.api.VDI.get_by_uuid(vdi_uuid)
        try:
            self.api.VDI.destroy(vdi_ref)
        except XenAPI.Failure as f:

            raise XenAdapterAPIError(self, "Failed to destroy VDI: {0}".format(f.details))

        return

