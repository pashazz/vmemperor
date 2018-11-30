import copy
import json
import uuid

import rethinkdb as r
import tornado.ioloop
from rethinkdb import ReqlTimeoutError, ReqlDriverError
from tornado import gen
from tornado.options import options as opts

from authentication import AdministratorAuthenticator
from connman import ReDBConnection
from constants import need_exit
from exc import XenAdapterUnauthorizedActionException, EmperorException, XenAdapterAPIError
from handlers.rest.base import RESTHandler, auth_required
from quota import Quota
from xenadapter import XenAdapterPool
from xenadapter.template import Template
from xenadapter.vm import VM


class CreateVM(RESTHandler):
    _ASYNC_KEY = 'createvm'

    @auth_required
    def post(self):
        try:
            tmpl_name = self.get_argument('template')
            self.sr_uuid = self.get_argument('storage')
            self.net_uuid = self.get_argument('network')
            self.vdi_size = self.get_argument('vdi_size')
            int(self.vdi_size)
            self.ram_size = self.get_argument('ram_size')
            int(self.ram_size)
            self.name_label = self.get_argument('name_label')


        except Exception as e:
            self.set_status(400)
            self.log.error(f"Exception: {e}")
            self.write({'status': 'error', 'message': 'bad request'})
            self.finish()
            return

        with self.conn:
            db = r.db(opts.database)
            if not isinstance(self.user_authenticator, AdministratorAuthenticator): # Prevent provisioning if quotas are not met
                quota = Quota(self.user_authenticator)
                usage  = quota.space_left_after_disk_creation(int(self.vdi_size)*1024*1024, f'users/{self.user_authenticator.get_id()}')
                if usage and  usage < 0:
                    self.write({'status': 'storage quota exceeded', 'message': f'storage limit will be exceeded by {-usage} bytes'})
                    self.finish()
                    return


            tmpls = db.table('tmpls').run()
            self.template = None
            if not tmpl_name:
                self.set_status(400)
                self.write({'status': 'bad argument: template', 'message': 'bad request'})
                self.log.error("Client supplied no template")
                self.finish()

            for tmpl in tmpls:
                if tmpl['uuid'] == tmpl_name or \
                        tmpl['name_label'] == tmpl_name:
                    self.template = tmpl
                    break

            if not self.template:
                self.set_status(400)
                self.write({'status': 'no such template', 'message': 'template ' + tmpl_name})
                self.log.error("Client supplied wrong template name: {0}".format(tmpl_name))
                self.finish()
                return

            self.override_pv_args = self.get_argument('override_pv_args', None)
            self.mode = 'hvm' if self.template['hvm'] else 'pv'
            self.os_kind = self.template['os_kind'] if 'os_kind' in self.template and self.template['os_kind'] else None
            self.log.info("Creating VM: name_label %s; os_kind: %s" % (self.name_label, self.os_kind))
            if self.os_kind is None:
                self.iso = self.get_argument('iso')
                self.scenario_url = None
                self.mirror_url = None
                self.ip_tuple = None
                self.hostname = None
                self.username = None
                self.password = None
                self.fullname = None
                self.partition = None
            else:
                self.iso = None
                self.hostname = self.get_argument('hostname')
                self.mirror_url = self.get_argument('mirror_url', None)
                ip = self.get_argument('ip', '')
                gw = self.get_argument('gateway', '')
                netmask = self.get_argument('netmask', '')
                dns0 = self.get_argument('dns0', '')
                dns1 = self.get_argument('dns1', '')
                if not ip or not gw or not netmask:
                    self.ip_tuple = None
                else:
                    self.ip_tuple = [ip, gw, netmask]

                if dns0:
                    self.ip_tuple.append(dns0)
                if dns1:
                    self.ip_tuple.append(dns1)

                self.username = self.get_argument('username')
                self.password = self.get_argument('password')
                self.fullname = self.get_argument('fullname', default=None)
                self.partition = self.get_argument('partition', default='auto')
                try:
                    self.vcpus = self.get_argument('vcpus', default=1)
                except ValueError:
                    self.vcpus = 1


            self.taskid = str(uuid.uuid4())

            self._run_task = self.taskid  # for on_finish

            tornado.ioloop.IOLoop.current().run_in_executor(self.executor, self.createvm)
            self.write(json.dumps({'task': self.taskid}))
            self.finish()

    def insert_log_entry(self, uuid, state, message):
        write_in = {'id': self._run_task}
        write_in['uuid'] = uuid
        write_in['state'] = state
        write_in['message'] = message

        self.op.set_operation(None, write_in)
        self.log.info(f"STATE CHANGE: uuid: {uuid}, state: {state}, message: {message}")

    def createvm(self):
        """
        Create a new VM. Current user gets full permissions of newly created VM
        Arguments:
        template - template UUID or name_label
        storage - SR UUID
        network - network UUID
        vdi_size - size of Virtual Disk Image to install OS on, in megabytes
        ram_size - size of virtual RAM
        hostname - VM hostname
        name_label - VM human-readable name
        mirror_url - repository URL for auto-installation
        os_kind - OS type to install ('ubuntu <release name>', 'debian <release name>', 'centos')
        mode - VM type  'pv' (Paravirtualization) or 'hvm' (Hardware virtual machine)
        username - UNIX username of an account to be created
        password - password for said user account
        fullname - user account's full name
        ip: IP address for static IP configuration (do not specify if desire DHCP)
        gateway: Gateway for static IP configuration
        netmask: Netmask for static IP configuration
        dns0: First DNS server for static IP configuration
        dns1: Second DNS server for static IP configuration (optional)
        partition: how to partition a virtual disk image. Default: 'auto'. Parameters are separated with '-'. Available parameters are 'auto', 'mbr', 'gpt', 'lvm', 'swap' (requires size as next param) and sets by 3 params: 'mountpoint', 'size', 'filesystem'. Example: lvm-/-4096--/boot-1024-ext4-swap-2048. If filesystem is skipped, default fs is used.
        override_pv_args: override all kernel command-line arguments in PV mode with this line, if specified


        :return: UUID of newly created VM

        """
        with ReDBConnection().get_connection():
            try:
                self.op.set_operation(self.user_authenticator, {'id': self.taskid})

                def do_clone(auth):
                    tmpl = Template(auth, uuid=self.template['uuid'])
                    vm = tmpl.clone(self.name_label)
                    self.insert_log_entry(vm.uuid, 'cloned', f'cloned from {tmpl.uuid}')
                    vm.create(self.insert_log_entry,  self.sr_uuid, self.net_uuid,
                                   self.vdi_size, self.ram_size,
                                   self.hostname, self.mode, os_kind=self.os_kind, ip=self.ip_tuple,
                                   install_url=self.mirror_url,
                                   name_label=self.name_label, override_pv_args=self.override_pv_args, iso=self.iso,
                                   username=self.username, password=self.password, partition=self.partition,
                                   fullname=self.fullname, vcpus=self.vcpus)

                    ioloop = tornado.ioloop.IOLoop.current()
                    self.uuid = vm.uuid
                    # ioloop.add_callback(self.do_finalize_install)
                    ioloop.run_in_executor(self.executor, self.finalize_install)
                    log_message = """
                                       Created VM: UUID {uuid}
                                       Created by: {user} (of {auth})
                                       Name: {name_label}
                                       Full name: {fullname}
                                       SR: {sr_uuid}
                                       Network: {net_uuid}
                                       IP, Gateway, Netmask, DNS: {ip}
                                       VDI Size: {vdi_size}
                                       RAM Size: {ram_size}
                                       Hostname: {hostname}
                                       Username: {username}
                                       Password: {password}
                                       ISO: {iso}
                                       Partition scheme: {partition}
                                       """
                    self.actions_log.info(log_message.format(user=self.user_authenticator.get_name(),
                                                             auth=self.user_authenticator.__class__.__name__,
                                                             name_label=self.name_label, fullname=self.fullname,
                                                             sr_uuid=self.sr_uuid, net_uuid=self.net_uuid,
                                                             vdi_size=self.vdi_size, ram_size=self.ram_size,
                                                             hostname=self.hostname, username=self.username,
                                                             password=self.password,
                                                             iso=self.iso, partition=self.partition, ip=self.ip_tuple,
                                                             uuid=vm.uuid))

                do_clone(self.user_authenticator)
            except XenAdapterUnauthorizedActionException as ee:
                self.insert_log_entry(None, 'access denied', ee.message)
            except EmperorException as ee:
                self.insert_log_entry(None, 'error', ee.message)

    @gen.coroutine
    def do_finalize_install(self):
        yield self.finalize_install()

    # @run_on_executor
    def finalize_install(self):
        '''
        Watch if VM is halted and boot it once again. Update status accordingly

        :return:
        '''
        auth = copy.copy(self.user_authenticator)
        auth.xen = XenAdapterPool().get()

        conn = ReDBConnection().get_connection()
        with conn:
            self.log.debug("Set access rights for VM disks")
            db = r.db(opts.database)
            disks = db.table('vms').get(self.uuid).pluck('disks').run()['disks']

            self.log.info("Finalizing installation of VM %s" % self.uuid)

            state = db.table('vms').get(self.uuid).pluck('power_state').run()['power_state']
            if state != 'Running':
                self.insert_log_entry(self.uuid, 'failed',
                                      "failed to start VM for installation (low resources?). State: %s" % state)
                return

            self.insert_log_entry(self.uuid, 'installing','installing OS')
            cur = db.table('vms').get(self.uuid).changes().run()
            while True:
                try:
                    change = cur.next(wait=1)
                except ReqlTimeoutError:
                    if need_exit.is_set():
                        return
                    else:
                        continue
                except ReqlDriverError as e:
                    self.log.error(
                        f"ReQL error while trying to retrieve VM '{self.uuid}': install status: {e}")
                    return

                if change['new_val']['power_state'] == 'Halted':
                    try:
                        vm = VM(auth, uuid=self.uuid)
                        other_config = vm.get_other_config()
                        if 'convert-to-hvm' in other_config and other_config['convert-to-hvm']:
                            vm.convert('hvm')

                        vm.start_stop_vm(True)
                        self.insert_log_entry(self.uuid, "installed", "OS successfully installed")
                    except XenAdapterAPIError as e:
                        self.insert_log_entry(self.uuid, "failed", "failed to start after installation: %s" % e.message)
                    finally:
                        break