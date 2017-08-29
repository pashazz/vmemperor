from xenadapter import XenAdapter
import tornado.web
import tornado.escape
import tornado.httpserver
import tornado.iostream
import json
from abc import ABCMeta, abstractmethod
import configparser
import socket
from tornado import gen, ioloop
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
import base64

import rethinkdb as r
from rethinkdb.errors import ReqlDriverError


import ldap3



executor = ThreadPoolExecutor(max_workers=16)  # read from settings

def CHECK_ER(ret):
    if ret['errors']:
        raise ValueError('Failed to modify data: {0}'.format(ret['first_error']))
    if ret['skipped']:
        raise ValueError('Failed to modify data: skipped - {0}'.format(ret['skipped']))

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")


class Authentication(metaclass=ABCMeta):
    @abstractmethod
    def check_credentials(self, password, username):
        """asserts credentials using inner db, or some outer authentication system"""
        return

    @abstractmethod
    def get_user_groups(self, username):
        """gets list of user groups"""
        return

    @abstractmethod
    def set_user_group(self, username, group):
        """adds user to group"""
        return

    @abstractmethod
    def set_user(self, username):
        """creates cookie given username"""
        return

@Authentication.register
class BasicAuthenticator(BaseHandler):
    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        authenticated = self.check_credentials(password, username)
        if authenticated:
            self.set_user(username)
            self.write(json.dumps({}))
        else:
            return self.write(json.dumps({"error": "wrong credentials"}))

    def set_user(self, username):
        if username:
            self.set_secure_cookie("user", tornado.escape.json_encode(username))

        else:
            self.clear_cookie("user")


class DummyAuth(BasicAuthenticator):
    def check_credentials(self, password, username):
        return True

class LDAPAuthenticator(BasicAuthenticator):
    def check_credentials(self, password, username):
        server = ldap3.Server('10.10.12.9')
        conn = ldap3.Connection(server, user='mailuser', password='mailuser', raise_exceptions=False)
        conn.bind()
        search_filter="(&(objectClass=person)(!(objectClass=computer))(!(UserAccountControl:1.2.840.113556.1.4.803:=2))(cn=*)(sAMAccountName=%s))" % username
        conn.search(search_base='dc=intra,dc=ispras,dc=ru',search_filter=search_filter,
                    attributes=['givenName', 'mail'])





"""
dbms - RethinkDB
db is used as cache
different users should see different info (i.e. only vms created by that user)


views should return info in json format
errors should be returned in next format: {'status': 'error', 'details': string, 'reason': string}

"""


class Test(BaseHandler):
    executor = executor

    @run_on_executor
    def heavy_task(self):
        return {'status': 'ok'}

    @gen.coroutine
    def get(self):
        res = yield self.heavy_task()
        self.write(json.dumps(res))


class AdminAuth(BaseHandler):
    executor = executor

    def post(self):
        """ """
        self.write()


class VMList(BaseHandler):
    executor = executor

    def get(self, user_id):
        """ """
        # read from db
        self.write(json.dumps(list))


class PoolList(BaseHandler):
    executor = executor

    def get(self):
        """ """
        # read from db
        self.write()


class TemplateList(BaseHandler):
    executor = executor

    def get(self):
        """ """
        XenAdapter.list_templates()
        self.write()


class CreateVM(BaseHandler):
    executor = executor

    def post(self):
        """ """
        settings = read_settings()['xenadapter']
        xen = XenAdapter(settings)
        tmpl_uuid = self.get_argument('template-select', )
        sr_uuid = self.get_argument('storage-select')
        net_uuid = self.get_argument('network-select')
        vdi_size = self.get_argument('hdd', '512')
        hostname = self.get_argument('hostname', '')
        os_kind = self.get_argument('os_kind', 'ubuntu')
        preseed_prefix = 'http://localhost:5000/' + 'preseed'
        vm_uuid = xen.create_vm(tmpl_uuid, sr_uuid, net_uuid, vdi_size, hostname, os_kind, preseed_prefix)
        self.write(json.dump({'vm_uuid': vm_uuid}))


class NetworkList(BaseHandler):
    executor = executor

    def get(self):
        """ """
        # read from db
        self.write()


class CreateNetwork(BaseHandler):
    executor = executor

    def get(self):
        """ """
        XenAdapter.create_network()
        # update db
        XenAdapter.list_networks()
        self.write()


class StartStopVM(BaseHandler):
    executor = executor

    def post(self):
        """ """
        XenAdapter.start_stop_vm()
        # update db
        self.write()


