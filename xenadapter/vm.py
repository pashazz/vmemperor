from .abstractvm import AbstractVM
from . import use_logger
import XenAPI
from authentication import BasicAuthenticator
import provision
from .xenobjectdict import XenObjectDict



from .os import OSChooser
from exc import *

from urllib.parse import urlencode

class VM (AbstractVM):

    db_table_name = 'vms'
    PROCESS_KEYS = ['power_state', 'name_label', 'uuid',  'metrics', 'guest_metrics', 'domain_type']

    def __init__(self, auth, uuid=None, ref=None):
        super().__init__(auth, uuid, ref)


    @classmethod
    def process_event(cls,  auth, event, db, authenticator_name):

        from vmemperor import CHECK_ER
        # patch event[snapshot] so that if it doesn't have domain_type, guess it from HVM_boot_policy
        try:
            if 'domain_type' not in event['snapshot']:
                event['snapshot']['domain_type'] = 'hvm' if 'HVM_boot_policy' in event['snapshot'] and event['snapshot']['HVM_boot_policy'] else 'pv'
        except:
            pass

        super(cls, VM).process_event(auth, event, db, authenticator_name)
        if event['class'] == 'vm':
            return # handled by supermethod
        elif event['class'] == 'vm_metrics':
            if event['operation'] == 'del':
                return #vm_metrics is removed when  VM has already been removed

            new_rec = cls.process_metrics_record(auth, event['snapshot'])
            # get VM by metrics ref
            metrics_query = db.table(cls.db_table_name).get_all(event['ref'], index='metrics')
            rec_len = len(metrics_query.run().items)
            if rec_len == 0:
                #auth.xen.log.warning("VM: Cannot find a VM for metrics {0}".format(event['ref']))
                return
            elif rec_len > 1:
                auth.xen.log.warning("VM::process_event: More than one ({1}) VM for metrics {0}: DB broken?".format(event['ref'], rec_len))
                return


            CHECK_ER(metrics_query.update(new_rec).run())

        #elif
        #else:
        #    raise XenAdapterArgumentError(auth.xen.log, "this method accepts only 'vm' and 'vm_metrics' events")






    @classmethod
    def filter_record(cls, record):
        return not (record['is_a_template'] or record['is_control_domain'])


    @classmethod
    def create_db(cls, db, indexes=None): #ignore indexes
        super(VM, cls).create_db(db, indexes=['metrics', 'guest_metrics'])

    @classmethod
    def process_record(cls, auth, ref, record):
        '''
        Creates a (shortened) dict record from long XenServer record. If no record could be created, return false
        :param record:
        :return: record for DB
        '''
        from xenadapter.network import VIF, Network
        new_rec = super().process_record(auth, ref, record)
        new_rec['networks'] = {}
        new_rec['disks'] = {}
        #for vbd in record['VBDs']:
        #    vdi_ref = auth.xen.api.VBD.get_VDI(vbd)
        #    try:
        #        vdi_uuid = auth.xen.api.VDI.get_uuid(vdi_ref)
        #        new_rec['disks'].append(vdi_uuid)
        #    except XenAPI.Failure as f:
        #        if f.details[1] != 'VDI':
        #            raise f
        return new_rec

    @classmethod
    def process_metrics_record(cls, auth, record):
        '''
        Process a record from VM_metrics. Used by init_db and process_event when
        processing a vm_metrics event
        :param auth:
        :param record:
        :return: record for DB
        '''
        # NB: ensure that keys and process_record.keys have no intersection
        keys = ['start_time', 'install_time', 'memory_actual']
        return XenObjectDict({k: v for k, v in record.items() if k in keys})


    @classmethod
    def create(cls, auth, new_vm_uuid, sr_uuid, net_uuid, vdi_size, ram_size, hostname, mode, os_kind=None, ip=None, install_url=None, name_label ='', start=True, override_pv_args=None, iso=None,
               username=None, password=None, partition=None, fullname=None):
        '''1
        Creates a virtual machine and installs an OS

        :param new_vm_uuid: Cloned template UUID (use clone_templ)
        :param sr_uuid: Storage Repository UUID
        :param net_uuid: Network UUID
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
        :param iso: ISO Image UUID. If specified, will be mounted
        :return: VM UUID
        '''
        #new_vm_uuid = self.clone_tmpl(tmpl_uuid, name_label, os_kind)

        vm = VM(auth, uuid=new_vm_uuid)
        vm.install = True
        vm.remove_tags('vmemperor')
        if isinstance(auth, BasicAuthenticator):
            vm.manage_actions('all',  user=auth.get_id())

        vm.set_ram_size(ram_size)
        vm.set_disks(sr_uuid, vdi_size)
        # After provision. manage disks actions

        if isinstance(auth, BasicAuthenticator):
            for vbd_ref in vm.get_VBDs():
                from .vbd import VBD
                from .disk import VDI

                vbd = VBD(auth=auth, ref=vbd_ref)
                if vbd.get_type() != 'Disk':
                    continue
                vdi = VDI(auth=auth, ref=vbd.get_VDI())
                vdi.manage_actions('all', user=auth.get_id())


        vm.install_guest_tools()


        #self.connect_vm(new_vm_uuid, net_uuid, ip)
        if mode == 'pv':
            vm.convert('pv')


        if net_uuid:
            try:
                from .network import Network
                net = Network(auth, uuid=net_uuid)
            except XenAdapterAPIError as e:
                auth.xen.insert_log_entry(new_vm_uuid, state="failed", message="Failed to connect VM to a network: %s" % e.message )
                return

            net.attach(vm)
        else:
            if os_kind:
                auth.xen.log.warning("os_kind specified as {0}, but no network specified. The OS won't install".format(os_kind))


        if os_kind:
            vm.os_detect(os_kind, ip, hostname, install_url, override_pv_args, fullname, username, password, partition)

        if iso:
            try:
                from .disk import ISO
                _iso = ISO(auth, uuid=iso)
                _iso.attach(vm)
            except XenAdapterAPIError as e:
                auth.xen.insert_log_entry(new_vm_uuid, state="failed",
                                          message="Failed to mount ISO for VM: %s" % e.message)
                return


        vm.os_install(install_url)
        vm.convert(mode)

        del vm.install
        #subscribe to changefeed

        return vm

    @use_logger
    def set_ram_size(self,  mbs):
        try:
            bs = str(1048576 * int(mbs))
            #vm_ref = self.api.VM.get_by_uuid(vm_uuid)
            static_min = self.get_memory_static_min()
#            if bs <= static_min:
#                self.set_memory_static_min(bs)
            self.set_memory(bs)
        except Exception as e:
            #self.destroy_vm(vm_uuid, force=True)
            try:
                raise e
            except XenAPI.Failure as f:
                self.insert_log_entry('failed', 'Failed to assign %s Mb of memory: %s' % (self.uuid, f.details))
                raise XenAdapterAPIError(self.log, "Failed to set ram size: {0} bytes".format(bs), f.details)




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
    def os_detect(self, os_kind, net_tuple, hostname,  install_url,  override_pv_args, fullname, username, password, partition):
        '''
        call only during install
        :param os_kind:
        :param ip:
        :param hostname:
        :param scenario_url:
        :param override_pv_args:
        :return:
        '''

        if not hasattr(self, 'install'):
            raise RuntimeError("Not an installation process")
        other_config = self.get_other_config()
        os = OSChooser.get_os(os_kind, other_config)

        if os:

            if net_tuple:
                os.set_network_parameters(*net_tuple)

            os.set_hostname(hostname)

            os.set_install_url(install_url)

            self.set_other_config(os.other_config)
            os.fullname = fullname
            os.username = username
            os.password = password
            os.partition = partition

            if not override_pv_args:
                pv_args = os.pv_args()
            else:
                pv_args = override_pv_args
            self.set_PV_args(pv_args)

            self.log.info("Set PV args: {0}".format(pv_args))





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

        self.insert_log_entry('installing', message)
        try:
            self.start(False, True)
        except Exception as e:
            try:
                raise e
            except XenAPI.Failure as f:
                self.insert_log_entry('failed', 'Failed to start OS installation:  %s' % f.details)
                raise XenAdapterAPIError(self.log, 'Failed to start OS installation', f.details)

    @use_logger
    def install_guest_tools(self):
        from .disk import ISO
        from xenadapter.sr import SR
        for ref in SR.get_all(self.auth):
            sr = SR(ref=ref, auth=self.auth)
            if sr.get_is_tools_sr():
                for vdi_ref in sr.get_VDIs():
                    vdi = ISO(ref=vdi_ref, auth=self.auth)
                    if vdi.get_is_tools_iso():
                        vdi.attach(self)
                        return

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
                self.log.info("Shutted down")
        except XenAPI.Failure as f:
            raise XenAdapterAPIError(self.log, "Failed to start/stop VM", f.details)

    @use_logger
    def get_vnc(self):
        self.start_stop_vm(True)
        consoles = self.get_consoles()  # references
        if (len(consoles) == 0):
            self.log.error('Failed to find console')
            return
        try:
            url = None
            for console in consoles:
                proto = self.xen.api.console.get_protocol(console)
                if proto == 'rfb':
                    url = self.xen.api.console.get_location(console)
                    break
            if not url:
                raise XenAdapterAPIError(self.log, "No RFB console, VM UUID in details", self.uuid)

            self.xen.log.info("Console location: {0}".format(url))
        except XenAPI.Failure as f:
            raise XenAdapterAPIError(self.log, "Failed to get console location",f.details)

        return url

    @use_logger
    def destroy_vm(self):
        from .disk import VDI
        from xenadapter.sr import SR
        from xenadapter.vbd import VBD

        self.start_stop_vm(False)

        vbds = self.get_VBDs()
        vdis = [VBD(self.auth, ref=vbd_ref).get_VDI() for vbd_ref in vbds]

        try:
            self.destroy()
            for vdi_ref in vdis:
                vdi = VDI(auth=self.auth, ref=vdi_ref)
                if len(vdi.get_VBDs()) < 2:
                    vdi.destroy()

        except XenAPI.Failure as f:
            raise XenAdapterAPIError(self.log, "Failed to destroy VM",f.details)

        return

    @use_logger
    def destroy_disk(self, vdi_uuid):
        vdi_ref = self.api.VDI.get_by_uuid(vdi_uuid)
        try:
            self.api.VDI.destroy(vdi_ref)
        except XenAPI.Failure as f:

            raise XenAdapterAPIError(self, "Failed to destroy VDI: {0}".format(f.details))

        return

