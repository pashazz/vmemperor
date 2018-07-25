from exc import *


from urllib.parse import urlencode

class GenericOS:
    '''
    A class that generates kernel boot arguments string for various Linux distributions
    '''

    def __init__(self):
        self.dhcp = True
        self.other_config = {}

        self.hostname = None
        self.username = None
        self.password = None
        self.install_url = None
        self.fullname = None
        self.ip = None
        self.gateway=None
        self.netmask = None
        self.dns0 = None
        self.dns1 = None
        self.partition = None

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

    def set_install_url(self, url):
        '''
        Set install URL to other_config field
        :param url:
        :return:
        '''
        self.install_url = url

    def set_scenario(self, url):
        raise NotImplementedError

    def get_scenario(self):
        '''
        return
        :return: Scenario URL
        '''
        from vmemperor import opts
        from xenadapter import XenAdapter
        args = dict(
            hostname=self.hostname,
            username=self.username,
            password=self.password,
            mirror_url=self.install_url,
            fullname=self.fullname,
            ip=self.ip,
            gateway=self.gateway,
            netmask=self.netmask,
            dns0=self.dns0,
            dns1=self.dns1,
            partition=self.partition
        )

        return 'http://' + opts.vmemperor_host + ':' + str(
            opts.vmemperor_port) + XenAdapter.AUTOINSTALL_PREFIX + "/" + self.os_kind.split()[0] + "?" \
        + urlencode(args, doseq=True)

    def set_kickstart(self, url):
        return 'ks={0}'.format(url)

    def set_preseed(self, url):
        return 'preseed/url={0}'.format(url)

    def set_hostname(self, hostname):
        self.hostname = hostname

    def set_network_parameters(self, ip=None, gw=None, netmask=None, dns1=None, dns2=None):
        self.ip = ip
        self.gateway = gw
        self.netmask = netmask
        self.dns1 = dns1
        self.dns2 = dns2
        if self.ip and self.gateway and self.netmask:
            self.dhcp = False

    def set_os_kind(self, os_kind):
        self.os_kind = os_kind

class DebianOS(GenericOS):
    '''
    OS-specific parameters for Debian
    '''
    HVM_RELEASES=[]

    def pv_args(self):
        if self.dhcp:
            net_config = "netcfg/disable_dhcp=false"
        else:
            if not self.ip:
                raise AttributeError("dhcp is set to false, but ip is not set")
            if not self.gateway:
                raise AttributeError("dhcp is set to false, but gateway is not set")
            if not self.netmask:
                raise AttributeError("dhcp is set to false, but netmask is not set")


        net_config  = "ipv6.disable=1 netcfg/disable_autoconfig=true netcfg/use_autoconfig=false  netcfg/confirm_static=true"
        net_config = net_config + " netcfg/get_ipaddress={0} netcfg/get_gateway={1} netcfg/get_netmask={2} netcfg/get_nameservers={3} netcfg/get_domain=vmemperor".format(
            self.ip, self.gateway, self.netmask, self.dns1)
        # scenario set up
        scenario = self.get_scenario()
        return "auto=true console=hvc0 debian-installer/locale=en_US console-setup/layoutcode=us console-setup/ask_detect=false interface=eth0 %s netcfg/get_hostname=%s preseed/url=%s --" % (
            net_config, self.hostname, scenario)

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

    def set_os_kind(self, os_kind: str):
        super().set_os_kind(os_kind)
        try:
            debian_release = self.get_release(os_kind.split()[1])
            self.other_config['debian-release'] = debian_release
        except IndexError:
            pass

        if self.other_config['debian-release'] in self.HVM_RELEASES:
            self.other_config['convert-to-hvm'] = 'true'

    def set_install_url(self, url):

        if not url:
            url = 'http://ftp.ru.debian.org/debian/'

        self.other_config['install-repository'] = url
        self.other_config['default-mirror'] = url
        super().set_install_url(url)


class UbuntuOS(DebianOS):
    '''
    OS-specific parameters for Ubuntu
    '''
    HVM_RELEASES = ['artful',  'zesty', 'yakkety']
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


    def set_install_url(self, url):
        if not url:
            url = 'http://archive.ubuntu.com/ubuntu/'
        super().set_install_url(url)





class CentOS(GenericOS):
    """
    OS-specific parameters for CetOS
    """

    def set_scenario(self, url):
        self.scenario = self.set_kickstart(url)


    def pv_args(self):
        '''
        TODO: rewrite for CentOS
        :return:
        '''
        if self.dhcp:
            net_config = "netcfg/disable_dhcp=false"
        else:
            if not self.ip:
                raise AttributeError("dhcp is set to false, but ip is not set")
            if not self.gateway:
                raise AttributeError("dhcp is set to false, but gateway is not set")
            if not self.netmask:
                raise AttributeError("dhcp is set to false, but netmask is not set")
            net_config = " ip=%s::%s:%s" % (self.ip, self.gateway, self.netmask)


            if self.dns0:
                net_config = net_config + ":::off:%s" % self.dns0
                if self.dns1:
                    net_config = net_config + ":%s" % self.dns1

        # scenario set up
        scenario = self.get_scenario()
        return "auto=true console=hvc0 debian-installer/locale=en_US console-setup/layoutcode=us console-setup/ask_detect=false interface=eth0 %s netcfg/get_hostname=%s preseed/url=%s --" % (
            net_config, self.hostname, scenario)


class OSChooser:
    @classmethod
    def get_os(cls, os_kind, other_config):
        if os_kind.startswith('ubuntu'):
            os = UbuntuOS()
        elif os_kind.startswith('centos'):
            os = CentOS()
        elif os_kind.startswith('debian'):
            os = DebianOS()
        else:
            return None

        os.other_config = other_config
        os.set_os_kind(os_kind)
        return os