class EnableDisableTemplate(BaseHandler):
    executor = executor

    def post(self):
        """ """
        XenAdapter.enable_disable_template()
        self.write()


class VNC(BaseHandler):
    executor = executor

    def get(self):
        """http://xapi-project.github.io/xen-api/consoles.html"""
        XenAdapter.get_vnc()
        self.write()


class AttachDetachDisc(BaseHandler):
    executor = executor

    def post(self):
        XenAdapter.create_disk()
        XenAdapter.attach_disk()
        XenAdapter.detach_disk()
        XenAdapter.destroy_disk()
        # update db info
        self.write()


class DestroyVM(BaseHandler):
    executor = executor

    def post(self):
        XenAdapter.destroy_vm()
        # update db info
        self.write()


class ConnectVM(BaseHandler):
    executor = executor

    def post(self):
        XenAdapter.connect_vm()
        # update db info
        self.write()


class AnsibleHooks:
    # todo
    pass



class EventLoop:
    """every n seconds asks all vms about their status and updates collections (dbs, tables)
    of corresponding user, if they are logged in (have open connection to dbms notifications)
     and admin db if admin is logged in"""
    executor = executor

    def __init__(self):
        settings = read_settings()
        self.xen = XenAdapter(settings['xenadapter'])
        if 'rethinkdb' in settings:
            if 'database' in settings['rethinkdb']:
                name_db = settings['rethinkdb']['database']
            else:
                name_db = 'test'
            if 'host' in settings['rethinkdb']:
                host_db = settings['rethinkdb']['host']
            else:
                host_db = 'localhost'
            if 'port' in settings['rethinkdb']:
                port_db = settings['rethinkdb']['port']
            else:
                port_db = 28015
        else:
            name_db = 'test'
            host_db = 'localhost'
            port_db = 28015
        self.conn = r.connect(host_db, port_db, name_db).repl()
        if name_db not in r.db_list().run():
            r.db_create(name_db).run()
        self.db = r.db(name_db)
        tables = self.db.table_list().run()
        if 'vms' not in tables:
            self.db.table_create('vms', durability='soft', primary_key='uuid').run()
            vms = self.xen.list_vms()
            CHECK_ER(self.db.table('vms').insert(vms, conflict='error').run())

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


def start_event_loop(delay = 1000):
    ioloop = tornado.ioloop.IOLoop.instance()
    loop_object = EventLoop()
    tornado.ioloop.PeriodicCallback(loop_object.vm_list_update, delay).start()  # read delay from ini
    ioloop.start()
    return ioloop

class ScenarioTest(BaseHandler):
    def initialize(self):
        self.opts = dict()
        self.opts['mirror_url'] = "mirror.corbina.ru"
        self.opts['mirror_path'] = '/ubuntu/dists/precise/main/installer-amd64/'
        self.opts['fullname'] = 'John Doe'
        self.opts['username'] = 'john'
        self.opts['password'] = 'john'

    def get(self, template_name):
        self.render("templates/installation-scenarios/{0}.jinja2".format(template_name), opts=self.opts)
        # url=http://192.168.122.1:8888/scenarios/test/ubuntu


class ConsoleHandler(BaseHandler):
    SUPPORTED_METHODS = {"CONNECT"}

    def initialize(self):
        settings = read_settings()
        url = urlparse(settings['xenadapter']['url'])
        username = settings['xenadapter']['username']
        password = settings['xenadapter']['password']
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




def make_app(auth_class=DummyAuth, debug = False):
    settings = {
        "cookie_secret": "SADFccadaeqw221fdssdvxccvsdf",
        "login_url": "/login",
        "debug": debug
    }
    return tornado.web.Application([
        (r"/login", auth_class),
        (r'/test', Test),
        (r'/scenarios/test/([^/]+)', ScenarioTest),
        (r'/(console.*)', ConsoleHandler)
    ], **settings)


def read_settings():
    """reads settings from ini"""
    config = configparser.ConfigParser()
    config.read('login.ini')
    settings = {}
    for section in config._sections:
        settings[section] = dict(config._sections[section])
    return settings



def main():
    """ reads settings in ini configures and starts system"""

    settings = read_settings()
    debug = False
    if 'debug' in settings:
        if 'debug' in settings['debug']:
            debug = bool(settings['debug']['debug'])
    app = make_app(debug)

    server = tornado.httpserver.HTTPServer(app)
    server.listen(8888, address="0.0.0.0")
    delay = 1000
    if 'ioloop' in settings:
        if 'delay' in settings['ioloop']:
            delay = int(settings['ioloop']['delay'])
    ioloop = start_event_loop(delay)

    return


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
