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

class BaseHandler(tornado.web.RequestHandler, Loggable):

    def initialize(self, executor):
        self.executor = executor
        self.init_log()
        self.conn = r.connect(opts.host, opts.port, opts.database)
        super().initialize()

    def get_current_user(self):
        return self.get_secure_cookie("user")



class AuthHandler(BaseHandler):

    def initialize(self, executor, authenticator):
        super().initialize(executor)
        self.authenticator = authenticator()

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        try:
            self.authenticator.check_credentials(username=username, password=password, log=self.log)
        except AuthenticationException:
            self.write(json.dumps({"error": "wrong credentials"}))
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
        """ """
        self.write()


class VMList(BaseHandler):
    def get(self):
        """ """
        #TODO where do we get user from
        user = 'root'
        # read from db
        self.conn.repl()
        table = r.db(opts.database).table('vms')
        list = [x for x in table.get_all(user, index='user').run()]

        if len(list) == 0:
            self.write('None')
        else:
            self.write(json.dumps(list))


class PoolList(BaseHandler):
    def get(self):
        """ """
        # read from db
        self.conn.repl()
        table = r.db(opts.database).table('pools')
        list = [x for x in table.run()]

        self.write(json.dumps(list))


class TemplateList(BaseHandler):

    def get(self):
        """ """

        # read from db
        self.conn.repl()
        table = r.db(opts.database).table('tmpls')
        list = [x for x in table.run()]

        self.write(json.dumps(list))


class CreateVM(BaseHandler):

    def post(self):
        """ """
        xen = XenAdapter(opts.group_dict('xenadapter'))
        try:
            tmpl_name = self.get_argument('template')
            print(tmpl_name)
            sr_uuid = self.get_argument('storage')
            net_uuid = self.get_argument('network')
            vdi_size = self.get_argument('vdi_size')
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
            kwargs['username'] = self.get_argument('username', default=None)
            kwargs['password'] = self.get_argument('password')
            kwargs['mirror_url'] = mirror_url
            kwargs['fullname'] = self.get_argument('fullname')
            kwargs['ip'] = ip
            if ip:
                kwargs['gateway'] = gw
                kwargs['netmask'] = netmask
                if dns0:
                    kwargs['dns0'] = dns0
                if dns1:
                    kwargs['dns1'] = dns1
        if 'ubuntu' in os_kind or 'debian' in os_kind:
            kwargs['mirror_url'] = kwargs['mirror_url'].split('http://')[1]
            kwargs['mirror_path'] = kwargs['mirror_url'][kwargs['mirror_url'].find('/'):]
            kwargs['mirror_url'] = kwargs['mirror_url'][:kwargs['mirror_url'].find('/')]
        scenario_url = 'http://'+ opts.vmemperor_url + ':' + str(opts.vmemperor_port) + XenAdapter.AUTOINSTALL_PREFIX + "/" + os_kind.split()[0] + "?" + "&".join(
            ('{0}={1}'.format(k, v) for k, v in kwargs.items()))
        vm_uuid = xen.create_vm(tmpl_uuid, sr_uuid, net_uuid, vdi_size, hostname, mode, os_kind, ip_tuple, mirror_url, scenario_url, name_label, False, override_pv_args)

        self.write(vm_uuid)


class NetworkList(BaseHandler):

    def get(self):
        """ """
        # read from db
        self.conn.repl()
        table = r.db(opts.database).table('nets')
        list = [x for x in table.run()]

        self.write(json.dumps(list))

class StartStopVM(BaseHandler):

    def post(self):
        """ """
        vm_uuid = self.get_argument('uuid')
        enable = self.get_argument('enable')
        xen = XenAdapter(opts.group_dict('xenadapter'))
        xen.start_stop_vm(vm_uuid, enable)
        self.write('ok')


class EnableDisableTemplate(BaseHandler):

    def post(self):
        """ """
        uuid = self.get_argument('uuid')
        enable = self.get_argument('enable')
        xen = XenAdapter(opts.group_dict('xenadapter'))
        xen.enable_disable_template(uuid, bool(enable))
        self.write('ok')


class VNC(BaseHandler):

    def get(self):
        """http://xapi-project.github.io/xen-api/consoles.html"""
        vm_uuid = self.get_argument('uuid')
        xen = XenAdapter(opts.group_dict('xenadapter'))
        url = xen.get_vnc(vm_uuid)
        self.write(url)


class AttachDetachDisk(BaseHandler):

    def post(self):
        xen = XenAdapter(opts.group_dict('xenadapter'))
        vm_uuid = self.get_argument('vm_uuid')
        vdi_uuid = self.get_argument('vdi_uuid')
        enable = self.get_argument('enable')
        if enable:
            vbd_uuid = xen.attach_disk(vm_uuid, vdi_uuid)
            self.write(vbd_uuid)
        else:
            xen.detach_disk(vm_uuid, vdi_uuid)
        self.write('ok')

class DestroyVM(BaseHandler):

    def post(self):
        xen = XenAdapter(opts.group_dict('xenadapter'))
        vm_uuid = self.get_argument('uuid')
        xen.destroy_vm(vm_uuid)
        self.write('ok')


class ConnectVM(BaseHandler):

    def post(self):
        xen = XenAdapter(opts.group_dict('xenadapter'))
        vm_uuid = self.get_argument('vm_uuid')
        net_uuid = self.get_argument('net_uuid')
        ip = self.get_argument('ip', default=None)
        vif_uuid = xen.connect_vm(vm_uuid, net_uuid, ip)
        self.write(vif_uuid)


class AnsibleHooks:
    # todo
    pass



class EventLoop:
    """every n seconds asks all vms about their status and updates collections (dbs, tables)
    of corresponding user, if they are logged in (have open connection to dbms notifications)
     and admin db if admin is logged in"""

    def __init__(self, executor):
        self.executor = executor
        self.xen = XenAdapter(opts.group_dict('xenadapter'))
        self.conn = r.connect(opts.host, opts.port, opts.database).repl()
        if opts.database not in r.db_list().run():
            r.db_create(opts.database).run()
        self.db = r.db(opts.database)
        tables = self.db.table_list().run()
        # required = ['vms', 'tmpls', 'pools', 'nets']
        # if 'vms' in tables:
        #     self.db.table('vms').delete().run()
        if 'vms' not in tables:
            self.db.table_create('vms', durability='soft', primary_key='uuid').run()
            vms = self.xen.list_vms()
            CHECK_ER(self.db.table('vms').insert(vms, conflict='error').run())
            self.db.table('vms').index_create('user').run()
            self.db.table('vms').index_wait('user').run()
        else:
            vms = self.xen.list_vms()
            CHECK_ER(self.db.table('vms').insert(vms, conflict='update').run())
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


def event_loop(executor, delay = 1000):
    ioloop = tornado.ioloop.IOLoop.instance()
    loop_object = EventLoop(executor)
    tornado.ioloop.PeriodicCallback(loop_object.vm_list_update, delay).start()  # read delay from ini

    return ioloop


class AutoInstall(BaseHandler):
    def get(self, os_kind):
        hostname = self.get_argument('hostname', default='xen_vm')
        username = self.get_argument('username', default=None)
        password = self.get_argument('password')
        mirror_url = self.get_argument('mirror_url')
        mirror_path = self.get_argument('mirror_path', default=None)
        fullname = self.get_argument('fullname')
        ip = self.get_argument('ip', default=None)
        gateway = self.get_argument('gateway', default=None)
        netmask = self.get_argument('netmask', default=None)
        dns0 = self.get_argument('dns0', default=None)
        dns1 = self.get_argument('dns1', default=None)

        if 'ubuntu' in os_kind or 'debian' in os_kind:
            filename = 'debian.jinja2'
        if 'centos' in os_kind:
            filename = 'centos-ks.cfg'
        if not filename:
            raise ValueError("OS {0} doesn't support autoinstallation".format(os_kind))
        self.render("templates/installation-scenarios/{0}".format(filename), hostname = hostname, username = username,
                    fullname=fullname, password = password, mirror_url=mirror_url, mirror_path=mirror_path, ip=ip, gateway=gateway, netmask=netmask, dns0=dns0, dns1=dns1)

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





    @tornado.web.asynchronous
    def connect(self, path):
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

    return tornado.web.Application([

        (r"/login", AuthHandler, dict(executor=executor, authenticator=auth_class)),
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
    ], **settings)


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
    define('vmemperor_port', group = 'vmemperor', type = int, default = 8889)

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
    ioloop = event_loop(executor, opts.delay)
    ioloop.start()
    return

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass