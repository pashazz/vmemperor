import atexit
from connman import ReDBConnection
from auth import dummy
from xenadapter import XenAdapter, XenAdapterPool
from xenadapter.template import Template
from xenadapter.vm import VM
from xenadapter.network import Network
from xenadapter.disk import ISO
import copy
import traceback
import inspect
import tornado.web
from tornado.escape import json_encode, json_decode
import tornado.httpserver
import tornado.iostream
import json
from dynamicloader import DynamicLoader
import configparser
import socket
from tornado import gen, ioloop
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
import base64
import pickle
import rethinkdb as r
from rethinkdb.errors import ReqlDriverError
from authentication import BasicAuthenticator
from loggable import Loggable
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from exc import *
import logging
from netifaces import ifaddresses, AF_INET
import uuid
from tornado.options import define, options as opts, parse_config_file
import queue
import threading
import datetime

from xmlrpc.client import DateTime as xmldt
from frozendict import frozendict
from authentication import AdministratorAuthenticator
from tornado.websocket import *
import asyncio
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
#Objects with ACL enabled
objects = [VM]

user_table_ready = threading.Event()

def table_drop(db, table_name):
    try:
        db.table_drop(table_name).run()
    except r.errors.ReqlOpFailedError as e:
        # TODO make logging
        print(e.message)
        r.db('rethinkdb').table('table_config').filter(
            {'db': opts.database, 'name': table_name}).delete().run()


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, xmldt):
            t =  datetime.datetime.strptime(o.value, "%Y%m%dT%H:%M:%SZ")
            return t.strftime("%d.%m.%Y, %H:%M:%S")
        

        return super().default(o)




def CHECK_ER(ret):
    if ret['errors']:
        raise ValueError('Failed to modify data: {0}'.format(ret['first_error']))
    if ret['skipped']:
        raise ValueError('Failed to modify data: skipped - {0}'.format(ret['skipped']))

def auth_required(method):
    def decorator(self, *args, **kwargs):
        user = HandlerMethods.get_current_user(self)
        if not user:
            self.write({'status': 'error', 'message': 'not authorized'});
        else:
            self.user_authenticator  = pickle.loads(user)
            self.user_authenticator.xen = XenAdapter({**opts.group_dict('xenadapter'), **opts.group_dict('rethinkdb')})
            self.xen = self.user_authenticator.xen
            return method(self, *args, **kwargs)

    return decorator




class HandlerMethods(Loggable):
    def init_executor(self, executor):
        self.executor = executor
        self.init_log()
        self.conn = ReDBConnection().get_connection()



    # def init_xen(self, auth=None) -> XenAdapter:
    #    opts_dict = {}
    #    opts_dict.update(opts.group_dict('xenadapter'))
    #    opts_dict.update(opts.group_dict('rethinkdb'))
    #    xen = XenAdapter(opts_dict, auth if auth else self.user_authenticator)
    #    return xen

    def get_current_user(self):
        return self.get_secure_cookie("user")


class BaseHandler(tornado.web.RequestHandler, HandlerMethods):

    def initialize(self, executor):
        self.init_executor(executor)
        super().initialize()

    def prepare(self):
        super().prepare()
        if not 'Content-Type' in self.request.headers:
            return
        content_type = self.request.headers['Content-Type'].split(';')
        if content_type[0] == 'application/json':
            encoding = 'utf-8'
            try:
                encoding = content_type[1].split('=')[1]
            except:
                pass

            json_data = json.loads(self.request.body.decode(encoding=encoding))
            json_data_lists = {k : [v] for k, v in json_data.items()}
            self.request.arguments.update(json_data_lists)

    def get_current_user(self):
        return self.get_secure_cookie("user")


    def try_xenadapter(self, func, post_hook = None):
        '''
        Call a xenadapter method, handle exceptions
        :param func:
        :param post_hook: call this function with a xenadapter method's return value and an authenticator object  as arguments argument (optional)        :return:
        '''
        auth = self.user_authenticator
        try:
            ret = func(auth)

        except XenAdapterUnauthorizedActionException as ee:
            self.set_status(403)
            self.write(json.dumps({'status': 'not allowed', 'details': ee.message}))
            self.finish()


        except EmperorException as ee:
            self.set_status(400)
            self.write(json.dumps({'status': 'error', 'details': ee.message}))
            self.finish()

        else:
            if ret:
                self.write(ret)
            else:
                self.write(json.dumps({'status': 'ok'}))


            self.finish()
            try:
                if post_hook:
                    post_hook(ret, auth)
            except EmperorException as e:
                self.log.error("try_xenadapter: exception catched in post_hook: %s" % e.message)


class BaseWSHandler(WebSocketHandler, HandlerMethods):
    def initialize(self, executor):
        self.init_executor(executor)
        super().initialize()





class AuthHandler(BaseHandler):

    def initialize(self, executor, authenticator):
        '''

        :param executor:
        :param authenticator: authentication object derived from BasicAuthenticator
        :return:
        '''
        super().initialize(executor)
        self.authenticator = authenticator()

    def post(self):
        '''
        Authenticate as a regular user
        params:
        :param username
        :param password
        :return:
        '''

        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        try:
            self.authenticator.check_credentials(username=username, password=password, log=self.log)
        except AuthenticationException:
            self.write(json.dumps({"status": 'error', 'message' :  "wrong credentials"}))
            self.set_status(401)
            return


        self.write(json.dumps({}))
        self.set_secure_cookie("user", pickle.dumps(self.authenticator))



"""
dbms - RethinkDB
db is used as cache
different users should see different info (i.e. only vms created by that user)


views should return info in json format
errors should be returned in next format: {'status': 'error', 'details': string, 'reason': string}

"""


class Test(BaseHandler):

    @run_on_executor
    def heavy_task(self):
        return {'status': 'ok'}

    @gen.coroutine
    def get(self):
        res = yield self.heavy_task()
        self.write(json.dumps(res))


class AdminAuth(BaseHandler):
    def post(self):
        '''
        Authenticate using XenServer auth system directly (as admin)
        :param username
        :param password
        :return:
        '''
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        try:
            authenticator = AdministratorAuthenticator()
            authenticator.check_credentials(username=username, password=password, log=self.log)
        except AuthenticationException:
            self.write(json.dumps({"status": 'error', 'message': "wrong credentials"}))
            self.set_status(401)
            return

        self.set_secure_cookie("user", pickle.dumps(authenticator))



class LogOut(BaseHandler):
    def get(self):
        self.clear_cookie('user')
        #self.redirect(self.get_argument("next", "/login"))
        self.write({'status': 'ok'})


class VMList(BaseWSHandler):
    @auth_required
    @tornado.web.asynchronous
    def open(self):
        with self.conn:
            db  = r.db(opts.database)
            self.db = db
            if isinstance(self.user_authenticator, AdministratorAuthenticator): #get all vms
                self.changes_query = db.table('vms').changes(include_types=True, include_initial=True)

            else:
                user_table_ready.wait()
                userid = str(self.user_authenticator.get_id())
                # Get all changes from VMS table (only changes, not removals) and mark them as 'state' changes
                # Plus get all initial values and changes from vms_user table and mark them as 'access' changes
                #
                self.changes_query = self.db.table('vms').changes(include_types=True).filter(
                    r.row['type'].eq(r.expr('change')).or_(r.row['type'].eq('remove')))\
                    .merge({'changed':'state'}).union(
                    self.db.table('vms_user').get_all('users/%s' % userid, index='userid').without('id').
                    changes(include_types=True, include_initial=True).merge(r.branch(r.row['type'].eq(r.expr('initial')).or_(r.row['type'].eq(r.expr('add'))),
                                                                                     self.db.table('vms').get(r.row['new_val']['ref']),
                                                                                     {'changed': 'access'})))

                for group in self.user_authenticator.get_user_groups():
                    group = str(group)

                    self.changes_query = self.changes_query.union(self.db.table('vms_user').get_all( 'groups/%s' % group, index='userid').without('id')
                                             .changes(include_types=True, include_initial=True).merge(r.branch(r.row['type'].eq(r.expr('initial')).or_(r.row['type']).eq(r.expr('add')),
                                                                                     self.db.table('vms').get(r.row['new_val']['ref']),
                                                                                     {'changed': 'access'})))

            ioloop = tornado.ioloop.IOLoop.instance()
            ioloop.run_in_executor(self.executor, self.items_changes)



    @gen.coroutine
    def do_items_changes(self):
        #asyncio.set_event_loop(asyncio.new_event_loop())
        #yield self.items_changes()
        pass


    #@run_on_executor
    def items_changes(self):
        '''
        Monitor for User table (access rules) items' changes with the following considerations:
        - We only monitor for changes in vms table. We need to filter them manually, as there's no way for such
        complicated filter in ReQL. These have 'changed' == 'state' and only 'type' == 'change'
        - We know about new entries in vms table because vms_user table provides that for us. Every addition to vms_user
        gets merged with the corresponding record from vms
        - All entries from vms_user table have 'changed' == 'access'
        - When
        '''
        conn = ReDBConnection().get_connection()
        with conn:
            invalid_refs = set()
            cur = None
            def create_cursor():
                nonlocal cur
                cur = self.changes_query.run()

            def check_access_entry(access_entry):
                if access_entry['userid'] == 'users/{0}'.format(self.user_authenticator.get_id()):
                    return True

                for group in self.user_authenticator.get_user_groups():
                    if access_entry['userid'] == 'groups/{0}'.format(group):
                        return True

                return False

            self.log.debug('Changes query: {0}'.format(self.changes_query))
            create_cursor()
            self.cur = cur
            for change in cur:
                if not self.ws_connection:
                    return
                if not isinstance(self.user_authenticator, AdministratorAuthenticator):
                    if 'changed' in change and change['changed'] == 'state': #Here we may have entries that we have to filter by user/group
                        if change['new_val']:
                            record = change['new_val']
                        elif change['type'] == 'remove':
                            invalid_refs.add(change['old_val']['ref'])
                            record = change['old_val']
                        else:
                            record = change

                        for access_entry in record['access']:
                            if check_access_entry(access_entry):
                                break
                        else: #Normal quit, not via break
                            continue #filter this entry


                    if change['type'] in ('initial', 'add'): #these are access only
                        del change['new_val'] # we merge them with entries from vms, we don't need new_val
                        if 'old_val' in change:
                            del change['old_val']

                    elif change['type'] == 'remove':
                        del change['new_val'] #always null

                        if change['old_val']['ref'] in invalid_refs:
                            continue #filter out these 'junk' messages as the entry has already been removed from vms




                self.write_message(json.dumps(change))

            return

    def on_close(self):
        if hasattr(self, 'cur'):
            self.log.info("Closing websocket connection: {0}".format(self.ws_connection))

            self.cur.close()


class PoolListPublic(BaseHandler):
    def get(self):
        '''

        :return: list of pools available for login (ids only)
        '''
        self.write(json.dumps([{'id': 1}]))


class PoolList(BaseHandler):
    @auth_required
    def get(self):
        """
        List of XenServer pools
         Format: list of http://xapi-project.github.io/xen-api/classes/pool.html ('fields')
         """
        # read from db
        self.conn.repl()
        table = r.db(opts.database).table('pools')
        list = [x for x in table.run()]

        self.write(json.dumps(list))


class TemplateList(BaseHandler):
    @auth_required
    def get(self):
        """
        List of available templates
        format:
        [{'ref': template ref,
          'name_label': template human-readable name,
          'hvm': True if this is an HVM template, False if PV template
          },...]

         """

        # read from db
        with self.conn:
            table = r.db(opts.database).table('tmpls')
            list = [x for x in table.run()]

            self.write(json.dumps(list))

class ISOList(BaseHandler):
    @auth_required
    def get(self):
        """
        List of available ISOs
        format:
        [{'location': 'file name or device file path',
          'name_description': 'human readable description',
          'name_label': file name OR device name if it's a real CD device,
          'ref': 'db199908-f133-4c7f-b06c-10ac2784ad5d'}]
         """

        # read from db
        with self.conn:
            table = r.db(opts.database).table('isos')
            list = [x for x in table.run()]

            self.write(json.dumps(list))


class CreateVM(BaseHandler):

    @auth_required
    @tornado.web.asynchronous
    def post(self):
        """
        Create a new VM. Current user gets full permissions of newly created VM
        Arguments:
        template - template ref or name_label
        storage - SR ref
        network - network ref
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


        :return: ref of newly created VM

        """

        try:
            tmpl_name = self.get_argument('template')
            self.sr_ref = self.get_argument('storage')
            self.net_ref = self.get_argument('network')
            self.vdi_size = self.get_argument('vdi_size')
            self.ram_size = self.get_argument('ram_size')
            self.hostname = self.get_argument('hostname')
            self.name_label = self.get_argument('name_label')
            self.mirror_url = self.get_argument('mirror_url')

        except:
            self.write_error(status_code=404)
            return
        with self.conn:
            db = r.db(opts.database)
            tmpls = db.table('tmpls').run()
            for tmpl in tmpls:
                if tmpl['ref'] == tmpl_name or \
                tmpl['name_label'] == tmpl_name:
                    tmpl_ref = tmpl['ref']
                    break

            if not tmpl_ref:
                raise ValueError('Wrong template name: {0}'.format(tmpl_name))

            self.os_kind = self.get_argument('os_kind', None)
            self.override_pv_args = self.get_argument('override_pv_args', None)
            self.mode = self.get_argument('mode')
            self.log.info("Creating VM: name_label %s; os_kind: %s" % (self.name_label, self.os_kind))
            ip = self.get_argument('ip', '')
            gw = self.get_argument('gateway', '')
            netmask = self.get_argument('netmask', '')
            dns0 = self.get_argument('dns0', '')
            dns1 = self.get_argument('dns1', '')
            if not ip or not gw or not netmask:
                self.ip_tuple = None
            else:
                self.ip_tuple = [ip,gw,netmask]

            if dns0:
                self.ip_tuple.append(dns0)
            if dns1:
                self.ip_tuple.append(dns1)

            kwargs = {}
            if 'ubuntu' in self.os_kind or 'centos' in self.os_kind or 'debian' in self.os_kind:
                # see os_kind-ks.cfg
                kwargs['hostname'] = self.get_argument('hostname', default='xen_vm')
                kwargs['username'] = self.get_argument('username', default='')
                kwargs['password'] = self.get_argument('password')
                kwargs['mirror_url'] = self.mirror_url
                kwargs['fullname'] = self.get_argument('fullname')
                kwargs['ip'] = ip
                kwargs['partition'] = self.get_argument('partition', default='auto')

                if ip:
                    kwargs['gateway'] = gw
                    kwargs['netmask'] = netmask
                    if dns0:
                        kwargs['dns0'] = dns0
                    if dns1:
                        kwargs['dns1'] = dns1
            self.scenario_url = 'http://'+ opts.vmemperor_url + ':' + str(opts.vmemperor_port) + XenAdapter.AUTOINSTALL_PREFIX + "/" + self.os_kind.split()[0] + "?" + "&".join(
                ('{0}={1}'.format(k, v) for k, v in kwargs.items()))
            self.log.info("Scenario URL generated: %s", self.scenario_url)

            def clone_post_hook(return_value, auth):
                vm =  VM.create(auth, return_value, self.sr_ref, self.net_ref, self.vdi_size, self.ram_size,
                                         self.hostname, self.mode, self.os_kind, self.ip_tuple, self.mirror_url,
                                         self.scenario_url, self.name_label, False, self.override_pv_args)

                ioloop = tornado.ioloop.IOLoop.current()
                self.ref = vm.ref
                #ioloop.add_callback(self.do_finalize_install)
                ioloop.run_in_executor(self.executor, self.finalize_install)



            def do_clone(auth):
                tmpl = Template(auth, ref=tmpl_ref)
                vm = tmpl.clone(self.name_label)
                return vm.ref


            self.try_xenadapter(do_clone, post_hook=clone_post_hook)

    @gen.coroutine
    def do_finalize_install(self):
        yield self.finalize_install()

    #@run_on_executor
    def finalize_install(self):
        '''
        Watch if VM is halted and boot it once again. Update status accordingly

        :return:
        '''
        auth = copy.copy(self.user_authenticator)
        auth.xen = XenAdapterPool().get()

        conn = ReDBConnection().get_connection()
        with conn:
            self.log.info("Finalizing installation of VM %s" % self.ref)
            db = r.db(opts.database)
            state = db.table('vms').get(self.ref).pluck('power_state').run()['power_state']
            if state != 'Running':
                auth.xen.insert_log_entry(self.ref, 'failed', "failed to start VM for installation (low resources?). State: %s" % state)
                return

            cur = db.table('vms').get(self.ref).changes().run()
            for change in cur:
                if change['new_val']['power_state'] == 'Halted':
                    try:
                        vm = VM(auth, ref=self.ref)
                        vm.start_stop_vm(True)
                    except XenAdapterAPIError as e:
                        auth.xen.insert_log_entry(self.ref, "failed", "failed to start after installation: %s" % e.message)
                    else:
                        auth.xen.insert_log_entry(self.ref, "installed", "OS successfully installed")
                    break









class NetworkList(BaseHandler):
    @auth_required
    def get(self):
        """
        Format: list of fields of http://xapi-project.github.io/xen-api/classes/network.html
        """
        # read from db
        self.conn.repl()
        table = r.db(opts.database).table('nets')
        list = [x for x in table.run()]

        self.write(json.dumps(list))


class ConvertVM(BaseHandler):
    @auth_required
    def post(self):
        vm_ref =self.get_argument('ref')
        mode = self.get_argument('mode')
        self.try_xenadapter(lambda auth: VM(auth, ref=vm_ref).convert(mode))

class EnableDisableTemplate(BaseHandler):
    @auth_required
    def post(self):
        """
         Enable or disable template
         Arguments:
             ref: VM ref
             enable: True if template needs to be enabled
         """
        ref = self.get_argument('ref')
        enable = self.get_argument('enable')


        self.try_xenadapter( lambda auth: Template(auth, ref=ref).enable_disable(bool(enable)))




class AttachDetachDisk(BaseHandler):
    @auth_required
    def post(self):
        '''
        Attach or detach VDI from/to VM
        Arguments:
            vm_ref: VM ref
            vdi_ref: VDI ref
            enable: True if to attach disk, False if to detach.
        '''
        with self.conn:
            vm_ref = self.get_argument('vm_ref')
            vdi_ref = self.get_argument('vdi_ref')
            enable = self.get_argument('enable')
            def xen_call(auth):
                if enable:
                    return auth.xen.attach_disk(vm_ref, vdi_ref)
                else:
                    auth.xen.detach_disk(vm_ref, vdi_ref)

            self.try_xenadapter(xen_call)








class ConnectVM(BaseHandler):
    @auth_required
    def post(self):
        '''
        Connect a VM to a Network. Requires permission "attach"
        Arguments:
        vm_ref: VM ref
        net_ref: Network ref
        ip: undocumented. Lera?
        :return:
        '''

        vm_ref = self.get_argument('vm_ref')
        net_ref = self.get_argument('net_ref')
        ip = self.get_argument('ip', default=None)
        self.try_xenadapter(lambda : xen.connect_vm(vm_ref, net_ref, ip))


class AnsibleHooks:
    # todo
    pass


class VMAbstractHandler(BaseHandler):
    '''
    Abstact handler for VM requests
    requires: function self.get_data returning something we can write
              attribute self.access - access mode
    provides: self.ref <- vm_ref

    '''
    @auth_required
    def post(self):
        vm_ref = self.get_argument('ref')
        self.ref = vm_ref
        try:
            self.vm = VM(self.user_authenticator, ref=vm_ref)
        except XenAdapterAPIError as e:
            self.set_status(400)
            self.write({'status' : 'bad request', 'message' : e.message})
            return
        try:
            self.vm.check_access(self.access)
        except XenAdapterUnauthorizedActionException as e:
            self.set_status(403)
            self.write({'status':'access denied', 'message' : e.message})
            return


        ret = self.get_data()
        if ret:
            self.write(ret)

    def get_data(self):
        '''return answer information (if everything is OK). Else use set_status and write'''
        raise NotImplementedError()

class SetAccessHandler(BaseHandler):
    @auth_required
    def post(self):
        with self.conn:
            ref = self.get_argument('ref')
            type = self.get_argument('type')
            action = self.get_argument('action')
            revoke = self.get_argument('revoke', False)
            user = self.get_argument('user', default=None)
            if not user:
                group = self.get_argument('group')
            else:
                group = None
            type_obj = None
            for obj in objects:
                if obj.__name__ == type:
                    type_obj = obj
                    break
            else:
                self.set_status(400)
                self.write({'status' : 'bad request', 'message' : 'unsupported type %s' % type})
                return

            try:
                self.target = type_obj(self.user_authenticator, ref=ref)
                self.target.check_access(action)
                self.target.manage_actions(action, revoke, user, group)
            except XenAdapterAPIError as e:
                self.set_status(400)
                self.write({'status': 'bad request', 'message': e.message})
                return
            except XenAdapterUnauthorizedActionException as e:
                self.set_status(403)
                self.write({'status': 'access denied', 'message': e.message})
                return

class GetAccessHandler(BaseHandler):
    @auth_required
    def post(self):
        with self.conn:

            ref = self.get_argument('ref')
            type = self.get_argument('type')
            type_obj = None
            for obj in objects:
                if obj.__name__ == type:
                    type_obj = obj
                    break
            else:
                self.set_status(400)
                self.write({'status': 'bad request', 'message': 'invalid type: %s' % type})
                return
            try:
                type_obj(self.user_authenticator, ref=ref).check_access(None)
            except XenAdapterAPIError as e:
                self.set_status(400)
                self.write({'status': 'bad request', 'message': e.message})
                return

            except XenAdapterUnauthorizedActionException as e:
                self.set_status(403)
                self.write({'status': 'access denied', 'message': e.message})
                return

            db = r.db(opts.database)
            self.write(db.table(type_obj.db_table_name).get(ref).pluck('access').run())




class InstallStatus(VMAbstractHandler):

    access = 'launch'

    def get_data(self):
        db = r.db(opts.database)
        try:
            d = db.table('vm_logs').filter({'ref': self.ref}).max('time').run()
            d['time'] = d['time'].isoformat()
            return d
        except:
            self.set_status(500)
            self.write({'status': 'database error/no info'})
            return

class VMInfo(VMAbstractHandler):

    access = 'launch'

    def get_data(self):
        db = r.db(opts.database)
        try:
            d = db.table('vms').get(self.ref).run()
            return d
        except:
            self.set_status(500)
            self.write({'status' : 'database error/no info'})
            return

class DestroyVM(VMAbstractHandler):

    access = 'destroy'

    def get_data(self):
        ref = self.get_argument('ref')

        self.try_xenadapter(lambda auth: VM(auth, ref=ref).destroy_vm())

class StartStopVM(VMAbstractHandler):

    access = 'launch'

    def get_data(self):
        ref = self.get_argument('ref')
        enable = self.get_argument('enable')
        if enable not in ('True', 'False'):
            self.set_status(400)
            self.write({'status': 'invalid enable value: expected True/False'})
            return

        self.try_xenadapter(lambda auth: VM(auth, ref=ref).start_stop_vm(enable == 'True'))


class VNC(VMAbstractHandler):

    access = 'launch'

    def get_data(self):
        '''
        Get VNC console url that supports HTTP CONNECT method. Requires permission 'launch'
        Arguments:
            ref: VM ref

        '''

        vm_ref = self.get_argument('ref')

        def get_vnc(auth: BasicAuthenticator):
            url = VM(auth, ref=vm_ref).get_vnc()
            url_splitted = list(urlsplit(url))
            url_splitted[0] = 'http'
            url_splitted[1] = opts.vmemperor_url + ":" + str(opts.vmemperor_port)
            url = urlunsplit(url_splitted)
            return url

        self.try_xenadapter(get_vnc)


class AttachDetachIso(VMAbstractHandler):

    access = 'attach'

    def get_data(self):
        '''
        Attach/detach ISO from/to vm
        Arguments:
            ref: VM ref
            iso_ref: ISO ref
            action: 'attach' or 'detach'
        :return:
        '''
        self.log.info("check if ISO ref is valid")
        iso_ref = self.get_argument('iso_ref')
        action = self.get_argument('action')
        if action == 'attach':
            is_attach = True
        elif action == 'detach':
            is_attach = False
        else:
            self.set_status(400)
            self.write({'status': 'error', 'message' : 'invalid parameter "action": should be one of '
                                                       '"attach", "detach", got %s' % action })
            return

        db = r.db(opts.database)
        res = db.table('isos').get(iso_ref).run()
        if res:
            self.log.info("ref %s valid, attaching/detaching..." % iso_ref)
            def attach(auth : BasicAuthenticator):
                iso = ISO(ref=iso_ref, auth=auth)
                if is_attach:
                    iso.attach(self.vm)
                else:
                    iso.detach(self.vm)


            self.try_xenadapter(attach)
        else:
            self.log.info("ref %s invalid, not attaching..." % iso_ref)
            self.set_status(400)
            self.write({'status':'error', 'message': 'invalid ref iso_ref'})
            return



class EventLoop(Loggable):
    """every n seconds asks all vms about their status and updates collections (dbs, tables)
    of corresponding user, if they are logged in (have open connection to dbms notifications)
     and admin db if admin is logged in"""


    def __init__(self, executor, authenticator):

        self.init_log()

        self.executor = executor
        self.authenticator = authenticator
        try:
            authenticator.xen = XenAdapter({**opts.group_dict('xenadapter'), **opts.group_dict('rethinkdb')})
        except XenAdapterConnectionError as e:
            raise RuntimeError("XenServer not reached")

        conn = ReDBConnection().get_connection()
        with conn:
            if opts.database not in r.db_list().run():
                r.db_create(opts.database).run()
            self.db = r.db(opts.database)
            tables = self.db.table_list().run()
            self.xen = XenAdapter({**opts.group_dict('xenadapter'), **opts.group_dict('rethinkdb')})
            # required = ['vms', 'tmpls', 'pools', 'nets']
            if 'vms' in tables:
                self.db.table('vms').delete().run()
            if 'vms' not in tables:
                self.db.table_create('vms', durability='soft', primary_key='ref').run()
                vms = VM.init_db(authenticator)
                CHECK_ER(self.db.table('vms').insert(vms, conflict='error').run())
                #self.db.table('vms').index_create('user').run()
                #self.db.table('vms').index_wait('user').run()
            else:
                vms = VM.init_db(authenticator)
                CHECK_ER(self.db.table('vms').insert(vms, conflict='update').run())



            if 'isos' not in tables:
                self.db.table_create('isos', durability='soft', primary_key='ref').run()
                isos = ISO.init_db(authenticator)
                #isos = self.xen.list_isos()
                CHECK_ER(self.db.table('isos').insert(isos, conflict='error').run())
            else:
                isos = ISO.init_db(authenticator)
                #isos = self.xen.list_isos()
                CHECK_ER(self.db.table('isos').insert(isos, conflict='update').run())

            if 'tmpls' not in tables:
                self.db.table_create('tmpls', durability='soft', primary_key='ref').run()
            #    tmpls = self.xen.list_templates().values()
                tmpls = Template.init_db(authenticator)
                CHECK_ER(self.db.table('tmpls').insert(list(tmpls), conflict='error').run())
            else:
             #   tmpls = self.xen.list_templates().values()
                tmpls = Template.init_db(authenticator)
                CHECK_ER(self.db.table('tmpls').insert(list(tmpls), conflict='update').run())
          #  if 'pools' not in tables:
          #      self.db.table_create('pools', durability='soft', primary_key='ref').run()
          #      pools = self.xen.list_pools().values()
          #      CHECK_ER(self.db.table('pools').insert(list(pools), conflict='error').run())
          #  else:
          #      pools = self.xen.list_pools().values()
          #      CHECK_ER(self.db.table('pools').insert(list(pools), conflict='update').run())
            if 'nets' not in tables:
                self.db.table_create('nets', durability='soft', primary_key='ref').run()
                nets = Network.init_db(authenticator)
                CHECK_ER(self.db.table('nets').insert(list(nets), conflict='error').run())
            else:
                nets = Network.init_db(authenticator)
                # nets = self.xen.list_networks().values()
                CHECK_ER(self.db.table('nets').insert(list(nets), conflict='update').run())

            del authenticator.xen


    @run_on_executor
    def do_access_monitor(self):
        conn = ReDBConnection().get_connection()
        log = self.create_additional_log('AccessMonitor')
        with conn:
            query = self.db.table(objects[0].db_table_name).pluck('ref', 'access')\
                .merge({'table' : objects[0].db_table_name}).changes()

            table_list = self.db.table_list().run()
            def initial_merge(table):
                nonlocal table_list
                table_user = table + '_user'
                if table_user in table_list:
                    self.db.table_drop(table_user).run()



                self.db.table_create(table_user, durability='soft').run()
                self.db.table(table_user).index_create('ref_and_userid', [r.row['ref'], r.row['userid']]).run()
                self.db.table(table_user).index_wait('ref_and_userid').run()
                self.db.table(table_user).index_create('userid', r.row['userid']).run()
                self.db.table(table_user).index_wait('userid').run()
                # no need yet
                #self.db.table(table_user).index_create('ref', r.row['ref']).run()
                #self.db.table(table_user).index_wait('ref').run()

                CHECK_ER(self.db.table(table_user).insert(
                    self.db.table(table).pluck('access', 'ref').filter(r.row['access'] != []).\
                    concat_map(lambda acc: acc['access'].merge({'ref':acc['ref']}))).run())


            i = 0
            while i < len(objects):
                initial_merge(objects[i].db_table_name)

                if i > 0:
                    query.union(self.db.table(objects[i].db_table_name).pluck('ref', 'access')\
                                    .merge({'table': objects[i].db_table_name}).changes())
                i += 1

            #indicate that vms_user table is ready
            user_table_ready.set()
            cur = query.run()

            def ref_delete(table_user, ref):
                self.db.table(table_user).filter({'ref' : ref}).delete().run()


            for record in cur:

                if record['new_val']: #edit
                    ref = record['new_val']['ref']
                    table = record['new_val']['table']
                    access = record['new_val']['access']
                    table_user = table + '_user'


                    if record['old_val']:
                        access_to_remove = \
                            set((frozendict(x) for x in record['old_val']['access'])) -\
                             set((frozendict(x) for x in access))
                        for item in access_to_remove:
                            CHECK_ER(self.db.table(table_user).get([record['old_val']['ref'], item['userid']], index='ref_and_userid').delete().run())
                    log.info("Modifying access rights for %s (table %s): %s" % (ref, table, json.dumps(access)))
                    if not record['old_val']:
                        for item in access:
                            CHECK_ER(self.db.table(table_user).insert(r.expr(item).merge({'ref' : ref})).run())
                    else:
                        access_diff = set((frozendict(x) for x in access)) -\
                                      set((frozendict(x) for x in record['old_val']['access']))

                        for item in access_diff:
                            CHECK_ER(self.db.table(table_user).insert(r.expr(item).merge({'ref' : ref} )).run())



                else:
                    ref = record['old_val']['ref']
                    table = record['old_val']['table']
                    table_user = table + '_user'
                    log.info("Deleting access rights for %s (table %s)" % (ref, table))
                    ref_delete(table_user, ref)

            return

    @gen.coroutine
    def access_monitor(self):
        yield self.do_access_monitor()


    @run_on_executor
    def process_xen_events(self):
        from XenAPI import  Failure

        self.authenticator.xen = XenAdapterPool().get()
        xen = self.authenticator.xen
        event_types = ["*"]
        token_from = ''
        timeout=1.0

        xen.api.event.register(["*"])
        conn = ReDBConnection().get_connection()
        with conn:


            while True:
                #pass
                try:
                    event_from_ret = xen.api.event_from(event_types, token_from, timeout)
                    events = event_from_ret['events']
                    token_from = event_from_ret['token']

                    for event in events:
                        if (opts.log_events and event['class'] in opts.log_events.split(',')) or not opts.log_events:
                            self.log.info("Event: %s" % json.dumps(event, cls=DateTimeEncoder))
                        #similarly to list_vms -> process
                        if event['class'] == 'vm':
                            ev_class = VM # use methods filter_record, process_record (classmethods)
                        else: # Implement ev_classes for all types of events
                            continue



                        ev_class.process_event(self.authenticator, event, self.db, self.authenticator.__name__)





                except Failure as f:
                    if f.details == [ "EVENTS_LOST" ]:
                       self.log.warning("Reregistering for events")
                       xen.api.event.register(["*"])




    @gen.coroutine
    def run_xen_queue(self):
        yield self.process_xen_events()



def event_loop(executor, delay = 1000, authenticator=None, ioloop = None):
    if not ioloop:
        ioloop = tornado.ioloop.IOLoop.instance()

    loop_object = EventLoop(executor, authenticator)
    #tornado.ioloop.PeriodicCallback(loop_object.vm_list_update, delay).start()  # read delay from ini
    ioloop.add_callback(loop_object.run_xen_queue)
    future = ioloop.run_in_executor(executor, loop_object.do_access_monitor)

    return ioloop



class AutoInstall(BaseHandler):
    def get(self, os_kind):
        '''
        This is used by CreateVM
        :param os_kind:
        :return:
        '''
        if os_kind == 'test':
            self.render("templates/installation-scenarios/test.cfg")
            return
        hostname = self.get_argument('hostname', default='xen_vm')
        username = self.get_argument('username', default='')
        password = self.get_argument('password')
        mirror_url = self.get_argument('mirror_url')
        fullname = self.get_argument('fullname')
        ip = self.get_argument('ip', default='')
        gateway = self.get_argument('gateway', default='')
        netmask = self.get_argument('netmask', default='')
        dns0 = self.get_argument('dns0', default='')
        dns1 = self.get_argument('dns1', default='')
        part = self.get_argument('partition').split('-')
        partition = {'method': 'regular',
                     'mode': 'mbr',
                     'expert_recipe': [],
                     'swap' : ''}
        if part[0] == 'auto':
            part.remove('auto')
        if 'swap' not in part and 'centos' not in os_kind:
            partition['swap'] = '2048'
        if 'swap' in part:
            ind = part.index('swap')
            partition['swap'] = part[ind + 1]
            part.remove('swap')
            part.remove(part[ind])
        if 'mbr' in part:
            part.remove('mbr')
        if 'gpt' in part:
            partition['mode'] = 'gpt'
            part.remove('gpt')
        if 'lvm' in part:
            partition['method'] = 'lvm'
            part.remove('lvm')
            if '/boot' not in part:
                raise ValueError("LVM partition require boot properties")
        partition['expert_recipe'] = [{'mp': part[i + 0], 'size': part[i + 1], 'fs': part[i + 2]}
                for i in range(0, len(part), 3)]
        if 'ubuntu' in os_kind or 'debian' in os_kind:
            mirror_url = mirror_url.split('http://')[1]
            mirror_path = mirror_url[mirror_url.find('/'):]
            mirror_url = mirror_url[:mirror_url.find('/')]
            filename = 'debian.jinja2'
            # filename = 'ubuntu-ks.cfg'
            # mirror_path = ''
        if 'centos' in os_kind:
            for part in partition['expert_recipe']:
                if part['mp'] is "/":
                    part['name'] = 'root'
                else:
                    part['name'] = part['mp'].replace('/','')
            filename = 'centos-ks.cfg'
            mirror_path = ''
        if not filename:
            raise ValueError("OS {0} doesn't support autoinstallation".format(os_kind))
        # filename = 'raid10.cfg'
        self.render("templates/installation-scenarios/{0}".format(filename), hostname = hostname, username = username,
                    fullname=fullname, password = password, mirror_url=mirror_url, mirror_path=mirror_path, ip=ip, gateway=gateway, netmask=netmask, dns0=dns0, dns1=dns1, partition=partition)

class ConsoleHandler(BaseHandler):
    SUPPORTED_METHODS = {"CONNECT"}

    def initialize(self,executor):
        super().initialize(executor)
        url = urlparse(opts.url)
        username = opts.username
        password = opts.password
        if ':' in url.netloc:
            host, port = url.netloc.split(':')
        else:
            host = url.netloc
            port = 80 #TODO: AS FOR NOW ONLY HTTP IS SUPPORTED

        self.host = host
        self.port = int(port)
        self.auth_token = base64.encodebytes('{0}:{1}'.format
                                             (username,
                                              password).encode())




    @auth_required
    def connect(self):
        '''
        This method proxies CONNECT calls to XenServer
        '''
        client_stream = self.request.connection.stream
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_stream = tornado.iostream.IOStream(sock)

        def connect_callback():
            lines =[
                'CONNECT {0} HTTP/1.1'.format(self.request.uri), #HTTP 1.1 creates Keep-alive connection
                'Host: {0}'.format(self.host),
             #   'Authorization: Basic {0}'.format(self.auth_token),
            ]
            server_stream.write('\r\n'.join(lines).encode())
            server_stream.write(b'\r\nAuthorization: Basic ' + self.auth_token)
            server_stream.write(b'\r\n\r\n')
            server_stream.read_until_close(streaming_callback=server_read)

        def server_read(data):
            if not data:
                client_stream.close()
            else:
                client_stream.write(data)


        def client_read(data):
            if not data:
                server_stream.close()
            else:
                server_stream.write(data)


        server_stream.connect((self.host, self.port), callback=connect_callback)

        client_stream.read_until_close(streaming_callback=client_read)
        print("closed")







def make_app(executor, auth_class=None, debug = False):
    if auth_class is None:
        d = DynamicLoader('auth')

        module = opts.authenticator if opts.authenticator else None
        if not auth_class:
            auth_class = d.load_class(class_base=BasicAuthenticator, module=module)[0]

    classes = [auth_class, Test, AutoInstall, ConsoleHandler]

    settings = {
        "cookie_secret": "SADFccadaeqw221fdssdvxccvsdf",
        "login_url": "/login",
        "debug": debug
    }
    for cls in classes:
        cls.debug = debug

    app =  tornado.web.Application([

        (r"/login", AuthHandler, dict(executor=executor, authenticator=auth_class)),
        (r"/logout", LogOut, dict(executor=executor)),
        (r'/test', Test, dict(executor=executor)),
        (XenAdapter.AUTOINSTALL_PREFIX + r'/([^/]+)', AutoInstall, dict(executor=executor)),
        (r'/(console.*)', ConsoleHandler, dict(executor=executor)),
        (r'/createvm', CreateVM, dict(executor=executor)),
        (r'/startstopvm', StartStopVM, dict(executor=executor)),
        (r'/vmlist', VMList, dict(executor=executor)),
        (r'/poollist', PoolList, dict(executor=executor)),
        (r'/list_pools', PoolListPublic, dict(executor=executor)),
        (r'/tmpllist', TemplateList, dict(executor=executor)),
        (r'/netlist', NetworkList, dict(executor=executor)),
        (r'/enabledisabletmpl', EnableDisableTemplate, dict(executor=executor)),
        (r'/vnc', VNC, dict(executor=executor)),
        (r'/attachdetachdisk', AttachDetachDisk, dict(executor=executor)),
        (r'/attachdetachiso', AttachDetachIso, dict(executor=executor)),
        (r'/destroyvm', DestroyVM, dict(executor=executor)),
        (r'/connectvm', ConnectVM, dict(executor=executor)),
        (r'/adminauth', AdminAuth, dict(executor=executor)),
        (r'/convertvm', ConvertVM, dict(executor=executor)),
        (r'/installstatus', InstallStatus, dict(executor=executor)),
        (r'/vminfo', VMInfo, dict(executor=executor)),
        (r'/isolist', ISOList, dict(executor=executor)),
        (r'/setaccess', SetAccessHandler, dict(executor=executor)),
        (r'/getaccess', GetAccessHandler, dict(executor=executor))

    ], **settings)

    app.auth_class = auth_class
    if debug:
        opts.database = opts.database + '_debug_{0}'.format(datetime.datetime.now().strftime("%b_%d_%Y_%H_%M_%S"))
        print("VMEmperor is launched in DEBUG mode. Using database {0}".format(opts.database))

    from auth.sqlalchemyauthenticator import SqlAlchemyAuthenticator, User, Group
    if opts.debug and app.auth_class.__name__ == SqlAlchemyAuthenticator.__name__:
        #create test users

        john_group = Group(name='John friends')
        SqlAlchemyAuthenticator.session.add(john_group)
        SqlAlchemyAuthenticator.session.add(User(name='john', password='john', groups=[john_group]))
        SqlAlchemyAuthenticator.session.add(User(name='mike', password='mike', groups=[john_group]))
        SqlAlchemyAuthenticator.session.add(User(name='eva', password='eva', groups=[]))
        try:
            SqlAlchemyAuthenticator.session.commit()
        except:  # Users have already been added
            SqlAlchemyAuthenticator.session.rollback()

    return app

def read_settings():
    """reads settings from ini"""
    define('debug', group = 'debug', type = bool, default=False)
    define('username', group = 'xenadapter')
    define('password', group = 'xenadapter')
    define('url', group = 'xenadapter')
    define('database', group = 'rethinkdb', default = 'test')
    define('host', group = 'rethinkdb', default = 'localhost')
    define('port', group = 'rethinkdb', type = int, default = 28015)
    define('delay', group = 'ioloop', type = int, default=5000)
    define('max_workers', group = 'executor', type = int, default=16)
    define('vmemperor_url', group ='vmemperor', default = '10.10.10.102')
    define('vmemperor_port', group = 'vmemperor', type = int, default = 8888)
    define('authenticator', group='vmemperor', default='')
    define('log_events', group='ioloop', default='')


    from os import path

    file_path = path.join(path.dirname(path.realpath(__file__)), 'login.ini')
    parse_config_file(file_path)
    ReDBConnection().set_options(opts.host, opts.port)

def main():
    """ reads settings in ini configures and starts system"""
    asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())

    read_settings()
    executor = ThreadPoolExecutor(max_workers = 1024)
    app = make_app(executor)
    server = tornado.httpserver.HTTPServer(app)
    server.listen(opts.vmemperor_port, address="0.0.0.0")
    ioloop = event_loop(executor, opts.delay, authenticator=app.auth_class)
    ioloop.start()
    return

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass