import pathlib
import signal
import atexit
from connman import ReDBConnection
from auth import dummy
from xenadapter import XenAdapter, XenAdapterPool
from xenadapter.template import Template
from xenadapter.vm import VM
from xenadapter.network import Network
from xenadapter.disk import ISO
from xenadapter.pool import Pool
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
from rethinkdb.errors import ReqlDriverError, ReqlTimeoutError
from authentication import BasicAuthenticator
from loggable import Loggable
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, urlencode
from exc import *
import logging
from netifaces import ifaddresses, AF_INET
import uuid
from tornado.options import define, options as opts, parse_config_file
import queue
import threading
import datetime


from xmlrpc.client import DateTime as xmldt
from frozendict import frozendict, FrozenDictEncoder
from authentication import AdministratorAuthenticator
from tornado.websocket import *
import asyncio
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
#Objects with ACL enabled
objects = [VM, Network]

user_table_ready = threading.Event()
need_exit = threading.Event()
xen_events_run = threading.Event() # called by USR2 signal handler

def table_drop(db, table_name):
    try:
        db.table_drop(table_name).run()
    except r.errors.ReqlOpFailedError as e:
        # TODO make logging
        print(e.message)
        r.db('rethinkdb').table('table_config').filter(
            {'db': opts.database, 'name': table_name}).delete().run()


class DateTimeEncoder(json.JSONEncoder):
    MY_TIME_FORMAT = "%d.%m.%Y, %H:%M:%S"
    def default(self, o):
        if isinstance(o, xmldt):
            t =  datetime.datetime.strptime(o.value, "%Y%m%dT%H:%M:%SZ")
            return t.strftime(self.MY_TIME_FORMAT)
        elif isinstance(o, datetime.datetime):
            return o.strftime(self.MY_TIME_FORMAT)

        

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
            self.set_status(401)
            self.write({'status': 'error', 'message': 'not authorized'})
        else:
            self.user_authenticator  = pickle.loads(user)
            self.user_authenticator.xen = XenAdapter({**opts.group_dict('xenadapter'), **opts.group_dict('rethinkdb')})
            self.xen = self.user_authenticator.xen
            return method(self, *args, **kwargs)

    return decorator




class HandlerMethods(Loggable):
    def init_executor(self, executor):
        self.executor = executor
        self.debug = opts.debug
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

            body = self.request.body.decode(encoding=encoding).strip()
            if body:
                json_data = json.loads(body)
                json_data_lists = {k : [v] for k, v in json_data.items()}
                self.request.arguments.update(json_data_lists)

                #monkey-patch decode argument
                self.decode_argument = lambda value, name: value

                #monkey-patch _get_arguments
                old_get_arguments = self._get_arguments
                self._get_arguments = lambda name, source, strip: old_get_arguments(name, source, False)

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
            self.log.info('User failed to login with credentials: {0} {1}'.format(username, password))
            self.set_status(401)
            return


        self.write(json.dumps({'status' : 'success', 'login' : username}))
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
                    .union(
                    self.db.table('vms_user').get_all('users/%s' % userid, index='userid').without('id').
                    changes(include_types=True, include_initial=True).
                        merge(r.branch((r.row['type'] == 'initial') | (r.row['type'] == 'add'),
                        self.db.table('vms').get(r.row['new_val']['uuid']),
                        {})))

                for group in self.user_authenticator.get_user_groups():
                    group = str(group)

                    self.changes_query = self.changes_query.union(self.db.table('vms_user').get_all( 'groups/%s' % group, index='userid')
                                                                  .without('id').changes(include_types=True, include_initial=True)
                                                                  .merge(r.branch((r.row['type'] == 'initial') | (r.row['type'] == 'add'),
                                                                  self.db.table('vms').get(r.row['new_val']['uuid']),
                                                                  {})))


            ioloop = tornado.ioloop.IOLoop.instance()
            ioloop.run_in_executor(self.executor, self.items_changes)




    def items_changes(self):
        '''
        Monitor for User table (access rules) items' changes with the following considerations:
        - We only monitor for changes in vms table. We need to filter them manually, as there's no way for such
        complicated filter in ReQL. These have 'type' == 'change'
        - We know about new entries in vms table because vms_user table provides that for us. Every addition to vms_user
        gets merged with the corresponding record from vms
        - All entries from vms_user table have 'type' in ('initial', 'add', 'remove') because do_access_monitor only operates
        with 'insert' and 'remove'
        - When
        '''
        try:
            conn = ReDBConnection().get_connection()
            with conn:
                valid_uuids = set()
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


                while True:
                    try:
                        change = cur.next(False)
                    except ReqlTimeoutError as e: #Monitor if we need to exit
                        if not self.ws_connection or need_exit.is_set():
                            return
                        else:
                            continue


                    if not self.ws_connection or need_exit.is_set():
                        return


                    if not isinstance(self.user_authenticator, AdministratorAuthenticator):
                        if change['type'] == 'change': #these are sent from vms
                            if change['new_val']:
                                record = change['new_val']
                            elif change['type'] == 'remove':
                                record = change['old_val']
                            else:
                                record = change

                            #for access_entry in record['access']:
                            #    if check_access_enSacceetry(access_entry):
                            #        break
                            #else: #Normal quit, not via break
                            #    continue #filter this entry
                            if record['uuid'] not in valid_uuids:
                                continue


                        elif change['type'] in ('initial', 'add'): #these are access only
                            del change['new_val'] # we merge them with entries from vms, we don't need new_val
                            if 'old_val' in change:
                                del change['old_val']

                            if change['uuid'] not in valid_uuids:
                                valid_uuids.add(change['uuid'])
                            else:
                                continue # we will get this change as we're subscribed anyway


                        elif change['type'] == 'remove':
                            del change['new_val'] #always null

                            if change['old_val']['uuid'] not in valid_uuids:
                                continue

                            valid_uuids.remove(change['old_val']['uuid'])



                    self.write_message(json.dumps(change, cls=DateTimeEncoder))

        except Exception as e:
            self.log.error("Exception in items_changes', user: {0}: {1}, restarting..."
                           .format(self.user_authenticator.get_id(), e))
            ioloop = tornado.ioloop.IOLoop.instance()
            ioloop.run_in_executor(self.executor, self.items_changes)



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
        with self.conn:
            table = r.db(opts.database).table('pools')
            list = [x for x in table.run()]

            self.write(json.dumps(list))


class TemplateList(BaseHandler):
    @auth_required
    def get(self):
        """
        List of available templates
        format:
        [{'uuid': template UUID,
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
          'uuid': 'db199908-f133-4c7f-b06c-10ac2784ad5d'}]
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

        try:
            tmpl_name = self.get_argument('template')
            self.sr_uuid = self.get_argument('storage')
            self.net_uuid = self.get_argument('network')
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
                if tmpl['uuid'] == tmpl_name or \
                tmpl['name_label'] == tmpl_name:
                    tmpl_uuid = tmpl['uuid']
                    break

            if not tmpl_uuid:
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
            self.scenario_url = 'http://'+ opts.vmemperor_url + ':' + str(opts.vmemperor_port) + XenAdapter.AUTOINSTALL_PREFIX + "/" + self.os_kind.split()[0] + "?" +\
                urlencode(kwargs, doseq=True )
            self.log.info("Scenario URL generated: %s", self.scenario_url)

            def clone_post_hook(return_value, auth):
                vm =  VM.create(auth, return_value, self.sr_uuid, self.net_uuid, self.vdi_size, self.ram_size,
                                         self.hostname, self.mode, self.os_kind, self.ip_tuple, self.mirror_url,
                                         self.scenario_url, self.name_label, False, self.override_pv_args)

                ioloop = tornado.ioloop.IOLoop.current()
                self.uuid = vm.uuid
                #ioloop.add_callback(self.do_finalize_install)
                ioloop.run_in_executor(self.executor, self.finalize_install)



            def do_clone(auth):
                tmpl = Template(auth, uuid=tmpl_uuid)
                vm = tmpl.clone(self.name_label)
                return vm.uuid


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
            self.log.info("Finalizing installation of VM %s" % self.uuid)
            db = r.db(opts.database)
            state = db.table('vms').get(self.uuid).pluck('power_state').run()['power_state']
            if state != 'Running':
                auth.xen.insert_log_entry(self.uuid, 'failed', "failed to start VM for installation (low resources?). State: %s" % state)
                return

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
                    self.log.error("ReQL error while trying to retreive VM {1} install status: {0}".format(e, self.uuid))
                    return

                if change['new_val']['power_state'] == 'Halted':
                    try:
                        vm = VM(auth, uuid=self.uuid)
                        vm.start_stop_vm(True)
                    except XenAdapterAPIError as e:
                        auth.xen.insert_log_entry(self.uuid, "failed", "failed to start after installation: %s" % e.message)
                    else:
                        auth.xen.insert_log_entry(self.uuid, "installed", "OS successfully installed")
                    break









class NetworkList(BaseHandler):
    @auth_required
    def get(self):
        with self.conn:
            db = r.db(opts.database)
            try:
                self.write(json.dumps(db.table('nets').coerce_to('array').run()))
            except Exception as e:
                self.set_status(500)
                self.log.error("Exception: {0}".format(e))





class ConvertVM(BaseHandler):
    @auth_required
    def post(self):
        vm_uuid =self.get_argument('uuid')
        mode = self.get_argument('mode')
        self.try_xenadapter(lambda auth: VM(auth, uuid=vm_uuid).convert(mode))

class EnableDisableTemplate(BaseHandler):
    @auth_required
    def post(self):
        """
         Enable or disable template
         Arguments:
             uuid: VM UUID
             enable: True if template needs to be enabled
         """
        uuid = self.get_argument('uuid')
        enable = self.get_argument('enable')


        self.try_xenadapter( lambda auth: Template(auth, uuid=uuid).enable_disable(bool(enable)))




class AttachDetachDisk(BaseHandler):
    @auth_required
    def post(self):
        '''
        Attach or detach VDI from/to VM
        Arguments:
            vm_uuid: VM UUID
            vdi_uuid: VDI UUID
            enable: True if to attach disk, False if to detach.
        '''
        with self.conn:
            vm_uuid = self.get_argument('vm_uuid')
            vdi_uuid = self.get_argument('vdi_uuid')
            enable = self.get_argument('enable')
            def xen_call(auth):
                if enable:
                    return auth.xen.attach_disk(vm_uuid, vdi_uuid)
                else:
                    auth.xen.detach_disk(vm_uuid, vdi_uuid)

            self.try_xenadapter(xen_call)








class ConnectVM(BaseHandler):
    @auth_required
    def post(self):
        '''
        Connect a VM to a Network. Requires permission "attach"
        Arguments:
        vm_uuid: VM UUID
        net_uuid: Network UUID
        ip: undocumented. Lera?
        :return:
        '''

        vm_uuid = self.get_argument('vm_uuid')
        net_uuid = self.get_argument('net_uuid')
        ip = self.get_argument('ip', default=None)
        self.try_xenadapter(lambda : xen.connect_vm(vm_uuid, net_uuid, ip))


class AnsibleHooks:
    # todo
    pass


class VMAbstractHandler(BaseHandler):
    '''
    Abstact handler for VM requests
    requires: function self.get_data returning something we can write
              attribute self.access - access mode
    provides: self.uuid <- vm_uuid

    '''
    @auth_required
    def post(self):

        vm_uuid = self.get_argument('uuid')
        self.uuid = vm_uuid
        with self.conn:
            try:
                self.vm = VM(self.user_authenticator, uuid=vm_uuid)
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
                self.write(json.dumps(ret, cls=DateTimeEncoder))

    def get_data(self):
        '''return answer information (if everything is OK). Else use set_status and write'''
        raise NotImplementedError()

class SetAccessHandler(BaseHandler):
    @auth_required
    def post(self):
        with self.conn:
            uuid = self.get_argument('uuid')
            _type = self.get_argument('type')
            action = self.get_argument('action')
            revoke = self.get_argument('revoke', False)
            if  type(revoke) == str and revoke.lower() == 'false':
                revoke = False

            if revoke:
                revoke = True
            user = self.get_argument('user', default=None)
            if not user:
                group = self.get_argument('group')
            else:
                group = None
            type_obj = None
            for obj in objects:
                if obj.__name__ == _type:
                    type_obj = obj
                    break
            else:
                self.set_status(400)
                self.write({'status' : 'bad request', 'message' : 'unsupported type %s' % _type})
                return

            try:
                self.target = type_obj(self.user_authenticator, uuid=uuid)
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

            uuid = self.get_argument('uuid')
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
                type_obj(self.user_authenticator, uuid=uuid).check_access(None)
            except XenAdapterAPIError as e:
                self.set_status(400)
                self.write({'status': 'bad request', 'message': e.message})
                return

            except XenAdapterUnauthorizedActionException as e:
                self.set_status(403)
                self.write({'status': 'access denied', 'message': e.message})
                return

            db = r.db(opts.database)
            self.write(db.table(type_obj.db_table_name).get(uuid).pluck('access').run())




class InstallStatus(VMAbstractHandler):

    access = 'launch'

    def get_data(self):
        db = r.db(opts.database)
        try:
            d = db.table('vm_logs').filter({'uuid': self.uuid}).max('time').run()
            d['time'] = d['time'].isoformat()
            return d
        except Exception as e:
            self.set_status(500)
            self.log.error("Unable to get VM installation logs: uuid: {0}, error: {1}".format(self.uuid, e))
            self.write({'status': 'database error/no info'})
            return

class VMInfo(VMAbstractHandler):

    access = 'launch'

    def get_data(self):
        db = r.db(opts.database)
        try:
            d = db.table('vms').get(self.uuid).run()
            return d
        except Exception as e:
            self.log.error("Exception: {0}".format(e))
            self.set_status(500)
            self.write({'status' : 'database error/no info'})
            return

class DestroyVM(VMAbstractHandler):

    access = 'destroy'

    def get_data(self):
        uuid = self.get_argument('uuid')


        self.try_xenadapter(lambda auth: VM(auth, uuid=uuid).destroy_vm())

class StartStopVM(VMAbstractHandler):

    access = 'launch'

    def get_data(self):
        uuid = self.get_argument('uuid')
        enable = self.get_argument('enable')


        self.try_xenadapter(lambda auth: VM(auth, uuid=uuid).start_stop_vm(enable))


class VNC(VMAbstractHandler):

    access = 'launch'

    def get_data(self):
        '''
        Get VNC console url that supports HTTP CONNECT method. Requires permission 'launch'
        Arguments:
            uuid: VM UUID

        '''

        vm_uuid = self.get_argument('uuid')

        def get_vnc(auth: BasicAuthenticator):
            url = VM(auth, uuid=vm_uuid).get_vnc()
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
            uuid: VM UUID
            iso_uuid: ISO UUID
            action: 'attach' or 'detach'
        :return:
        '''
        self.log.info("check if ISO UUID is valid")
        iso_uuid = self.get_argument('iso_uuid')
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
        res = db.table('isos').get(iso_uuid).run()
        if res:
            self.log.info("UUID %s valid, attaching/detaching..." % iso_uuid)
            def attach(auth : BasicAuthenticator):
                iso = ISO(uuid=iso_uuid, auth=auth)
                if is_attach:
                    iso.attach(self.vm)
                else:
                    iso.detach(self.vm)


            self.try_xenadapter(attach)
        else:
            self.log.info("UUID %s invalid, not attaching..." % iso_uuid)
            self.set_status(400)
            self.write({'status':'error', 'message': 'invalid UUID iso_uuid'})
            return



class EventLoop(Loggable):
    """every n seconds asks all vms about their status and updates collections (dbs, tables)
    of corresponding user, if they are logged in (have open connection to dbms notifications)
     and admin db if admin is logged in"""


    def __init__(self, executor, authenticator):
        self.debug = opts.debug

        self.init_log()

        self.executor = executor
        self.authenticator = authenticator

        self.log.info("Using database {0}".format(opts.database))
        conn = ReDBConnection().get_connection()
        with conn:
            print("Creating databases", end='...')
            if opts.database in r.db_list().run():
                r.db_drop(opts.database).run()

            r.db_create(opts.database).run()
            self.db = r.db(opts.database)
            tables = self.db.table_list().run()

            self.db.table_create('vm_logs', durability='soft').run()
            self.db.table('vm_logs').wait()

            try:
                authenticator.xen = XenAdapter({**opts.group_dict('xenadapter'), **opts.group_dict('rethinkdb')})
            except XenAdapterConnectionError as e:
                raise RuntimeError("XenServer not reached")

            self.xen = XenAdapter({**opts.group_dict('xenadapter'), **opts.group_dict('rethinkdb')})
            # required = ['vms', 'tmpls', 'pools', 'nets']


            self.db.table_create('vms', durability='soft', primary_key='uuid').run()
            self.db.table('vms').index_create('ref', r.row['ref']).run()
            self.db.table('vms').index_wait('ref').run()
            self.db.table('vms').index_create('metrics').run()
            self.db.table('vms').index_wait('metrics').run()


            vms = VM.init_db(authenticator)
            CHECK_ER(self.db.table('vms').insert(vms, conflict='error').run())





            if 'isos' not in tables:
                self.db.table_create('isos', durability='soft', primary_key='uuid').run()
                isos = ISO.init_db(authenticator)

                CHECK_ER(self.db.table('isos').insert(isos, conflict='error').run())
            else:
                isos = ISO.init_db(authenticator)

                CHECK_ER(self.db.table('isos').insert(isos, conflict='update').run())

            if 'tmpls' not in tables:
                self.db.table_create('tmpls', durability='soft', primary_key='uuid').run()

                tmpls = Template.init_db(authenticator)
                CHECK_ER(self.db.table('tmpls').insert(list(tmpls), conflict='error').run())
            else:
             #   tmpls = self.xen.list_templates().values()
                tmpls = Template.init_db(authenticator)
                CHECK_ER(self.db.table('tmpls').insert(list(tmpls), conflict='update').run())
            if 'pools' not in tables:
                self.db.table_create('pools', durability='soft', primary_key='uuid').run()
                pools = Pool.init_db(authenticator)
                CHECK_ER(self.db.table('pools').insert(list(pools), conflict='error').run())
            else:
                pools = Pool.init_db(authenticator)
                CHECK_ER(self.db.table('pools').insert(list(pools), conflict='update').run())
            if 'nets' not in tables:
                self.db.table_create('nets', durability='soft', primary_key='uuid').run()
                nets = Network.init_db(authenticator)
                CHECK_ER(self.db.table('nets').insert(list(nets), conflict='error').run())
            else:
                nets = Network.init_db(authenticator)
                # nets = self.xen.list_networks().values()
                CHECK_ER(self.db.table('nets').insert(list(nets), conflict='update').run())

            del authenticator.xen


    def do_access_monitor(self):
        try:
            self.log.debug("started access_monitor in thread {0}".format(threading.get_ident()))
            conn = ReDBConnection().get_connection()
            #log = self.create_additional_log('AccessMonitor')
            log = self.log
            with conn:
                query = self.db.table(objects[0].db_table_name).pluck('uuid', 'access')\
                    .merge({'table' : objects[0].db_table_name}).changes()

                table_list = self.db.table_list().run()
                def initial_merge(table):
                    nonlocal table_list
                    table_user = table + '_user'
                    if table_user in table_list:
                        self.db.table_drop(table_user).run()


                    self.db.table_create(table_user, durability='soft').run()
                    self.db.table(table_user).wait().run()
                    self.db.table(table_user).index_create('uuid_and_userid', [r.row['uuid'], r.row['userid']]).run()
                    self.db.table(table_user).index_wait('uuid_and_userid').run()
                    self.db.table(table_user).index_create('userid', r.row['userid']).run()
                    self.db.table(table_user).index_wait('userid').run()
                    # no need yet
                    #self.db.table(table_user).index_create('uuid', r.row['uuid']).run()
                    #self.db.table(table_user).index_wait('uuid').run()

                    CHECK_ER(self.db.table(table_user).insert(
                        self.db.table(table).pluck('access', 'uuid').filter(r.row['access'] != []).\
                        concat_map(lambda acc: acc['access'].merge({'uuid':acc['uuid']}))).run())


                i = 0
                while i < len(objects):
                    initial_merge(objects[i].db_table_name)

                    if i > 0:
                        query.union(self.db.table(objects[i].db_table_name).pluck('uuid', 'access')\
                                        .merge({'table': objects[i].db_table_name}).changes())
                    i += 1

                #indicate that vms_user table is ready
                user_table_ready.set()
                cur = query.run()

                def uuid_delete(table_user, uuid):
                    CHECK_ER(self.db.table(table_user).filter({'uuid' : uuid}).delete().run())


                while True:
                    try:
                        record = cur.next(False)
                    except ReqlTimeoutError as e:
                        if need_exit.is_set():
                            self.log.debug("Exiting access_monitor")
                            return
                        else:
                            continue

                    if record['new_val']: #edit
                        uuid = record['new_val']['uuid']
                        table = record['new_val']['table']
                        access = record['new_val']['access']
                        table_user = table + '_user'


                        #if record['old_val']:
                        #    access_to_remove = \
                        #        set((frozendict(x) for x in record['old_val']['access'])) -\
                        #         set((frozendict(x) for x in access))
                        #    if access_to_remove:
                        #        log.info("Removing access rights for {0} (table {1}): {2}"
                        #        .format(uuid, table, json.dumps(access_to_remove, cls=FrozenDictEncoder)))

                        #    for item in access_to_remove:
                        #        CHECK_ER(self.db.table(table_user).get_all([record['old_val']['uuid'], item['userid']], index='uuid_and_userid').delete().run())



                        if not record['old_val']:
                            if access:
                                log.info("Adding access rights for %s (table %s): %s" %
                                         (uuid, table, json.dumps(access)))
                            for item in access:
                                CHECK_ER(self.db.table(table_user).insert(r.expr(item).merge({'uuid' : uuid})).run())
                        else:

                            access_diff = set((frozendict(x) for x in access)) -\
                                          set((frozendict(x) for x in record['old_val']['access']))

                            if access_diff:
                                log.info("Adding access rights for %s (table %s): %s" %
                                         (uuid, table, json.dumps(access_diff, cls=FrozenDictEncoder)))
                            for item in access_diff:
                                CHECK_ER(self.db.table(table_user).insert(r.expr(item).merge({'uuid' : uuid} )).run())



                    else:
                        uuid = record['old_val']['uuid']
                        table = record['old_val']['table']
                        table_user = table + '_user'
                        log.info("Deleting access rights for %s (table %s)" % (uuid, table))
                        uuid_delete(table_user, uuid)
        except Exception as e:
            self.log.error("Exception in access_monitor: {0}"
                           .format(e))
            #tornado.ioloop.IOLoop.current().run_in_executor(self.executor, self.do_access_monitor)
            raise e

    def process_xen_events(self):
        self.log.debug("Started process_xen_events in thread {0}".format(threading.get_ident()))
        from XenAPI import Failure

        self.authenticator.xen = XenAdapterPool().get()
        xen = self.authenticator.xen
        event_types = ["*"]
        token_from = ''
        timeout = 1.0

        xen.api.event.register(event_types)
        conn = ReDBConnection().get_connection()
        with conn:
            self.log.debug("Started process_xen_events. You can kill this thread and 'freeze'"
                           " cache databases (except for access) by sending signal USR2")

            while True:
                try:
                    if not xen_events_run.is_set():
                        self.log.debug("Freezing process_xen_events")
                        xen_events_run.wait()
                        self.log.debug("Unfreezing process_xen_events")
                    if need_exit.is_set():
                        self.log.debug("Exiting process_xen_events")
                        return

                    event_from_ret = xen.api.event_from(event_types, token_from, timeout)
                    events = event_from_ret['events']
                    token_from = event_from_ret['token']

                    for event in events:
                        log_this = opts.log_events and event['class'] in opts.log_events.split(',')\
                                   or not opts.log_events


                        # similarly to list_vms -> process
                        if event['class'] == 'vm' or event['class'] == 'vm_metrics':
                            ev_class = VM  # use methods filter_record, process_record (classmethods)
                        else:  # Implement ev_classes for all types of events
                            if log_this:
                                self.log.debug("Ignored Event: %s" % json.dumps(event, cls=DateTimeEncoder))
                            continue

                        if log_this:
                            self.log.debug("Event: %s" % json.dumps(event, cls=DateTimeEncoder))

                        ev_class.process_event(self.authenticator, event, self.db, self.authenticator.__name__)





                except Failure as f:
                    if f.details == ["EVENTS_LOST"]:
                        self.log.warning("Reregistering for events")
                        xen.api.event.register(event_types)



def event_loop(executor, authenticator=None, ioloop = None):
    if not ioloop:
        ioloop = tornado.ioloop.IOLoop.instance()

    loop_object = EventLoop(executor, authenticator)

    #tornado.ioloop.PeriodicCallback(loop_object.vm_list_update, delay).start()  # read delay from ini

    ioloop.run_in_executor(executor, loop_object.do_access_monitor)

    xen_events_run.set()
    ioloop.run_in_executor(executor, loop_object.process_xen_events)

    def usr2_signal_handler(num, stackframe):
        if xen_events_run.is_set():
            xen_events_run.clear()
        else:
            xen_events_run.set()

    signal.signal(signal.SIGUSR2, usr2_signal_handler)


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
    define('log_file_name', group='log',default='vmemperor.log')


    from os import path

    file_path = path.join(path.dirname(path.realpath(__file__)), 'login.ini')
    parse_config_file(file_path)
    ReDBConnection().set_options(opts.host, opts.port)

    def on_exit():
        xen_events_run.set()
        need_exit.set()




    atexit.register(on_exit)
    # do log rotation
    log_path = pathlib.Path(opts.log_file_name)
    if log_path.exists():
        number = 0
        for file in log_path.parent.glob(opts.log_file_name + ".*"):
            try:
                next_number = int(file.suffix[1:])
                if next_number > number:
                    number = next_number
            except ValueError:
                continue

        for current in range(number, -1, -1):
            file = pathlib.Path(opts.log_file_name + '.{0}'.format(current))
            if file.exists():
                file.rename(opts.log_file_name + '.{0}'.format(current + 1))

        log_path.rename(opts.log_file_name + '.0')


def main():
    """ reads settings in ini configures and starts system"""
    asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())

    read_settings()






    executor = ThreadPoolExecutor(max_workers = 1024)
    app = make_app(executor)
    server = tornado.httpserver.HTTPServer(app)
    server.listen(opts.vmemperor_port, address="0.0.0.0")
    ioloop = event_loop(executor, authenticator=app.auth_class)
    print("Using authentication: {0}".format(app.auth_class.__name__))
    ioloop.start()

    return

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass