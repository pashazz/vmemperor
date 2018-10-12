import pathlib
from collections import OrderedDict
import signal
import atexit
from connman import ReDBConnection
import subprocess
from rethinkdb_helper import CHECK_ER
from xenadapter import XenAdapter, XenAdapterPool
from xenadapter.template import Template
from xenadapter.vm import VM
from xenadapter.vmguest import VMGuest
from xenadapter.network import Network, VIF
from xenadapter.disk import ISO, VDI, VDIorISO
from xenadapter.sr import SR
from xenadapter.vbd import VBD
from xenadapter.task import Task
from playbook import Playbook, PlaybookEncoder
from tasks import Operations
import copy
import traceback
import tornado.web
import tornado.httpserver
import tornado.iostream
from dynamicloader import DynamicLoader
import socket
from tornado import ioloop
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode
import pickle
import rethinkdb as r
from rethinkdb.errors import ReqlDriverError, ReqlTimeoutError
from rethinkdb.net import DefaultCursorEmpty
from authentication import BasicAuthenticator
from loggable import Loggable
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from exc import *
import time
import logging
import uuid
from tornado.options import define, options as opts, parse_config_file
import threading
import datetime
import tempfile
import shutil
from ruamel import yaml
from xmlrpc.client import DateTime as xmldt
from frozendict import frozendict, FrozenDictEncoder
from authentication import AdministratorAuthenticator
from tornado.websocket import *
import asyncio
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
from typing import Dict, Optional
from secrets import token_urlsafe

logger = None # global logger

POSTINST_ROUTE = r'/postinst'
# Objects with ACL enabled
objects = [VM, Network, VDI]

user_table_ready = threading.Event()
first_batch_of_events = threading.Event()
need_exit = threading.Event()
xen_events_run = threading.Event()  # called by USR2 signal handler
URL = ""
ansible_pubkey = ""
playbooks = Dict[str, Playbook]



secrets = {}

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
            t = datetime.datetime.strptime(o.value, "%Y%m%dT%H:%M:%SZ")
            return t.isoformat()
        elif isinstance(o, datetime.datetime):
            return o.isoformat()

        return super().default(o)


def auth_required(method):
    def decorator(self, *args, **kwargs):
        user = HandlerMethods.get_current_user(self)
        if not user:
            self.set_status(401)
            self.write({'status': 'error', 'message': 'not authorized'})
        else:
            self.user_authenticator = pickle.loads(user)
            self.user_authenticator.xen = XenAdapter({**opts.group_dict('xenadapter'), **opts.group_dict('rethinkdb')})
            self.xen = self.user_authenticator.xen
            return method(self)

    return decorator


def admin_required(method):
    def decorator(self, *args, **kwargs):
        user = HandlerMethods.get_current_user(self)
        if not user:
            self.set_status(401)
            self.write({'status': 'error', 'message': 'not authorized'})
        else:
            self.user_authenticator = pickle.loads(user)
            if not isinstance(self.user_authenticator, AdministratorAuthenticator):
                self.set_status(403)
                self.write({'status': 'error', 'message': 'administrator required'})
                return
            self.user_authenticator.xen = XenAdapter({**opts.group_dict('xenadapter'), **opts.group_dict('rethinkdb')})
            self.xen = self.user_authenticator.xen
            return method(self)

    return decorator


class HandlerMethods(Loggable):
    def init_executor(self, executor):
        self.executor = executor
        self.debug = opts.debug
        self.init_log()
        self.conn = ReDBConnection().get_connection()
        first_batch_of_events.wait()
        self.actions_log = self.create_additional_log('actions')

    def get_current_user(self):
        return self.get_secure_cookie("user")


class BaseHandler(tornado.web.RequestHandler, HandlerMethods):
    _ASYNC_KEY = None

    def initialize(self, executor):
        self.init_executor(executor)
        self.user_authenticator = Optional[BasicAuthenticator]

        self.op = Operations(r.db(opts.database))

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
                json_data_lists = {k: [v] for k, v in json_data.items()}
                self.request.arguments.update(json_data_lists)

                # monkey-patch decode argument
                self.decode_argument = lambda value, name: value

                # monkey-patch _get_arguments
                old_get_arguments = self._get_arguments
                self._get_arguments = lambda name, source, strip: old_get_arguments(name, source, False)

    def get_current_user(self):
        return self.get_secure_cookie("user")


    def async_run(self, task_ref):
        self._run_task = task_ref
        ioloop = tornado.ioloop.IOLoop.instance()
        ioloop.run_in_executor(self.executor, self.run_async_task)


    def run_async_task(self):
        task = Task(auth=self.user_authenticator, ref=self._run_task)

        with ReDBConnection().get_connection():
            write_in = {'id' : self._run_task}
            self.op.set_operation(self.user_authenticator, write_in)
            write_in['created'] = task.get_created()
            while task.get_status() == 'pending':
                write_in['status'] = task.get_status()
                write_in['progress'] =  task.get_progress()
                self.op.set_operation(None, write_in)
                time.sleep(1)

            write_in['finished'] = task.get_finished()
            write_in['status'] = task.get_status()
            write_in['progress'] = task.get_progress()

            if write_in['status'] == 'failure':
                write_in['error_info'] = task.get_error_info()


            self.op.set_operation(None, write_in)
        task.destroy()


    def try_xenadapter(self, func, post_hook=None):
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
            self.write(json.dumps({"status": 'error', 'message': "wrong credentials"}))
            self.log.info('User failed to login with credentials: {0} {1}'.format(username, password))
            self.set_status(401)
            return

        self.write(json.dumps({'status': 'success', 'login': username}))
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
    def initialize(self, executor, authenticator):
        super().initialize(executor)
        self.user_auth = authenticator

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
            authenticator = AdministratorAuthenticator(user_auth=self.user_auth)
            authenticator.check_credentials(username=username, password=password, log=self.log)
        except AuthenticationException:
            self.write(json.dumps({"status": 'error', 'message': "wrong credentials"}))
            self.set_status(401)
            return

        self.set_secure_cookie("user", pickle.dumps(authenticator))


class LogOut(BaseHandler):
    def get(self):
        self.clear_cookie('user')
        # self.redirect(self.get_argument("next", "/login"))
        self.write({'status': 'ok'})


class Playbooks(BaseHandler):
    @auth_required
    def get(self):
        _playbooks = playbooks.values();
        if not isinstance(self.user_authenticator, AdministratorAuthenticator):
            _playbooks = filter(lambda playbook: not playbook.get_inventory(), _playbooks)
        _playbooks = list(_playbooks)
        self.write(json.dumps(list(_playbooks), cls=PlaybookEncoder))


class TurnTemplate(BaseHandler):
    @admin_required
    def post(self):
        uuid = self.get_argument('uuid')
        action = self.get_argument('action')
        tmpl = Template(self.user_authenticator, uuid=uuid)
        if action not in ('on', 'off'):
            self.set_status(400)
            self.write({'status': 'error', 'message': 'action is either on or off'})
            return
        try:
            tmpl.enable_disable(action == 'on')
        except XenAdapterAPIError as e:
            self.set_status(400)
            self.write({'status': 'error', 'message': e.message})
            return

        self.write({'status': 'ok'})

class AllTemplates(BaseHandler):
    @admin_required
    def get(self):
        tmpl = Template.get_all_records(self.user_authenticator)
        self.write(json.dumps(tmpl, cls=DateTimeEncoder ))



class ResourceList(BaseHandler):
    @auth_required
    def get(self):
        with self.conn:
            db = r.db(opts.database)
            user_table_ready.wait()
            try:
                if isinstance(self.user_authenticator, AdministratorAuthenticator):
                    query = db.table(self.table).coerce_to('array')

                else:
                    userid = str(self.user_authenticator.get_id())
                    query = db.table(self.table + '_user').get_all('users/%s' % userid, index='userid'). \
                        pluck('uuid').coerce_to('array'). \
                        merge(db.table(self.table).get(r.row['uuid']).without('uuid'))

                    for group in self.user_authenticator.get_user_groups():
                        group = str(group)
                        query = query.union(db.table(self.table + '_user').get_all('groups/%s' % group, index='userid'). \
                                            without('id').coerce_to('array'). \
                                            merge(db.table(self.table).get(r.row['uuid']).without('uuid')))

                page = int(self.get_argument('page', -1))
                if page > 0:
                    page_size = int(self.get_argument('page_size', 10))
                    query = query.slice((page - 1) * page_size, page_size)

                self.write(json.dumps(query.run()))


            except Exception as e:
                self.set_status(500)
                self.log.error("Exception: {0}".format(e))


class NetworkList(ResourceList):
    table = 'nets'


class VDIList(ResourceList):
    table = 'vdis'


class VMList(BaseWSHandler):
    connections = []

    @auth_required
    @tornado.web.asynchronous
    def open(self):
        self.connections.append(self)
        with self.conn:
            db = r.db(opts.database)
            self.db = db
            if isinstance(self.user_authenticator, AdministratorAuthenticator):  # get all vms
                self.changes_query = db.table('vms').changes(include_types=True, include_initial=True)

            else:
                user_table_ready.wait()
                userid = str(self.user_authenticator.get_id())
                # Get all changes from VMS table (only changes, not removals) and mark them as 'state' changes
                # Plus get all initial values and changes from vms_user table and mark them as 'access' changes
                #
                self.changes_query = self.db.table('vms').changes(include_types=True).filter(
                    r.row['type'].eq(r.expr('change')).or_(r.row['type'].eq('remove'))) \
                    .union(
                    self.db.table('vms_user').get_all('users/%s' % userid, index='userid').without('id').
                        changes(include_types=True, include_initial=True).
                        merge(r.branch((r.row['type'] == 'initial') | (r.row['type'] == 'add'),
                                       self.db.table('vms').get(r.row['new_val']['uuid']),
                                       {})))

                for group in self.user_authenticator.get_user_groups():
                    group = str(group)

                    self.changes_query = self.changes_query.union(
                        self.db.table('vms_user').get_all('groups/%s' % group, index='userid')
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
                        change = cur.next(1)
                    except (ReqlTimeoutError, DefaultCursorEmpty) as e:  # Monitor if we need to exit
                        if not self.ws_connection or need_exit.is_set():
                            return
                        else:
                            continue

                    if not self.ws_connection or need_exit.is_set():
                        return

                    if isinstance(self.user_authenticator, AdministratorAuthenticator):
                        if change['type'] in ('initial', 'add'):
                            if change['new_val']:
                                new_val = change['new_val'].copy()
                                del change['new_val']
                                change.update(new_val)
                        elif change['type'] == 'remove':
                            del change['new_val']

                    else:
                        if change['type'] == 'change':  # these are sent from vms
                            if change['new_val']:
                                record = change['new_val']
                            elif change['type'] == 'remove':
                                record = change['old_val']
                            else:
                                record = change

                            # for access_entry in record['access']:
                            #    if check_access_enSacceetry(access_entry):
                            #        break
                            # else: #Normal quit, not via break
                            #    continue #filter this entry
                            if record['uuid'] not in valid_uuids:
                                continue


                        elif change['type'] in ('initial', 'add'):  # these are access only
                            del change['new_val']  # we merge them with entries from vms, we don't need new_val
                            if 'old_val' in change:
                                del change['old_val']

                            if change['uuid'] not in valid_uuids:
                                valid_uuids.add(change['uuid'])
                            else:
                                continue  # we will get this change as we're subscribed anyway


                        elif change['type'] == 'remove':
                            del change['new_val']  # always null

                            if change['old_val']['uuid'] not in valid_uuids:
                                continue

                            valid_uuids.remove(change['old_val']['uuid'])

                    try:
                        self.write_message(json.dumps(change, cls=DateTimeEncoder))
                    except WebSocketClosedError:
                        return

        except Exception as e:
            self.log.error("Exception in items_changes', user: {0}: {1}, restarting..."
                           .format(self.user_authenticator.get_id(), e))
            traceback.print_exc()
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
        XenServer pool list
        TODO: Rewrite it using RethinkDB cache
         """

        with self.conn:

            pool_info = {}
            api = self.user_authenticator.xen.api

            pools = api.pool.get_all_records()
            default_sr = None
            pool_description = None
            for pool in pools.values():
                default_sr = pool['default_SR']
                pool_description = pool['name_description']
                pool_id = pool['uuid']

            if default_sr == 'OpaqueRef:NULL':
                default_sr = None

            networks = api.network.get_all_records()
            # TODO: implement filtering by tags some time
            pool_info["networks"] = []
            for net in networks.values():
                if net["name_label"] == "Host internal management network":
                    continue
                pool_info["networks"].append({"uuid": net["uuid"], "name_label": net["name_label"]})

            pool_info["storage_resources"] = []
            storage_resources = api.SR.get_all_records()

            for key, sr in storage_resources.items():
                if sr["type"] == "lvmoiscsi" or sr["type"] == "lvm":
                    if default_sr is None and sr["name_label"] == "Local storage":
                        default_sr = key

                    label = ''.join((sr["name_label"], " (Available %d GB)" % (
                            (int(sr['physical_size']) - int(sr['virtual_allocation'])) / (1024 * 1024 * 1024))))
                    if sr["shared"]:
                        label = ''.join(("Shared storage: ", label))
                        pool_info["storage_resources"].insert(0, {"uuid": sr["uuid"], "name_label": label})
                    else:
                        pool_info["storage_resources"].append({"uuid": sr["uuid"], "name_label": label})

            sr_info = api.SR.get_record(default_sr)
            pool_info['hdd_available'] = (int(sr_info['physical_size']) - int(sr_info['virtual_allocation'])) / (
                    1024 * 1024 * 1024)

            pool_info['host_list'] = []

            records = api.host.get_all_records()
            for host_ref, record in records.items():
                metrics = api.host_metrics.get_record(record['metrics'])
                host_entry = dict()
                for i in ['name_label', 'resident_VMs', 'software_version', 'cpu_info']:
                    host_entry[i] = record[i]
                host_entry['memory_total'] = int(metrics['memory_total']) / (1024 * 1024)
                host_entry['memory_free'] = int(metrics['memory_free']) / (1024 * 1024)
                host_entry['live'] = metrics['live']
                host_entry['memory_available'] = int(api.host.compute_free_memory(host_ref)) / (1024 * 1024)
                pool_info['host_list'].append(host_entry)

            # For now we have a single endpoint
            pool_info['url'] = opts.url
            pool_info['description'] = pool_description
            pool_info['uuid'] = pool_id

            # TODO filter templates by tag??

            tmpls_table = r.db(opts.database).table('tmpls')
            pool_info['templates_enabled'] = [x for x in tmpls_table.run()]

        self.write(json.dumps([pool_info]))


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
                def clone_post_hook(return_value, auth):
                    vm = VM.create(self.insert_log_entry, auth, return_value, self.sr_uuid, self.net_uuid,
                                   self.vdi_size, self.ram_size,
                                   self.hostname, self.mode, os_kind=self.os_kind, ip=self.ip_tuple,
                                   install_url=self.mirror_url,
                                   name_label=self.name_label, override_pv_args=self.override_pv_args, iso=self.iso,
                                   username=self.username, password=self.password, partition=self.partition,
                                   fullname=self.fullname)

                    ioloop = tornado.ioloop.IOLoop.current()
                    self.uuid = vm.uuid
                    # ioloop.add_callback(self.do_finalize_install)
                    ioloop.run_in_executor(self.executor, self.finalize_install)
                    log_message = """
                    Created VM: UUID {return_value}
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
                                                             return_value=return_value))

                def do_clone(auth):
                    tmpl = Template(auth, uuid=self.template['uuid'])
                    vm = tmpl.clone(self.name_label)
                    self.insert_log_entry(vm.uuid, 'cloned', f'cloned from {tmpl.uuid}')
                    clone_post_hook(vm.uuid, auth)

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


class ConvertVM(BaseHandler):
    @auth_required
    def post(self):
        vm_uuid = self.get_argument('uuid')
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

        self.try_xenadapter(lambda auth: Template(auth, uuid=uuid).enable_disable(bool(enable)))


class TaskStatus(BaseHandler):
    @auth_required
    def post(self):
        task = self.get_argument('task')

        operation = None
        try:
            operation = self.op.get_operation(self.user_authenticator, task)
        except KeyError:
            self.set_status(404)
            self.finish()
            return


        try:
            self.write(json.dumps({k: v for k, v in operation.items() if k != 'auth'},
                       cls=DateTimeEncoder))
        except Exception as e:
            self.write({'status': 'error', 'details': 'no such task'})
            self.set_status(400)
        finally:
            self.finish()


class ExecutePlaybook(BaseHandler):
    _ASYNC_KEY = 'pb'

    def run_ansible(self):
        with ReDBConnection().get_connection():
            self.log.info(f"Running: {self.cmd_line} in {self.cwd} as {self.cwd.name}")
            task = {'id': self.cwd.name}

            log_path = Path(opts.ansible_logs).joinpath(self.cwd.name)
            os.makedirs(log_path)
            with open(log_path.joinpath('stdout'), 'w') as _stdout:
                with open(log_path.joinpath('stderr'), 'w') as _stderr:
                    task['returncode'] = None
                    self.op.set_operation(self.user_authenticator, task)
                    proc = subprocess.run(self.cmd_line,
                                          cwd=self.cwd, stdout=_stdout, stderr=_stderr,
                                          env={"ANSIBLE_HOST_KEY_CHECKING":"False"})

                    task['returncode'] = proc.returncode
                    self.op.set_operation(None, task)

            self.log.info(f'Finished {self.cwd.name} with return code {tasks[self.cwd.name]["returncode"]}')

    @auth_required
    def post(self):
        vms = self.get_argument('vms')
        ans = {}
        with self.conn:
            for _vm in vms:
                vm = VM(self.user_authenticator, uuid=_vm)
                try:
                    vm.check_access('launch')
                except XenAdapterUnauthorizedActionException as e:
                    self.set_status(403)
                    self.write({'status': 'access denied', 'message': e.message})
                    return

            _playbook = self.get_argument('playbook')
            if not _playbook in playbooks:
                self.set_status(400)
                self.write({'status': 'error', 'message': 'no such playbook: {0}'.format(_playbook)})
                return
            p = playbooks[_playbook]

            temp_dir = tempfile.mkdtemp(prefix='vmemperor-', suffix=f'-playbook-{_playbook}')
            self.log.info(f"Creating temporary directory {temp_dir}")
            from distutils.dir_util import copy_tree
            playbook_dir = p.get_playbook_dir()
            self.log.info(f"Copying {playbook_dir} into temporary directory")
            copy_tree(playbook_dir, temp_dir)
            temp_path = Path(temp_dir)
            table = r.db(opts.database).table('vms')
            documents = table.get_all(*vms).coerce_to('array').run()

            if not p.get_inventory():
                hosts_file = 'hosts'
                yaml_hosts = {'all': {'hosts': {}}}
                for vm in documents:
                    for net in vm['networks'].values():
                        if not net['network'] in opts.ansible_networks:
                            continue
                        if not 'ip' in net or not net['ip']:
                            continue
                        yaml_hosts['all']['hosts'][vm['name_label']] = {
                            'ansible_user': 'root',
                            'ansible_host': net['ip']
                        }
                        break
                    else:
                        self.log.warning(
                            f"Ignoring VM {vm['uuid']}: not connected to any of 'ansible_networks'. Check your configuration")
                        if 'warnings' in ans:
                            if 'notconnected' in ans['warnings']:
                                ans['warnings']['notconnencted'].append(vm['uuid'])
                            else:
                                ans['warnings'] = {'notconnected': vm['uuid']}
                        else:
                            ans['warnings'] = {'notconnected': vm['uuid']}

                if yaml_hosts['all']['hosts']:
                    # Create ansible execution task

                    with open(temp_path.joinpath(hosts_file), 'w') as file:
                        yaml.dump(yaml_hosts, file)
                    self.log.info("Hosts file created")
                else:
                    self.set_status(400)
                    self.write(ans)
                    self.log.error(f"{temp_dir}: No suitable VMs found")
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    self.finish()
                    return


            else:
                hosts_file = p.get_inventory()

            self.log.info("Patching variables files...")

            for key, vars in p.vars.items():
                vars_copy = vars.copy()
                for variable in p.variables_locations[key]:
                    value = self.get_argument(variable, p.config['variables'][variable]['value'])
                    vars_copy[variable] = value
                file_name = temp_path.joinpath(key, 'all')
                with open(file_name, 'w') as file:
                    yaml.dump(vars_copy, file)

                self.log.info(f'File {file_name} patched')

            self.cmd_line = [opts.ansible_playbook, '-i', hosts_file, p.get_playbook_file()]
            self.cwd = temp_path
            ans['task'] = self.cwd.name
            self._run_task = ans['task']
            ioloop = tornado.ioloop.IOLoop.instance()
            ioloop.run_in_executor(self.executor, self.run_ansible)
            self.write(ans)
            self.finish()


class ResourceAbstractHandler(BaseHandler):
    '''
    Abstact handler for resource requests
    requires: function self.get_data returning something we can write
              attribute self.access - access mode
              attribute self.resource - resource class
    provides: self.uuid <- vm_uuid

    '''

    @auth_required
    def post(self):

        uuid = self.get_argument('uuid')
        self.uuid = uuid
        with self.conn:
            try:
                resource_name = self.resource.__name__.lower()
                self.__setattr__(resource_name, self.resource(self.user_authenticator, uuid=uuid))
            except XenAdapterAPIError as e:
                self.set_status(400)
                self.write({'status': 'bad request', 'message': e.message})
                return

            try:
                from xenadapter.xenobject import ACLXenObject
                if isinstance(self.__getattribute__(resource_name), ACLXenObject):
                    self.__getattribute__(resource_name).check_access(self.access)
            except XenAdapterUnauthorizedActionException as e:
                self.set_status(403)
                self.write({'status': 'access denied', 'message': e.message})
                return

            ret = self.get_data()
            if ret:
                self.write(json.dumps(ret, cls=DateTimeEncoder))

    def get_data(self):
        '''return answer information (if everything is OK). Else use set_status and write'''
        raise NotImplementedError()


class VMAbstractHandler(ResourceAbstractHandler):
    resource = VM


class NetworkAbstractHandler(ResourceAbstractHandler):
    resource = Network


class VDIAbstractHandler(ResourceAbstractHandler):
    resource = VDI


class ISOAbstractHandler(ResourceAbstractHandler):
    resource = ISO


class SetAccessHandler(BaseHandler):
    @auth_required
    def post(self):
        with self.conn:
            uuid = self.get_argument('uuid')
            _type = self.get_argument('type')
            action = self.get_argument('action')
            revoke = self.get_argument('revoke', False)
            if type(revoke) == str and revoke.lower() == 'false':
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
                self.write({'status': 'bad request', 'message': 'unsupported type: %s' % _type})
                return

            try:
                self.target = type_obj(self.user_authenticator, uuid=uuid)
                self.log.info("Checking object {0} access for action {1}, revoke: {2}".format(_type, action, revoke))
                self.target.check_access(action)
                self.log.debug("Access granted, performing changes")
                self.target.manage_actions(action, revoke, user, group)
                self.log.debug("Changes successful")
            except XenAdapterAPIError as e:
                self.set_status(400)
                self.write({'status': 'bad request', 'message': e.message})
                return
            except XenAdapterUnauthorizedActionException as e:
                self.set_status(403)
                self.write({'status': 'access denied', 'message': e.message})
                return


class UserInfo(BaseHandler):
    @auth_required
    def get(self):
        auth = self.user_authenticator
        self.write(
            {
                'id': auth.get_id(),
                'name': auth.get_name(),
                'groups': auth.get_user_groups(),
                'is_admin': isinstance(auth, AdministratorAuthenticator)
            }
        )


class UserList(BaseHandler):
    @auth_required
    def get(self):
        with self.conn:
            self.write(json.dumps(r.db(opts.database).table('users').coerce_to('array').run()))


class GroupList(BaseHandler):
    @auth_required
    def get(self):
        with self.conn:
            self.write(json.dumps(r.db(opts.database).table('groups').coerce_to('array').run()))


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


class InstallStatus(BaseHandler):
    @auth_required
    def post(self):
        taskid = self.get_argument('taskid')


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
            self.write({'status': 'database error/no info'})
            return


class VMNetInfo(VMAbstractHandler):
    access = 'launch'

    def get_data(self):
        db = r.db(opts.database)
        try:
            vm_data = db.table('vms').get(self.uuid).do(lambda vm: vm['networks'].keys(). \
                                                        map(lambda key: r.expr([key, vm['networks'][key].merge(
                db.table('nets').get(vm['networks'][key]['network']).without('uuid'))])).filter(
                lambda item: item[1] != None). \
                                                        coerce_to('object')).run()
            return vm_data
        except Exception as e:
            self.log.error("Exception: {0}".format(e))
            traceback.print_exc()
            self.set_status(500)
            self.write({'status': 'database error/no info'})
            return


class VMDiskInfo(VMAbstractHandler):
    access = 'launch'

    def get_data(self):
        db = r.db(opts.database)
        try:

            vm_data = db.table('vms').get(self.uuid).do(lambda vm: vm['disks'].keys(). \
                                                        map(
                lambda diskKey: r.expr([diskKey, vm['disks'][diskKey].merge(r.branch(
                    vm['disks'][diskKey]['VDI'] != None, #if
                    r.branch( #then
                    vm['disks'][diskKey]['type'].eq('Disk'), #inner if
                    db.table('vdis').get(vm['disks'][diskKey]['VDI']).without('uuid'), # inner then
                    db.table('isos').get(vm['disks'][diskKey]['VDI']).without('uuid')), # inner else
                    {} # else
                    ))])).filter(lambda item: item[1] != None).coerce_to('object')).run()
            return vm_data



        except Exception as e:
            self.log.error("Exception: {0}".format(e))
            traceback.print_exc()
            self.set_status(500)
            self.write({'status': 'database error/no info'})
            return


class NetworkInfo(NetworkAbstractHandler):
    access = 'attach'

    def get_data(self):
        db = r.db(opts.database)
        try:
            d = db.table('nets').get(self.uuid).run()
            return d
        except Exception as e:
            self.log.error("Exception: {0}".format(e))
            self.set_status(500)
            self.write({'status': 'database error/no info'})
            return


class VDIInfo(VDIAbstractHandler):
    access = 'attach'

    def get_data(self):
        db = r.db(opts.database)
        try:
            d = db.table('vdis').get(self.uuid).run()
            return d
        except Exception as e:
            self.log.error("Exception: {0}".format(e))
            self.set_status(500)
            self.write({'status': 'database error/no info'})
            return



class ISOInfo(ISOAbstractHandler):
    def get_data(self):
        db = r.db(opts.database)
        try:
            d = db.table('isos').get(self.uuid).run()
            return d
        except Exception as e:
            self.log.error("Exception: {0}".format(e))
            self.set_status(500)
            self.write({'status': 'database error/no info'})
            return


class DestroyVM(VMAbstractHandler):
    access = 'destroy'
    _ASYNC_KEY = 'destroyvm'
    def get_data(self):
        uuid = self.get_argument('uuid')

        def run(auth):
            task = VM(auth, uuid=uuid).async_destroy()
            if task:
                self.async_run(task)
                return {'task': task}

        self.try_xenadapter(run)

class DestroyVDI(VDIAbstractHandler):
    access = 'destroy'
    _ASYNC_KEY = 'destroyvdi'
    def get_data(self):
        uuid = self.get_argument('uuid')

        def run(auth):
            task = VDI(auth, uuid=uuid).async_destroy()
            if task:
                self.async_run(task)
                return {'task': task}

        self.try_xenadapter(run)

class StartStopVM(VMAbstractHandler):
    access = 'launch'
    _ASYNC_KEY = 'startstopvm'
    def get_data(self):
        uuid = self.get_argument('uuid')
        enable = self.get_argument('enable')

        if isinstance(enable, str) and enable.lower() == "false":
            enable = False

        def run(auth):
            task = VM(auth, uuid=uuid).start_stop_vm(enable)
            if task:
                self.async_run(task)
                return {'task': task}

        self.try_xenadapter(run)


class RebootVM(VMAbstractHandler):
    access = 'launch'
    _ASYNC_KEY = 'rebootvm'
    def get_data(self):
        uuid = self.get_argument('uuid')

        def run(auth):
            task = VM(auth, uuid=uuid).async_clean_reboot()
            if task:
                self.async_run(task)
                return {'task': task}

        self.try_xenadapter(run)


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
            secret = token_urlsafe()
            secrets[secret] = {
                'uuid': vm_uuid,
                'auth' : auth
            }


            url = f'ws://{opts.vmemperor_host}:{opts.vmemperor_port}/console?secret={secret}'
            self.log.debug(f"VNC Console URL for uuid: {vm_uuid}: {url}")
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
        iso = self.get_argument('iso')
        action = self.get_argument('action')
        if action == 'attach':
            is_attach = True
        elif action == 'detach':
            is_attach = False
        else:
            self.set_status(400)
            self.write({'status': 'error', 'message': 'invalid parameter "action": should be one of '
                                                      '"attach", "detach", got %s' % action})
            return

        db = r.db(opts.database)
        res = db.table('isos').get(iso).run()
        if res:
            self.log.info("UUID {1} valid, {0}...".format(
                "attaching" if is_attach else "detaching",
                iso))

            def attach(auth: BasicAuthenticator):
                _iso = ISO(uuid=iso, auth=auth)
                if is_attach:
                    _iso.attach(self.vm)
                else:
                    _iso.detach(self.vm)

            self.try_xenadapter(attach)
        else:
            self.log.info("UUID {1} invalid, not {0}...".format("attaching" if is_attach else "detaching",
                                                                iso))
            self.set_status(400)
            self.write({'status': 'error', 'message': 'invalid UUID iso_uuid'})
            return


class AttachDetachVDI(VMAbstractHandler):
    access = 'attach'

    def get_data(self):
        vdi = self.get_argument('vdi')

        action = self.get_argument('action')
        if action == 'attach':
            is_attach = True
        elif action == 'detach':
            is_attach = False
        else:
            self.set_status(400)
            self.write({'status': 'error', 'message': 'invalid parameter "action": should be one of '
                                                      '"attach", "detach", got %s' % action})
            return

        vdi = self.get_argument('vdi')

        _vdi = VDIorISO(auth=self.user_authenticator, uuid=vdi)

        try:
            _vdi.check_access('attach')
        except XenAdapterUnauthorizedActionException as e:
            self.set_status(403)
            self.write({'status': 'access denied', 'message': e.message})
            return

        def attach(auth):

            if is_attach:
                _vdi.attach(self.vm)
            else:
                _vdi.detach(self.vm)

        self.try_xenadapter(attach)


class NetworkAction(VMAbstractHandler):
    access = 'attach'

    def get_data(self):
        _net = self.get_argument('net')

        action = self.get_argument('action')
        if action == 'attach':
            is_attach = True
        elif action == 'detach':
            is_attach = False
        else:
            self.set_status(400)
            self.write({'status': 'error', 'message': 'invalid parameter "action": should be one of '
                                                      '"attach", "detach", got %s' % action})
            return

        net = Network(auth=self.user_authenticator, uuid=_net)

        try:
            net.check_access('attach')
        except XenAdapterUnauthorizedActionException as e:
            self.set_status(403)
            self.write({'status': 'access denied', 'message': e.message})
            return

        def attach(auth):
            # TODO support arguments: MAC. MTU, qos_algorithm_type
            if is_attach:
                net.attach(self.vm)
            else:
                net.detach(self.vm)

        self.try_xenadapter(attach)


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
            self.log.debug("Creating databases...")
            if opts.database in r.db_list().run():
                r.db_drop(opts.database).run()

            r.db_create(opts.database).run()
            self.db = r.db(opts.database)

            # create database for async tasks
            self.db.table_create('tasks', durability='soft').run()
            self.db.table('tasks').wait()

            try:
                authenticator.xen = XenAdapter({**opts.group_dict('xenadapter'), **opts.group_dict('rethinkdb')})
            except XenAdapterConnectionError as e:
                raise XenAdapterAPIError(self.log, "XenServer not reached", e.message)

            self.xen = XenAdapter({**opts.group_dict('xenadapter'), **opts.group_dict('rethinkdb')})
            for obj in objects:
                obj.create_db(self.db)

            del authenticator.xen

    def do_user_table(self):
        try:
            conn = ReDBConnection().get_connection()
            log = self.log
            with conn:
                self.db.table_create('users', durability='soft').run()
                self.db.table_create('groups', durability='soft').run()
                users = self.authenticator.get_all_users(log=log)
                groups = self.authenticator.get_all_groups(log=log)
                self.db.table('users').insert(users, conflict='update').run()
                self.db.table('groups').insert(groups, conflict='update').run()
                while True:
                    if need_exit.is_set():
                        return
                    delay = 0
                    while True:
                        if opts.user_source_delay <= delay:
                            break
                        if need_exit.is_set():
                            return
                        sleep_time = 2
                        time.sleep(sleep_time)
                        delay += sleep_time

                    new_users = self.authenticator.get_all_users(log=log)
                    new_groups = self.authenticator.get_all_groups(log=log)
                    self.db.table('users').insert(new_users, conflict='update').run()
                    self.db.table('groups').insert(new_groups, conflict='update').run()

                    new_users_set = set(map(lambda item: item['id'], new_users))
                    users_set = set(map(lambda item: item['id'], users))
                    difference = users_set.difference(new_users_set)
                    if difference:
                        self.db.table('users').get(*difference).delete().run()

                    new_groups_set = set(map(lambda item: item['id'], new_users))
                    groups_set = set(map(lambda item: item['id'], users))
                    difference = groups_set.difference(new_groups_set)
                    if difference:
                        self.db.table('groups').get(*difference).delete().run()


        except Exception as e:
            self.log.error(f"Exception in user_table: {e}")
            traceback.print_exc()
            # tornado.ioloop.IOLoop.current().run_in_executor(self.executor, self.do_access_monitor)
            raise e

    def do_access_monitor(self):
        try:
            conn = ReDBConnection().get_connection()
            # log = self.create_additional_log('AccessMonitor')
            log = self.log
            with conn:
                table_list = self.db.table_list().run()

                query = self.db.table(objects[0].db_table_name).pluck('uuid', 'access') \
                    .merge({'table': objects[0].db_table_name}).changes(include_initial=True, include_types=True)

                def initial_merge(table):
                    nonlocal table_list

                    self.db.table(table).wait().run()
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
                    # self.db.table(table_user).index_create('uuid', r.row['uuid']).run()
                    # self.db.table(table_user).index_wait('uuid').run()

                i = 0
                while i < len(objects):

                    initial_merge(objects[i].db_table_name)

                    if i > 0:
                        query = query.union(self.db.table(objects[i].db_table_name).pluck('uuid', 'access') \
                                            .merge({'table': objects[i].db_table_name}).changes(include_initial=True,
                                                                                                include_types=True))
                    i += 1

                # indicate that vms_user table is ready
                user_table_ready.set()
                self.log.debug("Changes query: {0}".format(query))
                cur = query.run()
                self.log.debug("Started access_monitor in thread {0}".format(threading.get_ident()))

                def uuid_delete(table_user, uuid):
                    CHECK_ER(self.db.table(table_user).filter({'uuid': uuid}).delete().run())

                while True:
                    try:
                        record = cur.next(1)
                    except ReqlTimeoutError as e:
                        if need_exit.is_set():
                            self.log.debug("Exiting access_monitor")
                            return
                        else:
                            continue

                    if record['new_val']:  # edit
                        uuid = record['new_val']['uuid']
                        table = record['new_val']['table']
                        access = record['new_val'].get('access', [])
                        table_user = table + '_user'

                        # if record['old_val']:
                        #    access_to_remove = \
                        #        set((frozendict(x) for x in record['old_val']['access'])) -\
                        #         set((frozendict(x) for x in access))
                        #    if access_to_remove:
                        #        log.info("Removing access rights for {0} (table {1}): {2}"
                        #        .format(uuid, table, json.dumps(access_to_remove, cls=FrozenDictEncoder)))

                        #    for item in access_to_remove:
                        #        CHECK_ER(self.db.table(table_user).get_all([record['old_val']['uuid'], item['userid']], index='uuid_and_userid').delete().run())

                        if 'old_val' not in record or not record['old_val']:
                            if access:
                                log.info("Adding access rights for %s (table %s): %s" %
                                         (uuid, table, json.dumps(access)))
                            for item in access:
                                CHECK_ER(self.db.table(table_user).insert(r.expr(item).merge({'uuid': uuid})).run())
                        else:

                            access_diff = set((frozendict(x) for x in access)) - \
                                          set((frozendict(x) for x in record['old_val']['access'])
                                              if 'access' in record['old_val'] else [])

                            if access_diff:
                                log.info("Adding access rights for %s (table %s): %s" %
                                         (uuid, table, json.dumps(access_diff, cls=FrozenDictEncoder)))
                            for item in access_diff:
                                CHECK_ER(self.db.table(table_user).insert(r.expr(item).merge({'uuid': uuid})).run())



                    else:
                        uuid = record['old_val']['uuid']
                        table = record['old_val']['table']
                        table_user = table + '_user'
                        log.info("Deleting access rights for %s (table %s)" % (uuid, table))
                        uuid_delete(table_user, uuid)
        except Exception as e:
            self.log.error("Exception in access_monitor: {0}"
                           .format(e))
            traceback.print_exc()
            # tornado.ioloop.IOLoop.current().run_in_executor(self.executor, self.do_access_monitor)
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

        def print_event(event):
            ordered = OrderedDict(event)
            ordered.move_to_end("operation", last=False)
            ordered.move_to_end("class", last=False)
            return ordered

        with conn:
            self.log.debug("Started process_xen_events. You can kill this thread and 'freeze'"
                           " cache databases (except for access) by sending signal USR2")
            first_batch_of_events.clear()

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
                        if event['class'] == 'message':
                            continue  # temporary hardcode to fasten event handling
                        log_this = opts.log_events and event['class'] in opts.log_events.split(',') \
                                   or not opts.log_events

                        # similarly to list_vms -> process
                        if event['class'] == 'vm_metrics':
                            ev_class = VM  # use methods filter_record, process_record (classmethods)
                        elif event['class'] == 'vm':
                            ev_class = [VM, Template]

                        elif event['class'] == 'network':
                            ev_class = Network
                        elif event['class'] == 'sr':
                            ev_class = SR

                        elif event['class'] == 'vdi':
                            ev_class = [ISO, VDI]
                        elif event['class'] == 'vif':
                            ev_class = VIF
                        elif event['class'] == 'vm_guest_metrics':
                            ev_class = VMGuest
                        elif event['class'] == 'vbd':
                            ev_class = VBD

                        else:  # Implement ev_classes for all types of events
                            if log_this:
                                self.log.debug(
                                    "Ignored Event: %s" % json.dumps(print_event(event), cls=DateTimeEncoder))
                            continue

                        if log_this:
                            self.log.debug("Event: %s" % json.dumps(print_event(event), cls=DateTimeEncoder))

                        try:
                            if isinstance(ev_class, list):
                                for cl in ev_class:
                                    cl.process_event(self.authenticator, event, self.db, self.authenticator.__name__)
                            else:
                                ev_class.process_event(self.authenticator, event, self.db, self.authenticator.__name__)
                        except Exception as e:
                            self.log.error("Failed to process event: class %s, error: %s" % (ev_class, e))
                            traceback.print_exc()

                    if not first_batch_of_events.is_set():
                        first_batch_of_events.set()


                except Failure as f:
                    if f.details == ["EVENTS_LOST"]:
                        self.log.warning("Reregistering for events")
                        xen.api.event.register(event_types)


def event_loop(executor, authenticator=None, ioloop=None):
    if not ioloop:
        ioloop = tornado.ioloop.IOLoop.instance()

    try:
        loop_object = EventLoop(executor, authenticator)
    except XenAdapterAPIError as e:
        print(f'Launch error: {e.message}: {e.details}')
        exit(2)

    # tornado.ioloop.PeriodicCallback(loop_object.vm_list_update, delay).start()  # read delay from ini

    ioloop.run_in_executor(executor, loop_object.do_access_monitor)
    ioloop.run_in_executor(executor, loop_object.do_user_table)
    xen_events_run.set()
    ioloop.run_in_executor(executor, loop_object.process_xen_events)

    def usr2_signal_handler(num, stackframe):
        if xen_events_run.is_set():
            xen_events_run.clear()
        else:
            xen_events_run.set()

    signal.signal(signal.SIGUSR2, usr2_signal_handler)

    return ioloop


class Postinst(BaseHandler):
    def get(self):
        os = self.get_argument("os")
        pubkey_path = pathlib.Path(ansible_pubkey)
        pubkey = pubkey_path.read_text()
        self.render('templates/installation-scenarios/postinst/{0}'.format(os), pubkey=pubkey)


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
                     'swap': ''}
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

            pubkey = ""  # We handle it in postinst
        if 'centos' in os_kind:
            for part in partition['expert_recipe']:
                if part['mp'] is "/":
                    part['name'] = 'root'
                else:
                    part['name'] = part['mp'].replace('/', '')
            filename = 'centos-ks.cfg'
            mirror_path = ''
            pubkey_path = pathlib.Path(ansible_pubkey)
            pubkey = pubkey_path.read_text()
        if not filename:
            raise ValueError("OS {0} doesn't support autoinstallation".format(os_kind))
        # filename = 'raid10.cfg'
        self.render("templates/installation-scenarios/{0}".format(filename), hostname=hostname, username=username,
                    fullname=fullname, password=password, mirror_url=mirror_url, mirror_path=mirror_path,
                    ip=ip, gateway=gateway, netmask=netmask, dns0=dns0, dns1=dns1, partition=partition, pubkey=pubkey,
                    postinst=URL + POSTINST_ROUTE + "?" + urlencode({'os': 'debian'}, doseq=True)
                    )


class ConsoleHandler(BaseWSHandler):
    def check_origin(self, origin):
        return True

    def initialize(self, executor):
        super().initialize(executor)

        username = opts.username
        password = opts.password
        self.auth_token = base64.encodebytes('{0}:{1}'.format
                                             (username,
                                              password).encode())


    @tornado.web.asynchronous
    def open(self):
        '''
        This method proxies WebSocket calls to XenServer
        '''


        # Get VM vnc url
        url_parsed = urlparse(self.request.uri)
        try:
            secret = parse_qs(url_parsed.query)['secret'][0]
        except KeyError:
            self.write_message("No argument secret")
            self.close()
            return


        try:
            data = secrets[secret]
        except KeyError:
            self.write_message("Invalid secret")
            self.close()
            return

        try:
            vm = VM(uuid=data['uuid'], auth=data['auth'])
            vnc_url = vm.get_vnc()
        except XenAdapterUnauthorizedActionException as ee:
            self.set_status(403)
            self.write(json.dumps({'status': 'not allowed', 'details': ee.message}))
            self.finish()


        except EmperorException as ee:
            self.set_status(400)
            self.write(json.dumps({'status': 'error', 'details': ee.message}))
            self.finish()

        vnc_url_parsed = urlsplit(vnc_url)
        port = vnc_url_parsed.port
        if port is None:
            port = 80 # TODO: If scheme is HTTPS, use 443
        self.sock = socket.create_connection((vnc_url_parsed.hostname, port))
        self.sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        self.sock.setblocking(0)
        self.halt = False
        self.translate = False
        self.key = None

        uri = f'{vnc_url_parsed.path}?{vnc_url_parsed.query}'
        lines = [
            'CONNECT {0} HTTP/1.1'.format(uri),  # HTTP 1.1 creates Keep-alive connection
            'Host: {0}'.format(opts.vmemperor_host),
            #   'Authorization: Basic {0}'.format(self.auth_token),
        ]
        self.sock.send('\r\n'.join(lines).encode())
        self.sock.send(b'\r\nAuthorization: Basic ' + self.auth_token)
        self.sock.send(b'\r\n\r\n')
        del secrets[secret]
        tornado.ioloop.IOLoop.current().spawn_callback(self.server_reading)

    def on_message(self, message):
        assert (isinstance(message, bytes))
        self.sock.send(message)

    def select_subprotocol(self, subprotocols):
        if 'binary' in subprotocols:
            proto = 'binary'
        else:
            proto = subprotocols[0] if len(subprotocols) else ""


        return proto

    @gen.coroutine
    def server_reading(self):
        try:
            data_sent = False
            http_header_read = False
            stream = tornado.iostream.IOStream(self.sock)
            while self.halt is False:
                try:
                    if not data_sent:
                        data = yield stream.read_bytes(100, partial=True)
                        if not http_header_read:
                            notok = b'200 OK' not in data
                            if notok:
                                self.log.error(f"Unable to open VNC Console {self.request.uri}: Error: {data}")
                                self.write_message(data)
                                self.close()
                                return
                            else:
                                http_header_read = True

                        try:
                            index = data.index(b'RFB')
                        except ValueError:
                            self.log.warning("server_reading: 200 OK returned, but no RFB in first data message. Continuing")
                            continue


                        data = data[index:]
                        data_sent = True
                    else:
                        data = yield stream.read_bytes(1024, partial=True)
                except StreamClosedError as e:
                    self.log.info(f"{self.request.uri}: Stream closed: {e}")
                    self.halt = True
                    self.close()
                    break
                self.write_message(data, binary=True)

        except:
            if self.halt is False:
                traceback.print_exc()
            else:
                pass

    def on_close(self):
        self.halt = True

        try:
            self.sock.send(b'close\n')
        except:
            pass
        finally:
            self.sock.close()


def make_app(executor, auth_class=None, debug=False):
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

    app = tornado.web.Application([

        (r"/login", AuthHandler, dict(executor=executor, authenticator=auth_class)),
        (r"/logout", LogOut, dict(executor=executor)),
        (r'/test', Test, dict(executor=executor)),
        (XenAdapter.AUTOINSTALL_PREFIX + r'/([^/]+)', AutoInstall, dict(executor=executor)),
        (POSTINST_ROUTE + r'.*', Postinst, dict(executor=executor)),
        (r'/console.*', ConsoleHandler, dict(executor=executor)),
        (r'/createvm', CreateVM, dict(executor=executor)),
        (r'/startstopvm', StartStopVM, dict(executor=executor)),
        (r'/rebootvm', RebootVM, dict(executor=executor)),
        (r'/vmlist', VMList, dict(executor=executor)),
        (r'/poollist', PoolList, dict(executor=executor)),
        (r'/list_pools', PoolListPublic, dict(executor=executor)),
        (r'/tmpllist', TemplateList, dict(executor=executor)),
        (r'/netlist', NetworkList, dict(executor=executor)),
        (r'/enabledisabletmpl', EnableDisableTemplate, dict(executor=executor)),
        (r'/vnc', VNC, dict(executor=executor)),
        (r'/attachdetachvdi', AttachDetachVDI, dict(executor=executor)),
        (r'/attachdetachiso', AttachDetachIso, dict(executor=executor)),
        (r'/netaction', NetworkAction, dict(executor=executor)),
        (r'/destroyvm', DestroyVM, dict(executor=executor)),
        (r'/adminauth', AdminAuth, dict(executor=executor, authenticator=auth_class)),
        (r'/convertvm', ConvertVM, dict(executor=executor)),
        (r'/installstatus', InstallStatus, dict(executor=executor)),
        (r'/vminfo', VMInfo, dict(executor=executor)),
        (r'/isolist', ISOList, dict(executor=executor)),
        (r'/vdilist', VDIList, dict(executor=executor)),
        (r'/setaccess', SetAccessHandler, dict(executor=executor)),
        (r'/getaccess', GetAccessHandler, dict(executor=executor)),
        (r'/netinfo', NetworkInfo, dict(executor=executor)),
        (r'/userinfo', UserInfo, dict(executor=executor)),
        (r'/vdiinfo', VDIInfo, dict(executor=executor)),
        (r'/isoinfo', ISOInfo, dict(executor=executor)),
        (r'/vmdiskinfo', VMDiskInfo, dict(executor=executor)),
        (r'/vmnetinfo', VMNetInfo, dict(executor=executor)),
        (r'/turntemplate', TurnTemplate, dict(executor=executor)),
        (r'/playbooks', Playbooks, dict(executor=executor)),
        (r'/executeplaybook', ExecutePlaybook, dict(executor=executor)),
        (r'/taskstatus', TaskStatus, dict(executor=executor)),
        (r'/userlist', UserList, dict(executor=executor)),
        (r'/grouplist', GroupList, dict(executor=executor)),
        (r'/alltemplates', AllTemplates, dict(executor=executor)),
        (r'/destroyvdi', DestroyVDI, dict(executor=executor))

    ], **settings)

    app.auth_class = auth_class

    from auth.sqlalchemyauthenticator import SqlAlchemyAuthenticator, User, Group
    if opts.debug and app.auth_class.__name__ == SqlAlchemyAuthenticator.__name__:
        # create test users

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
    define('debug', group='debug', type=bool, default=False)
    define('username', group='xenadapter')
    define('password', group='xenadapter')
    define('url', group='xenadapter')
    define('database', group='rethinkdb', default='test')
    define('host', group='rethinkdb', default='localhost')
    define('port', group='rethinkdb', type=int, default=28015)
    define('delay', group='ioloop', type=int, default=5000)
    define('max_workers', group='executor', type=int, default=16)
    define('vmemperor_host', group='vmemperor', default='localhost')
    define('vmemperor_port', group='vmemperor', type=int, default=8888)
    define('authenticator', group='vmemperor', default='')
    define('log_events', group='ioloop', default='')
    define('user_source_delay', group='ioloop', type=int, default=2)
    define('log_file_name', group='log', default='vmemperor.log')
    define('ansible_pubkey', group='ansible', default='~/.ssh/id_rsa.pub')
    define('ansible_playbook', group='ansible', default='ansible-playbook')
    define('ansible_dir', group='ansible', default='./ansible')
    define('ansible_logs', group='ansible', default='./ansible_logs')
    define('ansible_networks', group='ansible', default='', multiple=True)

    from os import path

    file_path = path.join(path.dirname(path.realpath(__file__)), 'login.ini')
    parse_config_file(file_path)
    global ansible_pubkey
    ansible_pubkey = path.expanduser(opts.ansible_pubkey)
    ReDBConnection().set_options(opts.host, opts.port)
    if not os.access(ansible_pubkey, os.R_OK):
        logger.warning("WARNING: Ansible pubkey {0} (ansible_pubkey config option) is not readable".format(ansible_pubkey))

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

    global URL
    URL = f"http://{opts.vmemperor_host}:{opts.vmemperor_port}"
    logger.debug(f"Listening on: {URL}")

    executor = ThreadPoolExecutor(max_workers=2048)
    app = make_app(executor)
    server = tornado.httpserver.HTTPServer(app)
    server.listen(opts.vmemperor_port, address="0.0.0.0")
    ioloop = event_loop(executor, authenticator=app.auth_class)
    logger.debug(f"Using authentication: {app.auth_class.__name__}")
    logger.debug("Loading playbooks...")
    global playbooks
    playbooks = {p.get_id(): p for p in Playbook.get_playbooks()}
    logger.debug(f"loaded  {len(playbooks)}")
    ioloop.start()

    return


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.DEBUG)
    logger.addHandler(sh)

    read_settings()

    try:
        main()
    except KeyboardInterrupt:
        pass