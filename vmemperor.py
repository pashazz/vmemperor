from xenadapter import XenAdapter
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

def CHECK_ER(ret):
    if ret['errors']:
        raise ValueError('Failed to modify data: {0}'.format(ret['first_error']))
    if ret['skipped']:
        raise ValueError('Failed to modify data: skipped - {0}'.format(ret['skipped']))

def auth_required(method):
    def decorator(self, *args, **kwargs):
        user = self.get_current_user()
        if not user:
            self.redirect(r'/login')
        else:
            self.user_authenticator  = pickle.loads(user)
            method(self, *args, **kwargs)

    return decorator



class BaseHandler(tornado.web.RequestHandler, Loggable):

    def initialize(self, executor):
        self.executor = executor
        self.init_log()
        self.conn = r.connect(opts.host, opts.port, opts.database)
        super().initialize()

    def get_current_user(self):
        return self.get_secure_cookie("user")

    def try_xenadapter(self, func):
        try:
            ret = func()
        except XenAdapterUnauthorizedActionException as ee:
            self.set_status(403)
            self.write(json.dumps({'status' : 'not allowed', 'details' : ee.message}))

        except EmperorException as ee:
            self.set_status(400)
            self.write(json.dumps({'status' : 'error', 'details' : ee.message}))

        else:
            if ret:
                self.write(ret)
            else:
                self.write(json.dumps({'status' : 'ok'}))




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
    def initialize(self, executor):
        super().initialize(executor)


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
            xen = XenAdapter(opts.group_dict('xenadapter'), (username, password))

        except XenAdapterConnectionError as e:
            self.write(json.dumps({"status": 'error', 'message': e.message}))
            self.set_status(401)
            return

        self.write(json.dumps({}))
        self.set_secure_cookie("user", pickle.dumps((username, password)))

class LogOut(BaseHandler):
    def initialize(self, executor):
        super().initialize()

    def get(self):
        self.clear_cookie('user')
        self.redirect(self.get_argument("next", "/login"))

class VMList(BaseHandler):
    @auth_required
    def get(self):
        '''
        List of VMs available for user. For admin, return everything.
        Control domain and templates are not included
        Format: list of the following form
       [{"access": access qualificator, separated by commas. Look at XenAdapter.check_rights documentation, parameter 'action',
        "disks": list of attached VDI UUIDs,
        "power_state": see http://xapi-project.github.io/xen-api/classes/vm.html -> Enums -> vm_power_state
          "network": list of virtual network UUIDs a VM is connected to.
          "uuid": vm UUID,
          "name_label": vm human readable name}, ...]

        :return:
        '''
        #TODO where do we get user from
        if isinstance(self.user_authenticator, tuple):
            user = self.user_authenticator[0]
            userid = None
        else:
            user = self.user_authenticator.get_id()
            userid = 'users/' + user
        # read from db

        self.conn.repl()
        db = r.db(opts.database)


        result = []
        def populate_result(userid):

            #cur = table('access_list').get_all(userid, index='userid').map(
            #    lambda doc: doc.merge({'vms': doc['vms'].merge(
            #        lambda vm: table('vms').get(vm['vm_uuid'])).without('vm_uuid')}))
            if userid:
                cur= db.table('access_list').get_all(userid, index='userid').concat_map(
                lambda doc : doc['vms'].merge(
                    lambda vm : db.table('vms').get(vm['vm_uuid'])).without('vm_uuid')
                ).coerce_to('array').run()

                result.extend(cur)
            else: #root mode
                   cur = db.table('vms').map(lambda doc: doc.merge( {'access' : 'all'}))

            result.extend(cur)





        populate_result(userid)

        for group in self.user_authenticator.get_user_groups():
            groupid = 'groups/' + group
            populate_result(groupid)



        self.write(json.dumps(result))






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
        [{'uuid': template UUID,
          'name_label': template human-readable name,
          'hvm': True if this is an HVM template, False if PV template
          },...]

         """

        # read from db
        self.conn.repl()
        table = r.db(opts.database).table('tmpls')
        list = [x for x in table.run()]

        self.write(json.dumps(list))


class CreateVM(BaseHandler):

    @auth_required
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

        xen = XenAdapter(opts.group_dict('xenadapter'), self.user_authenticator)
        try:
            tmpl_name = self.get_argument('template')
            sr_uuid = self.get_argument('storage')
            net_uuid = self.get_argument('network')
            vdi_size = self.get_argument('vdi_size')
            ram_size = self.get_argument('ram_size')
            hostname = self.get_argument('hostname')
            name_label = self.get_argument('name_label')
            mirror_url = self.get_argument('mirror_url')

        except:
            self.write_error(status_code=404)
            return

        tmpls = xen.list_templates()
        if tmpl_name in tmpls.keys():
            tmpl_uuid = tmpl_name
        else:
            for tmpl in tmpls.values():
                if tmpl['name_label'] == tmpl_name:
                    tmpl_uuid = tmpl['uuid']
        if not tmpl_uuid:
            raise ValueError('Wrong template name: {0}'.format(tmpl_name))

        os_kind = self.get_argument('os_kind', None)
        override_pv_args = self.get_argument('override_pv_args', None)
        mode = self.get_argument('mode')
        self.log.info("Creating VM: name_label %s; os_kind: %s" % (name_label, os_kind))
        ip = self.get_argument('ip', '')
        gw = self.get_argument('gateway', '')
        netmask = self.get_argument('netmask', '')
        dns0 = self.get_argument('dns0', '')
        dns1 = self.get_argument('dns1', '')
        if not ip or not gw or not netmask:
            ip_tuple = None
        else:
            ip_tuple = [ip,gw,netmask]

        if dns0:
            ip_tuple.append(dns0)
        if dns1:
            ip_tuple.append(dns1)

        kwargs = {}
        if 'ubuntu' in os_kind or 'centos' in os_kind or 'debian' in os_kind:
            # see os_kind-ks.cfg
            kwargs['hostname'] = self.get_argument('hostname', default='xen_vm')
            kwargs['username'] = self.get_argument('username', default='')
            kwargs['password'] = self.get_argument('password')
            kwargs['mirror_url'] = mirror_url
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
        scenario_url = 'http://'+ opts.vmemperor_url + ':' + str(opts.vmemperor_port) + XenAdapter.AUTOINSTALL_PREFIX + "/" + os_kind.split()[0] + "?" + "&".join(
            ('{0}={1}'.format(k, v) for k, v in kwargs.items()))
        print('\n'+scenario_url+'\n')
        self.try_xenadapter(lambda  : xen.create_vm(tmpl_uuid, sr_uuid, net_uuid, vdi_size, ram_size, hostname, mode, os_kind, ip_tuple, mirror_url, scenario_url, name_label, False, override_pv_args))


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

class StartStopVM(BaseHandler):
    @auth_required
    def post(self):
        """
         Start or stop VM, requires 'launch' permission
         Arguments:
             uuid: VM UUID
             enable: True if to start VM, False if to stop VM
         """
        vm_uuid = self.get_argument('uuid')
        enable = self.get_argument('enable')
        xen = XenAdapter(opts.group_dict('xenadapter'))
        self.try_xenadapter( lambda : xen.start_stop_vm(vm_uuid, enable))


class ConvertVM(BaseHandler):
    @auth_required
    def post(self):
        vm_uuid =self.get_argument('uuid')
        xen = XenAdapter(opts.group_dict('xenadapter'))
        self.try_xenadapter(lambda: xen.convert_vm(vm_uuid))

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
        xen = XenAdapter(opts.group_dict('xenadapter'))
        self.try_xenadapter( lambda : xen.enable_disable_template(uuid, bool(enable)) )





class VNC(BaseHandler):
    @auth_required
    def get(self):
        '''
        Get VNC console url that supports HTTP CONNECT method. Requires permission 'launch'
        Arguments:
            uuid: VM UUID

        '''
        vm_uuid = self.get_argument('uuid')
        xen = XenAdapter(opts.group_dict('xenadapter'))
        def get_vnc():
            url = xen.get_vnc(vm_uuid)
            url_splitted = urlsplit(url)
            url_splitted[0] = 'http'
            url_splitted[1] = opts.vmemperor_url
            url = urlunsplit(url_splitted)
            return url
        self.try_xenadapter(get_vnc)




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
        xen = XenAdapter(opts.group_dict('xenadapter'))
        vm_uuid = self.get_argument('vm_uuid')
        vdi_uuid = self.get_argument('vdi_uuid')
        enable = self.get_argument('enable')
        def xen_call():
            if enable:
                return xen.attach_disk(vm_uuid, vdi_uuid)
            else:
                xen.detach_disk(vm_uuid, vdi_uuid)

        self.try_xenadapter(xen_call)



class DestroyVM(BaseHandler):
    @auth_required
    def post(self):
        '''
        Destroy VM. Requires permission "destroy"
        Arguments:
        uuid: VM UUID
        :return:
        '''

        xen = XenAdapter(opts.group_dict('xenadapter'))
        vm_uuid = self.get_argument('uuid')
        self.try_xenadapter(lambda : xen.destroy_vm(vm_uuid))




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
        xen = XenAdapter(opts.group_dict('xenadapter'))
        vm_uuid = self.get_argument('vm_uuid')
        net_uuid = self.get_argument('net_uuid')
        ip = self.get_argument('ip', default=None)
        self.try_xenadapter(lambda : xen.connect_vm(vm_uuid, net_uuid, ip))


class AnsibleHooks:
    # todo
    pass



class EventLoop:
    """every n seconds asks all vms about their status and updates collections (dbs, tables)
    of corresponding user, if they are logged in (have open connection to dbms notifications)
     and admin db if admin is logged in"""

    def __init__(self, executor, authenticator):
        self.executor = executor
        self.xen = XenAdapter(opts.group_dict('xenadapter'), authenticator)
        self.conn = r.connect(opts.host, opts.port, opts.database).repl()
        if opts.database not in r.db_list().run():
            r.db_create(opts.database).run()
        self.db = r.db(opts.database)
        tables = self.db.table_list().run()
        # required = ['vms', 'tmpls', 'pools', 'nets']
        if 'vms' in tables:
            self.db.table('vms').delete().run()
        if 'vms' not in tables:
            self.db.table_create('vms', durability='soft', primary_key='uuid').run()
            vms = self.xen.list_vms()
            CHECK_ER(self.db.table('vms').insert(vms, conflict='error').run())
            #self.db.table('vms').index_create('user').run()
            #self.db.table('vms').index_wait('user').run()
        else:
            vms = self.xen.list_vms()
            CHECK_ER(self.db.table('vms').insert(vms, conflict='update').run())

        if 'access_list' in tables:
            # self.db.table('access_list').delete().run()
            try:
                self.db.table_drop('access_list').run()
                tables.remove('access_list')
            except r.errors.ReqlOpFailedError as e:
                # TODO make logging
                print(e.message)
                r.db('rethinkdb').table('table_config').filter(
                    {'db': opts.database, 'name': "access_list"}).delete().run()


        if 'access_list' not in tables:
            self.db.table_create('access_list', durability='soft').run()
            access_list  = self.xen.access_list()
            CHECK_ER(self.db.table('access_list').insert(access_list, conflict='error').run())
            self.db.table('access_list').index_create('userid').run()
            self.db.table('access_list').index_wait('userid').run()

        else:
            access_list = self.xen.access_list()
            CHECK_ER(self.db.table('access_list').insert(access_list, conflict='update').run())


        if 'tmpls' not in tables:
            self.db.table_create('tmpls', durability='soft', primary_key='uuid').run()
            tmpls = self.xen.list_templates().values()
            CHECK_ER(self.db.table('tmpls').insert(list(tmpls), conflict='error').run())
        else:
            tmpls = self.xen.list_templates().values()
            CHECK_ER(self.db.table('tmpls').insert(list(tmpls), conflict='update').run())
        if 'pools' not in tables:
            self.db.table_create('pools', durability='soft', primary_key='uuid').run()
            pools = self.xen.list_pools().values()
            CHECK_ER(self.db.table('pools').insert(list(pools), conflict='error').run())
        else:
            pools = self.xen.list_pools().values()
            CHECK_ER(self.db.table('pools').insert(list(pools), conflict='update').run())
        if 'nets' not in tables:
            self.db.table_create('nets', durability='soft', primary_key='uuid').run()
            nets = self.xen.list_networks().values()
            CHECK_ER(self.db.table('nets').insert(list(nets), conflict='error').run())
        else:
            nets = self.xen.list_networks().values()
            CHECK_ER(self.db.table('nets').insert(list(nets), conflict='update').run())


    @run_on_executor
    def heavy_task(self):
        self.conn.repl()
        vms = self.xen.list_vms()
        CHECK_ER(self.db.table('vms').insert(vms, conflict = 'update').run())

        db_vms = self.db.table('vms').pluck('uuid')
        if len(vms) != db_vms.count().run():
            db_vms = db_vms.run()
            vm_uuid = [vm['uuid'] for vm in vms]
            for doc in db_vms:
                if doc['uuid'] not in vm_uuid:
                    CHECK_ER(self.db.table('vms').get(doc['uuid']).delete().run())

        # raise ValueError('SUCCESS')
        return

    @gen.coroutine
    def vm_list_update(self):
        yield self.heavy_task()


def event_loop(executor, delay = 1000, authenticator=None):
    ioloop = tornado.ioloop.IOLoop.instance()
    loop_object = EventLoop(executor, authenticator)
    tornado.ioloop.PeriodicCallback(loop_object.vm_list_update, delay).start()  # read delay from ini

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
    @tornado.web.asynchronous
    def connect(self, path):
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
        auth_class = d.load_class(class_base=BasicAuthenticator)[0]

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
        (r'/tmpllist', TemplateList, dict(executor=executor)),
        (r'/netlist', NetworkList, dict(executor=executor)),
        (r'/enabledisabletmpl', EnableDisableTemplate, dict(executor=executor)),
        (r'/vnc', VNC, dict(executor=executor)),
        (r'/attachdetachdisk', AttachDetachDisk, dict(executor=executor)),
        (r'/destroyvm', DestroyVM, dict(executor=executor)),
        (r'/connectvm', ConnectVM, dict(executor=executor)),
        (r'/adminauth', AdminAuth, dict(executor=executor)),
        (r'/convertvm', ConvertVM, dict(executor=executor))
    ], **settings)

    app.auth_class = auth_class
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
    define('vmemperor_url', group ='vmemperor', default = '10.10.10.61')
    define('vmemperor_port', group = 'vmemperor', type = int, default = 8888)

    from os import path

    file_path = path.join(path.dirname(path.realpath(__file__)), 'login.ini')
    parse_config_file(file_path)

def main():
    """ reads settings in ini configures and starts system"""
    read_settings()
    executor = ThreadPoolExecutor(max_workers = opts.max_workers)
    app = make_app(executor, debug= opts.debug)
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