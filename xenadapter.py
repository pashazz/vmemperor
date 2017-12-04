
import XenAPI
import hooks
import provision
from exc import XenAdapterAPIError, XenAdapterArgumentError, XenAdapterConnectionError, XenAdapterUnauthorizedActionException
from authentication import BasicAuthenticator

from loggable import Loggable
import logging
import time
import rethinkdb as r
import traceback


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
            self.ip = None
        else:
            if not gw:
                raise XenAdapterArgumentError(self, "Network configuration: IP has been specified, missing gateway")
            if not netmask:
                raise XenAdapterArgumentError(self, "Network configuration: IP has been specified, missing netmask")
            ip_string = " ip=%s::%s:%s" % (ip, gw, netmask)

            if dns1:
                ip_string = ip_string + ":::off:%s" % dns1
                if dns2:
                    ip_string = ip_string + ":%s" % dns2

            self.ip = ip_string
        self.dhcp = False


class UbuntuOS(GenericOS):
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
            self.ip = None
        else:
            if not gw:
                raise XenAdapterArgumentError(self, "Network configuration: IP has been specified, missing gateway")
            if not netmask:
                raise XenAdapterArgumentError(self, "Network configuration: IP has been specified, missing netmask")

            ip_string = " ipv6.disable=1 netcfg/disable_autoconfig=true netcfg/use_autoconfig=false  netcfg/confirm_static=true netcfg/get_ipaddress=%s netcfg/get_gateway=%s netcfg/get_netmask=%s netcfg/get_nameservers=%s netcfg/get_domain=vmemperor" % (
                ip, gw, netmask, dns1)

            self.ip = ip_string
        self.dhcp = False

    def get_release(self, num):
        releases = {
            '12.04': 'precise',
            '14.04': 'trusty',
            '14.10': 'utopic',
            '15.04': 'vivid',
            '15.10': 'willy',
            '16.04': 'xenial',
            '16.10': 'yakkety',
            '17.04': 'zesty',
            '17.10': 'artful',
        }
        if num in releases.keys():
            return releases[num]
        if num in releases.values():
            return num
        return None


class DebianOS(GenericOS):
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
            self.ip = None
        else:
            if not gw:
                raise XenAdapterArgumentError(self, "Network configuration: IP has been specified, missing gateway")
            if not netmask:
                raise XenAdapterArgumentError(self, "Network configuration: IP has been specified, missing netmask")

            ip_string = " ipv6.disable=1 netcfg/disable_autoconfig=true netcfg/use_autoconfig=false  netcfg/confirm_static=true netcfg/get_ipaddress=%s netcfg/get_gateway=%s netcfg/get_netmask=%s netcfg/get_nameservers=%s netcfg/get_domain=vmemperor" % (
                ip, gw, netmask, dns1)

            self.ip = ip_string
        self.dhcp = False

    def get_release(self, num):
        releases = {
            '7': 'wheezy',
            '8': 'jessie',
            '9': 'stretch'
        }
        if str(num) in releases.keys():
            return releases[str(num)]
        if num in releases.values():
            return num
        return None


class CentOS(GenericOS):
    """
    OS-specific parameters for CetOS
    """

    def set_scenario(self, url):
        self.scenario = self.set_kickstart(url)

    def pv_args(self):
        return "%s %s" % (self.ip, self.scenario)


def use_logger(method):
    def decorator(self, *args, **kwargs):
        oldFormatter = self.xen.fileHandler.formatter
        self.xen.fileHandler.setFormatter(
            logging.Formatter(
                "%(levelname)-10s [%(asctime)s] (type: {0}; uuid: {1}) : %(message)s".format(self.__class__.__name__,
                                                                                             self.uuid))
        )
        ret = method(self, *args, **kwargs)
        self.xen.fileHandler.setFormatter(oldFormatter)
        return ret

    return decorator


class XenObjectMeta(type):
    def __getattr__(cls, item):
        def method(xen : XenAdapter, *args, **kwargs):
            if not hasattr(cls, 'api_class'):
                raise XenAdapterArgumentError(xen.log, "api_class not specified for XenObject")

            api_class = getattr(cls, 'api_class')
            api = getattr(xen.api, api_class)
            attr = getattr(api, item)
            try:
                return attr(*args, **kwargs)
            except XenAPI.Failure as f:
                raise XenAdapterAPIError(xen.log, "Failed to execute static method %s::%s: Error details: %s"
                                         % (api_class, item, f.details ))
        return method




class XenObject(metaclass=XenObjectMeta):

    def __init__(self, auth : BasicAuthenticator,  uuid=None, ref=None):
        '''Set  self.auth.xen_api_class to xen.api.something before calling this'''
        self.auth = auth
        # if not isinstance(xen, XenAdapter):
        #          raise AttributeError("No XenAdapter specified")
        self.log = self.auth.xen.log
        self.xen = self.auth.xen

        if uuid:
            self.uuid = uuid
            try:
                getattr(self, 'ref') #uuid check
            except XenAPI.Failure as f:
                raise  XenAdapterAPIError(auth.xen.log, "Failed to initialize object of type %s with UUID %s: %s" %
                                          (self.__class__.__name__, self.uuid, f.details))

        elif ref:
            self.ref = ref
        else:
            raise AttributeError("Not uuid nor ref not specified")



        self.access_prefix = 'vm-data/vmemperor/access'



    def check_access(self,  action):
        return True

    def manage_actions(self, action,  revoke=False, user=None, group=None, force=False):
        pass




    def __getattr__(self, name):
        api = getattr(self.xen.api, self.api_class)
        if name == 'uuid': #ленивое вычисление uuid по ref
            self.uuid = api.get_uuid(self.ref)
            return self.uuid
        elif name == 'ref': #ленивое вычисление ref по uuid
            self.ref = api.get_by_uuid(self.uuid)
            return self.ref



        attr = getattr(api, name)
        return lambda *args, **kwargs : attr(self.ref, *args, **kwargs)

class ACLXenObject(XenObject):
    def get_access_path(self, username=None, is_group=False):
        return '{3}/{0}/{1}/{2}'.format(self.auth.__class__.__name__,
                                                               'groups' if is_group else 'users',
                                                        username, self.access_prefix)

    ALLOW_EMPTY_XENSTORE = False # Empty xenstore for some objects might treat them as
    def check_access(self,  action):
        '''
        Check if it's possible to do 'action' with specified VM
        :param action: action to perform
        for 'VM'  these are

        - launch: can start/stop vm
        - destroy: can destroy vm
        - attach: can attach/detach disk/network interfaces
        :return: True if access granted, False if access denied, None if no info
        '''
        #if self.auth == 'root':
#            return True
        self.log.info("Checking %s %s rights for user %s: action %s" % (self.__class__.__name__, self.uuid, self.auth.get_id(), action))

        username = self.get_access_path(self.auth.get_id(), False)
        xenstore_data = self.get_xenstore_data()
        if not xenstore_data:
            if self.ALLOW_EMPTY_XENSTORE:
                return True
            raise XenAdapterUnauthorizedActionException(self.log,
                                                    "Unauthorized attempt (no info on access rights): needs privilege '%s', call stack: %s"
                                                    % (action, traceback.format_stack()))



        actionlist = xenstore_data[username].split(';') if username in xenstore_data else None
        if actionlist and (action in actionlist or 'all' in actionlist):
            self.log.info('User %s is allowed to perform action %s on %s %s' % (self.auth.get_id(), action, self.__class__.__name__, self.uuid))
            return True
        else:
            for group in self.auth.get_user_groups():
                groupname = self.get_access_path(group, True)
                actionlist = xenstore_data[groupname].split(';') if groupname in xenstore_data else None
                if actionlist and any(('all' in actionlist, action in actionlist)):
                    self.log.info('User %s via group %s is allowed to perform action %s on %s %s' % (self.auth.get_id(), group, action, self.__class__.__name__,  self.__uuid__))
                    return True

            raise XenAdapterUnauthorizedActionException(self.log,
                                                        "Unauthorized attempt: needs privilege '%s', call stack: %s"
                                                        % (action, traceback.format_stack()))

    def manage_actions(self, action,  revoke=False, user=None, group=None, force=False):
        '''
        Changes action list for a Xen object
        :param action:
        :param revoke:
        :param user: User ID as returned from authenticator.get_id()
        :param group:
        :param force: Change actionlist even if user do not have sufficient permissions. Used by CreateVM
        :return:
        '''

        if all((user,group)) or not any((user, group)):
            raise XenAdapterArgumentError(self.log, 'Specify user or group for XenObject::manage_actions')



        if user:
            real_name = self.get_access_path(user, False)
        elif group:
            real_name = self.get_access_path(group, True)

        if force or self.check_rights(action):
            xenstore_data = self.get_xenstore_data()
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

            self.set_xenstore_data(xenstore_data)


class VIF(XenObject, metaclass=XenObjectMeta):
    api_class = 'VIF'
    @classmethod
    def create(cls, auth, *args, **kwargs):
        attr = cls.__class__.__getattr__(cls, 'create')
        return VIF(auth, ref=attr(auth.xen, *args, **kwargs))


class AbstractVM(ACLXenObject):
    api_class = 'VM'

    def insert_log_entry(self, *args, **kwargs):
        self.auth.xen.insert_log_entry(self.uuid, *args, **kwargs)

class VM (AbstractVM):

    def __init__(self, auth, uuid=None, ref=None):
        super().__init__(auth, uuid, ref)

    @classmethod
    def create(self, auth, new_vm_uuid, sr_uuid, net_uuid, vdi_size, ram_size, hostname, mode, os_kind=None, ip=None, install_url=None, scenario_url=None, name_label = '', start=True, override_pv_args=None):
        '''
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
        :return: VM UUID
        '''
        #new_vm_uuid = self.clone_tmpl(tmpl_uuid, name_label, os_kind)

        vm = VM(auth, uuid=new_vm_uuid)
        vm.install = True
        if isinstance(auth, BasicAuthenticator):
            vm.manage_actions('all',  user=auth.get_id(), force=True)

        vm.set_ram_size(ram_size)
        vm.set_disks(sr_uuid, vdi_size)





        #self.connect_vm(new_vm_uuid, net_uuid, ip)
        vm.convert('pv')

        try:
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






    @classmethod
    def get_all_records(cls, xen):
       return {k:v for k,v in xen.api.VM.get_all_records().items()
                if not (v['is_a_template'] or v['is_control_domain'])}



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
        if not hasattr(self, 'install'):
            self.check_access('launch')

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
        if not hasattr(self, 'install'):
            self.check_access('launch')


        ps = self.get_power_state()
        try:
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
        if not hasattr(self, 'install'):
            self.check_access('launch')

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
    def destroy_vm(self, force=False):

        if not hasattr(self, 'install'):
            self.check_access('destroy')

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



class Template(AbstractVM):
    ALLOW_EMPTY_XENSTORE = True

    @classmethod
    def get_all_records(cls, xen):
        return {k: v for k, v in xen.api.VM.get_all_records().items()
                if v['is_a_template']}

    @use_logger
    def clone(self, name_label):
        try:

            new_vm_ref = self.__getattr__('clone')(name_label)
            vm = VM(self.auth, ref=new_vm_ref)
            self.insert_log_entry('cloned', 'Cloned to %s' % vm.uuid)
            self.log.info("New VM is created: UUID {0}".format(vm.uuid))
            return vm
        except XenAPI.Failure as f:
            self.insert_log_entry('failed', f.details)
            raise XenAdapterAPIError(self.log, "Failed to clone template: {0}".format(f.details))

    @use_logger
    def enable_disable(self, enable):
        '''
        Adds/removes tag 'vmemperor'
        :param enable:
        :return:
        '''
        try:
            if enable:
                self.add_tags('vmemperor_enabled')
                self.log.info("Enabled template UUID {0}".format(self.uuid))
            else:
                self.remove_tags('vmemperor_enabled')
                self.log.info("Disabled template UUID {0}".format(self.uuid))
        except XenAPI.Failure as f:
            raise XenAdapterAPIError(self.log, "Failed to {0} template: {1}".format(
                'enable' if enable else 'disable', f.details))



class Network(XenObject):
    api_class = "network"
    def __init__(self, auth, uuid):
        super().__init__(auth, uuid)

    @use_logger
    def attach(self, vm: VM) -> VIF:
        self.check_access('attach')

        args = {'VM': vm.ref, 'network': self.ref , 'device': str(len(vm.get_VIFs())),
                'MAC': '', 'MTU': self.get_MTU() , 'other_config': {},
                'qos_algorithm_type': '', 'qos_algorithm_params': {}}
        try:

            vif = VIF.create(self.auth, args)
            #vif_uuid = self.auth.xen.api.VIF.get_uuid(vif_ref)

            self.log.info("VM is connected to network: VIF UUID {0}".format(vif.uuid))
        except XenAdapterAPIError as f:
            raise XenAdapterAPIError(self.auth.xen.log, "Failed to create VIF: {0}".format(f.details))

        return vif


class VBD(XenObject):
    api_class = 'VBD'


class Attachable:

    @use_logger
    def _attach(self : XenObject, vm: VM, type : str, mode: str, empty=False) -> str:
        '''
        Attach self (XenObject - either ISO or Disk) to vm VM with disk type type
        :param vm:VM to attach to
        :param mode: 'RO'/'RW'
        :param type: 'CD'/'Disk'/'Floppy'
        :return: VBD UUID
        '''
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

        vbd_ref = self.auth.xen.api.VBD.get_by_uuid(vbd_uuid)
        if vm.get_power_state() == 'Running':
            try:
                self.auth.xen.api.VBD.unplug(vbd_ref)
            except Exception as e:
                self.log.warning("Failed to detach disk from running VM")
                return 1

        try:
            self.api.VBD.destroy(vbd_ref)
            self.log.info("VBD UUID {0} is destroyed".format(vbd_uuid))
        except XenAPI.Failure as f:
            raise XenAdapterAPIError(self.log, "Failed to detach disk: {0}".format(f.details))

        return



class ISO(XenObject, Attachable):
    api_class = 'VDI'

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

    def attach(self, vm : VM) -> VBD:
        return VBD(uuid=self._attach(vm, 'CD', 'RO'))

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

class Singleton(type):
    """Metaclass for singletons. Any instantiation of a Singleton class yields
    the exact same object, e.g.:

    >>> class MyClass(metaclass=Singleton):
            pass
    >>> a = MyClass()
    >>> b = MyClass()
    >>> a is b
    True
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        try:

            if kwargs['nosingleton']:
                del kwargs['nosingleton']
                return super(Singleton, cls).__call__(*args, **kwargs)
        except:
            pass

        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args,
                                                                **kwargs)
        return cls._instances[cls]

    @classmethod
    def __instancecheck__(mcs, instance):
        if instance.__class__ is mcs:
            return True
        else:
            return isinstance(instance.__class__, mcs)



class XenAdapter(Loggable, metaclass=Singleton):
    AUTOINSTALL_PREFIX = '/autoinstall'
    VMEMPEROR_ACCESS_PREFIX='vm-data/vmemperor/access'




    def __init__(self, settings):
        """creates session connection to XenAPI. Connects using admin login/password from settings
        :param authenticator: authorized authenticator object
    """

        #if isinstance(authenticator, tuple):
#            settings['username'] = authenticator[0]
#            settings['password'] = authenticator[1]
#            self.vmemperor_user = authenticator[0]
#        else:
#            try:
#                self.vmemperor_user = authenticator.get_id()
#            except:
#                self.vmemperor_user = 'root'



 #       self.authenticator = authenticator
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
            self.log.info ('Authentication is successful. XenAdapter object created')
            self.api = self.session.xenapi
        except OSError as e:
            raise XenAdapterConnectionError(self.log, "Unable to reach XenServer at {0}: {1}".format(url, str(e)))
        except XenAPI.Failure as e:
            raise XenAdapterConnectionError(self.log, 'Failed to login: url: "{1}"; username: "{2}"; password: "{3}"; error: {0}'.format(str(e), url, username, password))


        self.conn = r.connect(settings['host'], settings['port'], db=settings['database']).repl()
        if not settings['database'] in r.db_list().run():
            r.db_create('vmemperor').run()

        self.db  = r.db(settings['database'])

        if  'vm_logs' not in self.db.table_list().run():
            self.db.table_create('vm_logs', durability='soft').run()
            self.db.table('vm_logs').index_create('uuid').run()
            self.db.table('vm_logs').index_wait('uuid').run()

        self.table = self.db.table('vm_logs')





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






    def list_pools(self) -> dict:
        '''
        :return: dict of pool records
        '''
        return self.get_all_records(self.api.pool)

    def list_vms(self):
        '''
        :return: list of vm records except dom0 and templates
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
                try:
                    vdi_uuid = self.api.VDI.get_uuid(vdi_ref)
                    new_rec['disks'].append(vdi_uuid)
                except XenAPI.Failure as f:
                    if f.details[1] != 'VDI':
                        raise f


            return new_rec

        return [process(value) for value in VM.get_all_records(self).values()]



    def list_srs(self) -> dict:
        '''
        :return: dict of storage repositories' records
        '''
        return self.get_all_records(self.api.SR)



    def list_isos(self) -> list:
        '''
        :return: list of ISO images records
        '''
        iso_list = []

        for ref, rec in ISO.get_all_records(self).items():
                fields = {'uuid', 'name_label', 'name_description', 'location'}
                rec = {key : value for key, value in rec.items() if key in fields }
                iso_list.append(rec)

        return iso_list







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

    assets = [VM, Template]


    def access_list(self, authenticator_name) -> list:
        def read_xenstore_access_rights(xenstore_data : dict, asset : ACLXenObject):
            filtered_iterator = filter(lambda keyvalue : keyvalue[1] and  keyvalue[0].startswith(self.VMEMPEROR_ACCESS_PREFIX),
                                       xenstore_data.items())

            for k, v in filtered_iterator:
                key_components= k[len(self.VMEMPEROR_ACCESS_PREFIX) + 1:].split('/')
                if key_components[0] == authenticator_name:

                    yield {'userid' :  '%s/%s' % (key_components[1], key_components[2]), 'access' : v}

            else:
                if asset.ALLOW_EMPTY_XENSTORE:
                    yield  {'userid' : 'any', 'access' : 'all'}

        # Repeat procedure for VM objects and VDI objects
        final_list = []
        for asset in self.assets:

            recs = asset.get_all_records(self)
            result_dict = {}
            for k,v in recs.items():
                xenstore_data = v['xenstore_data']
                for d in read_xenstore_access_rights(xenstore_data, asset):
                    if d['userid'] in result_dict:
                        result_dict[d['userid']].append({'uuid' : v['uuid'], 'access' : d['access']})
                    else:
                        result_dict[d['userid']] = [{'uuid' : v['uuid'], 'access' : d['access']}]


            print(asset.api_class)
            final_list.extend([{'userid' : k, 'type' : asset.api_class, 'items' : v} for k, v in result_dict.items()])
        return final_list


    def insert_log_entry(self, uuid, state, message):

        #r.now() is rethink-compatible datetime.datetime.now()
        self.table.insert(dict(uuid=uuid, state=state, message=message, time=r.now()), durability='soft').run(self.conn)






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



    def get_vnc(self, vm_uuid) -> str:
        """
        Get VNC Console
        :param vm_uuid: VM UUID
        :return: URL console location
        """
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        self.start_stop_vm(True)
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


