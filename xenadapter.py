import XenAPI
import hooks
import provision
from exc import XenAdapterAPIError, XenAdapterArgumentError, XenAdapterConnectionError, XenAdapterUnauthorizedActionException
from authentication import BasicAuthenticator

from loggable import Loggable
from inspect import signature



def xenadapter_root(method):
    def decorator(self, *args, **kwargs):
        if self.vmemperor_user == 'root':
            return method(self, *args, **kwargs)
        else:
            raise XenAdapterAPIError(self.log,  "Attempt to call root-only method by user")


    return decorator

def requires_privilege(privilege):
    def requires_privilege_decorator(method):
        def decorator(self, *args, **kwargs):
            sig = signature(method)
            bound_arguments = sig.bind(self, *args, **kwargs)
            if self.check_rights(privilege, bound_arguments.arguments['vm_uuid']):
                return method(self, *args, **kwargs)
            else:
                raise XenAdapterUnauthorizedActionException(self.log, "Unauthorized attempt to call function '%s': needs privilege '%s'"
                                                            % (str(method), privilege))

        return decorator
    return requires_privilege_decorator






class XenAdapter(Loggable):
    AUTOINSTALL_PREFIX = '/autoinstall'
    VMEMPEROR_ACCESS_PREFIX='vm-data/vmemperor/access'

    def get_access_path(self, username=None, is_group=False):
        return '{3}/{0}/{1}/{2}'.format(self.authenticator.__class__.__name__,
                                                               'groups' if is_group else 'users',
                                                            username, self.VMEMPEROR_ACCESS_PREFIX)


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



    def check_rights(self,  action, uuid):
        '''
        Check if it's possible to do 'action' with specified VM
        :param action: action to perform
        - launch: can start/stop vm
        - destroy: can destroy vm
        - attach: can attach/detach disk/network interfaces
        :param uuid: VM uuid
        :return:
        '''
        if self.vmemperor_user == 'root':
            return True
        self.log.debug("Checking VM %s rights for user %s: action %s" % (uuid, self.vmemperor_user, action))

        username = self.get_access_path(self.vmemperor_user, False)
        xenstore_data = self.api.VM.get_xenstore_data(self.api.VM.get_by_uuid(uuid))
        if not xenstore_data:
            self.log.debug("No access information for vm %s, returning None.." % uuid)
            return None
        actionlist = xenstore_data[username].split(';') if username in xenstore_data else None
        if actionlist and (action in actionlist or 'all' in actionlist):
            self.log.debug('User %s is allowed to perform action %s on VM %s' % (self.vmemperor_user, action, uuid))
            return True
        else:
            for group in self.authenticator.get_user_groups():
                groupname = self.get_access_path(group, True)
                actionlist = xenstore_data[groupname].split(';') if groupname in xenstore_data else None
                if actionlist and any(('all' in actionlist, action in actionlist)):
                    self.log.debug('User %s via group %s is allowed to perform action %s on VM %s' % (self.vmemperor_user, group, action, uuid))
                    return True

            self.log.warning('User %s is not allowed to perform action %s on VM %s' % (self.vmemperor_user, action, uuid))
            return False

    def manage_actions(self, action, vm_uuid, revoke=False, user=None, group=None, force=False):
        '''
        Changes action list for a VM
        :param authenticator:
        :param action:
        :param uuid:
        :param revoke:
        :param user:
        :param group:
        :param force: Change actionlist even if user do not have sufficient permissions. Used by CreateVM
        :return:
        '''
        if all((user,group)) or not any((user, group)):
            raise XenAdapterArgumentError(self.log, 'Specify user or group for XenAdapter::manage_actions')



        if user:
            real_name = self.get_access_path(user, False)
        elif group:
            real_name = self.get_access_path(group, True)

        if force or self.check_rights(action, vm_uuid):
            vm_ref = self.api.VM.get_by_uuid(vm_uuid)
            xenstore_data = self.api.VM.get_xenstore_data(vm_ref)
            if real_name in xenstore_data:
                actionlist = xenstore_data[real_name].split(';')
            else:
                actionlist = []

            if revoke:
                if action in actionlist:
                    actionlist.remove(action)
            else:
                if action not in actionlist:
                    actionlist.append(action)

            actions = ';'.join(actionlist)

            xenstore_data[real_name] = actions

            self.api.VM.set_xenstore_data(vm_ref, xenstore_data)




    def __init__(self, settings,  authenticator=None):
        """creates session connection to XenAPI. Connects using admin login/password from settings
        :param authenticator: authorized authenticator object
    """
        if isinstance(authenticator, tuple):
            settings['username'] = authenticator[0]
            settings['password'] = authenticator[1]
            self.vmemperor_user = authenticator[0]
        else:
            try:
                self.vmemperor_user = authenticator.get_id()
            except:
                self.vmemperor_user = 'root'



        self.authenticator = authenticator
        if 'debug' in settings:
                self.debug = bool(settings['debug'])


        self.init_log()



        try:
            url = settings['url']
            username = settings['username']
            password = settings['password']
        except KeyError as e:
            raise XenAdapterArgumentError(self.log, 'Failed to parse settings: {0}'.format(str(e)))

        try:
            self.session = XenAPI.Session(url)
            self.session.xenapi.login_with_password(username, password)
            self.log.info ('Authentication is successful. XenAdapter object created. VMEmperor user: %s aka %s' % (self.vmemperor_user, self.authenticator.get_name() if isinstance(self.authenticator, BasicAuthenticator)  else "(XenServer authentication)"))
            self.api = self.session.xenapi
        except OSError as e:
            raise XenAdapterConnectionError(self.log, "Unable to reach XenServer at {0}: {1}".format(url, str(e)))
        except XenAPI.Failure as e:
            raise XenAdapterConnectionError(self.log, 'Failed to login: url: "{1}"; username: "{2}"; password: "{3}"; error: {0}'.format(str(e), url, username, password))

        return

    @xenadapter_root
    def list_pools(self) -> dict:
        '''
        :return: dict of pool records
        '''
        return self.get_all_records(self.api.pool)

    @xenadapter_root
    def list_vms(self):
        '''
        :return: dict of vm records except dom0 and templates
        '''
        keys = ['power_state', 'name_label', 'uuid']
        #return {key : value for key, value in self.get_all_records(self.api.VM).items()
        #       if not value['is_a_template'] and not value['is_control_domain']}

        def process(value):
            vm_ref = self.api.VM.get_by_uuid(value['uuid'])
            new_rec = {k : v for k,v in value.items() if k in keys}

            new_rec['network'] = []
            vifs = self.api.VM.get_VIFs(vm_ref)
            for vif in vifs:
                net_ref = self.api.VIF.get_network(vif)
                net_uuid = self.api.network.get_uuid(net_ref)
                new_rec['network'].append(net_uuid)
            new_rec['disks'] = []
            vbds = self.api.VM.get_VBDs(vm_ref)
            for vbd in vbds:
                vdi_ref = self.api.VBD.get_VDI(vbd)
                vdi_uuid = self.api.VDI.get_uuid(vdi_ref)
                new_rec['disks'].append(vdi_uuid)
            return new_rec

        return [process(value) for value in self.get_all_records(self.api.VM).values()
                if not value['is_a_template'] and not value['is_control_domain']]

    @xenadapter_root
    def list_srs(self) -> dict:
        '''
        :return: dict of storage repositories' records
        '''
        return self.get_all_records(self.api.SR)


    @xenadapter_root
    def list_vdis(self) -> dict:
        '''
        :return: dict of virtual disk images' records
        '''
        return self.get_all_records(self.api.VDI)

    @xenadapter_root
    def list_networks(self) -> dict:
        '''
        dict of network interfaces' records
        :return:
        '''
        return self.get_all_records(self.api.network)

    #@xenadapter_root
    def list_templates(self) -> dict:
        '''
        dict of VM templates' records
        :return:
        '''
        keys = ['hvm', 'name_label', 'uuid']
        def process(value):
            new_rec = {k: v for k, v in value.items() if k in keys}
            if value['HVM_boot_policy'] == '':
                new_rec['hvm'] = False
            else:
                new_rec['hvm'] = True
            return new_rec

        return {value['uuid'] : process(value) for value in self.get_all_records(self.api.VM).values()
                  if value['is_a_template']}

    @xenadapter_root
    def access_list(self) -> list:
        if not self.authenticator:
            raise XenAdapterAPIError(self.log, "Unable to generate access list: no authenticator object given to XenAdapter")
        def read_xenstore_access_rights(xenstore_data : dict):
            filtered_iterator = filter(lambda keyvalue : keyvalue[1] and  keyvalue[0].startswith(self.VMEMPEROR_ACCESS_PREFIX),
                                       xenstore_data.items())

            for k, v in filtered_iterator:
                key_components= k[len(self.VMEMPEROR_ACCESS_PREFIX) + 1:].split('/')
                if key_components[0] == self.authenticator.__name__:

                    yield {'userid' :  '%s/%s' % (key_components[1], key_components[2]), 'access' : v}


        vms = self.api.VM.get_all_records()
        result_dict = {}
        for k, v in vms.items():
            if v['is_a_template'] or v['is_control_domain']:
                continue
            xenstore_data = v['xenstore_data']
            for d in read_xenstore_access_rights(xenstore_data):
                if d['userid'] in result_dict:
                    result_dict[d['userid']].append({'vm_uuid' : v['uuid'], 'access' : d['access']})
                else:
                    result_dict[d['userid']] = [{'vm_uuid' : v['uuid'], 'access' : d['access']}]

        return [{'userid' : k, 'vms' : v} for k, v in result_dict.items()]









    class GenericOS:
        '''
        A class that generates kernel boot arguments string for various Linux distributions
        '''
        def __init__(self):
            self.dhcp = True

        def pv_args(self) -> str:
            '''
            Obtain pv_args - kernel parameters for paravirtualized VM
            :return:
            '''

        def hvm_args(self) -> str:
            '''
            Obtain hvm_args - whatever that might be
            :return:
            '''
        def set_scenario(self, url):
            raise NotImplementedError
        def set_kickstart(self, url):
            return 'ks={0}'.format(url)
        def set_preseed(self, url):
            return 'preseed/url={0}'.format(url)

        def set_hostname(self, hostname):
            self.hostname = hostname

        def set_network_parameters(self, ip=None, gw=None, netmask=None, dns1=None, dns2=None):
            if not ip:
               self.dhcp = True
            else:
                if not gw:
                    raise XenAdapterArgumentError(self,"Network configuration: IP has been specified, missing gateway")
                if not netmask:
                    raise XenAdapterArgumentError(self,"Network configuration: IP has been specified, missing netmask")
                ip_string = " ip=%s::%s:%s" % (ip, gw, netmask)

                if dns1:
                    ip_string = ip_string + ":::off:%s" % dns1
                    if dns2:
                        ip_string = ip_string +":%s" % dns2

            self.ip = ip_string
            self.dhcp = False


    class UbuntuOS (GenericOS):
        '''
        OS-specific parameters for Ubuntu
        '''

        def set_scenario(self, url):
            self.scenario = self.set_preseed(url)
            # self.scenario = self.set_kickstart(url)

        def pv_args(self):
            if self.dhcp:
                self.ip = "netcfg/disable_dhcp=false"
            return "auto=true console=hvc0 debian-installer/locale=en_US console-setup/layoutcode=us console-setup/ask_detect=false interface=eth0 %s netcfg/get_hostname=%s %s --" % (
                self.ip, self.hostname, self.scenario)

        def set_network_parameters(self, ip=None, gw=None, netmask=None, dns1=None, dns2=None):
            if not ip:
                self.dhcp = True
            else:
                if not gw:
                    raise XenAdapterArgumentError(self, "Network configuration: IP has been specified, missing gateway")
                if not netmask:
                    raise XenAdapterArgumentError(self, "Network configuration: IP has been specified, missing netmask")

                ip_string = " ipv6.disable=1 netcfg/disable_autoconfig=true netcfg/use_autoconfig=false  netcfg/confirm_static=true netcfg/get_ipaddress=%s netcfg/get_gateway=%s netcfg/get_netmask=%s netcfg/get_nameservers=%s netcfg/get_domain=vmemperor" % (
                ip, gw, netmask, dns1)

            self.ip = ip_string
            self.dhcp = False

    class CentOS (GenericOS):
        """
        OS-specific parameters for CetOS
        """
        def set_scenario(self, url):
            self.scenario = self.set_kickstart(url)



        def pv_args(self):
            return "%s %s" % (self.ip, self.scenario)

    def create_vm(self, tmpl_uuid, sr_uuid, net_uuid, vdi_size, ram_size, hostname, mode, os_kind=None, ip=None, install_url=None, scenario_url=None, name_label = '', start=True, override_pv_args=None) -> str:
        '''
        Creates a virtual machine and installs an OS

        :param tmpl_uuid: Template UUID
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
        :return: VM UUID
        '''
        try:
            tmpl_ref = self.api.VM.get_by_uuid(tmpl_uuid)
            new_vm_ref = self.api.VM.clone(tmpl_ref, name_label)
            new_vm_uuid = self.api.VM.get_uuid(new_vm_ref)
            self.log.info ("New VM is created: UUID {0}, OS type {1}".format(new_vm_uuid, os_kind))
        except XenAPI.Failure as f:
            raise XenAdapterAPIError(self, "Failed to clone template: {0}".format(f.details))



        try:

            ram_size = str(1048576 * int(ram_size))
            self.api.VM.set_memory(new_vm_ref, ram_size)

            if install_url:
                self.log.info("Adding Installation URL: %s" % install_url)
                config = self.api.VM.get_other_config(new_vm_ref)
                config['install-repository'] = install_url
                config['default-mirror'] = install_url
                self.api.VM.set_other_config(new_vm_ref, config)

            if 'ubuntu' in os_kind or 'debian' in os_kind:
                os = XenAdapter.UbuntuOS()
                try:
                    debian_release = os_kind.split()[1]
                    config = self.api.VM.get_other_config(new_vm_ref)
                    config['debian-release'] = debian_release
                    self.api.VM.set_other_config(new_vm_ref, config)
                except IndexError:
                    pass
            else:
                if 'centos' in os_kind:
                    os = XenAdapter.CentOS()
                    config = self.api.VM.get_other_config(new_vm_ref)
                    if 'rhel6' in config:
                        del config['rhel6']
                    self.api.VM.set_other_config(new_vm_ref, config)
                else:
                    os = None

            if os:
                os.set_network_parameters(*ip)
                os.set_hostname(hostname)
                os.set_scenario(scenario_url)

                if mode == 'pv':
                    if not override_pv_args:
                        pv_args = os.pv_args()
                    else:
                        pv_args = override_pv_args
                    self.api.VM.set_HVM_boot_policy(new_vm_ref, '')
                    self.api.VM.set_PV_bootloader(new_vm_ref, 'eliloader')
                    self.api.VM.set_PV_args(new_vm_ref, pv_args)

                if mode == 'hvm':
                    policy = self.api.VM.get_HVM_boot_policy(new_vm_ref)
                    if policy == '':
                        self.api.VM.set_HVM_boot_policy(new_vm_ref, 'BIOS order')
                    bp = self.api.VM.get_HVM_boot_params(new_vm_ref)
                    bp['ks'] = scenario_url

        except XenAPI.Failure as f:
            self.destroy_vm(new_vm_uuid)
            raise XenAdapterAPIError(self, 'Failed to install OS: {0}'.format(f.details))

        try:
            specs = provision.ProvisionSpec()
            vdi_size = str(1048576 * int(vdi_size))
            specs.disks.append(provision.Disk("0", vdi_size, sr_uuid, True))
            provision.setProvisionSpec(self.session, new_vm_ref, specs)
        except Exception as e:
            self.destroy_vm(new_vm_uuid)
            try:
                raise e
            except XenAPI.Failure as f:
                raise XenAdapterAPIError(self, "Failed to setting disk: {0}".format(f.details))

        try:
            self.api.VM.provision(new_vm_ref)
        except Exception as e:
            self.destroy_vm(new_vm_uuid)
            try:
                raise e
            except XenAPI.Failure as f:
                raise XenAdapterAPIError(self, "Failed to provision: {0}".format(f.details))

        if self.vmemperor_user:
            self.manage_actions('all', new_vm_uuid, user=self.vmemperor_user, force=True)

        self.connect_vm(new_vm_uuid, net_uuid, ip)





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

        other_config = {}
        if self.vmemperor_user:
            other_config['vmemperor_user'] = self.vmemperor_user

        args = {'SR': sr_ref, 'virtual_size': str(size), 'type': 'system', \
                'sharable': False, 'read_only': False, 'other_config': other_config, \
                'name_label': name_label}
        try:
            vdi_ref = self.api.VDI.create(args)
            vdi_uuid = self.api.VDI.get_uuid(vdi_ref)
            self.log.info ("VDI is created: UUID {0}".format(vdi_uuid))
        except XenAPI.Failure as f:
            raise XenAdapterAPIError(self, "Failed to create VDI: {0}".format(f.details))

        return vdi_uuid

    @requires_privilege('launch')
    def start_stop_vm(self, vm_uuid, enable):
        """
        Starts and stops VM if required
        :param vm_uuid:
        :param enable:
        :return:
        """
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        ps = self.api.VM.get_power_state(vm_ref)
        try:
            if ps != 'Running' and bool(enable) == True:
                self.api.VM.start (vm_ref, False, True)
                self.log.info ("Started VM UUID {0}".format(vm_uuid))
            if ps == 'Running' and bool(enable) == False:
                self.api.VM.shutdown(vm_ref)
                self.log.info("Shutted down VM UUID {0}".format(vm_uuid))
        except XenAPI.Failure as f:
            raise XenAdapterAPIError (self.log, "Failed to start/stop VM: {0}".format(f.details))

        return

    @requires_privilege('attach')
    def connect_vm(self, vm_uuid, net_uuid, ip=None):
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
        except XenAdapterAPIError as f:
            raise XenAdapterAPIError(self, "Failed to create VIF: {0}".format(f.details))

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
        except XenAPI.Failure as f:
            raise XenAdapterAPIError (self, "Failed to enable/disable template: {0}".format(f.details))

    def get_power_state(self, vm_uuid) -> str:
        '''
        Returns a power state of the VM
        :param vm_uuid: VM UUID
        :return: VM State string
        '''
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        return self.api.VM.get_power_state(vm_ref)

    @requires_privilege('launch')
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
            return ""
        try:
            cons_ref = consoles[0]
            console = self.api.console.get_record(cons_ref)
            url = self.api.console.get_location(cons_ref)
            self.log.info ("Console location {0} of VM UUID {1}".format(url, vm_uuid))
        except XenAPI.Failure as f:
            raise XenAdapterAPIError(self, "Failed to get console location: {0}".format(f.details))

        return url



    @requires_privilege('attach')
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
        except XenAPI.Failure as f:
            raise XenAdapterAPIError(self, "Failed to create VBD: {0}".format(f.details))

        vbd_uuid = self.api.VBD.get_uuid(vbd_ref)
        if (self.api.VM.get_power_state(vm_ref) == 'Running'):
            try:
                self.api.VBD.plug(vbd_ref)
            except Exception as e:
                self.log.warning("Disk will be attached after reboot with VBD UUID {0}".format(vbd_uuid))
                return vbd_uuid

        self.log.info ("Disk is attached with VBD UUID: {0}".format(vbd_uuid))

        return vbd_uuid

    @requires_privilege('attach')
    def detach_disk(self, vm_uuid, vdi_uuid):
        '''
        Detach a VBD object while trying to eject it if the machine is running
        :param vbd_uuid: virtual block device UUID to detach
        :return:
        '''
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        vdi_ref = self.api.VDI.get_by_uuid(vdi_uuid)
        vbds = self.api.VM.get_VBDs(vm_ref)
        for vbd_ref in vbds:
            vdi = self.api.VBD.get_VDI(vbd_ref)
            if vdi == vdi_ref:
                vbd_uuid = self.api.VBD.get_uuid(vbd_ref)
                break
        if not vbd_uuid:
            raise XenAdapterAPIError(self, "Failed to detach disk: Disk isn't attached")

        vbd_ref = self.api.VBD.get_by_uuid(vbd_uuid)
        if self.api.VM.get_power_state(vm_ref) == 'Running':
            try:
                self.api.VBD.unplug(vbd_ref)
            except Exception as e:
                self.log.warning("Failed to detach disk from running VM")
                return 1
            
        try:
            self.api.VBD.destroy(vbd_ref)
            self.log.info("VBD UUID {0} is destroyed".format(vbd_uuid))
        except XenAPI.Failure as f:
            raise XenAdapterAPIError(self, "Failed to detach disk: {0}".format(f.details))

        return

    @requires_privilege('destroy')
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
        except XenAPI.Failure as f:
            raise XenAdapterAPIError (self, "Failed to destroy VM: {0}".format(f.details))

        return

    def destroy_disk(self, vdi_uuid):
        vdi_ref = self.api.VDI.get_by_uuid(vdi_uuid)
        try:
            self.api.VDI.destroy(vdi_ref)
        except XenAPI.Failure as f:

            raise XenAdapterAPIError(self, "Failed to destroy VDI: {0}".format(f.details))

        return

    @requires_privilege('launch')
    def hard_shutdown(self, vm_uuid):
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        if self.api.VM.get_power_state(vm_ref) != 'Halted':
            self.api.VM.hard_shutdown(vm_ref)


    def set_other_config(self, subject, uuid, name, value=None, overwrite=True):
        '''
        Set value of other_config field
        :param subject: API subject
        :param uuid:
        :param name:
        :param value: none if you wish to remove field
        :return:
        '''
        ref = subject.get_by_uuid(uuid)
        if value is not None:
            if overwrite:
                try:
                    subject.remove_from_other_config(ref, name)
                except XenAPI.Failure as f:
                    self.log.debug("set_other_config: failed to remove entry %s from other_config (overwrite=True): %s" % (name, f.details))
            try:
                subject.add_to_other_config(ref, name, value)
            except XenAPI.Failure as f:
                raise XenAdapterAPIError(self, "Failed to add tag '{0}' with value '{1}' to subject '{2}'s other_config field {3}': {4}".format(
                    name, value, subject, uuid, f.details))
        else:
            try:
                subject.remove_from_other_config(ref, name, value)
            except XenAPI.Failure as f:
                raise XenAdapterAPIError(self,
                                         "Failed to remove tag '{0}' from subject '{1}'s other_config field {2}': {3}".format(
                                             name, subject, uuid, f.details))


