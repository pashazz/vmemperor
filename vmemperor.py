from xenadapter import XenAdapter
import tornado.web
from tornado.escape import json_encode, json_decode
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
import pickle
import rethinkdb as r
from rethinkdb.errors import ReqlDriverError

from loggable import Loggable
import ldap3
from ldap3.utils.conv import escape_bytes
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
        super().initialize()

    def get_current_user(self):
        return self.get_secure_cookie("user")

class Authentication(metaclass=ABCMeta):
    @abstractmethod
    def check_credentials(self, password, username):
        """asserts credentials using inner db, or some outer authentication system"""
        return

    @abstractmethod
    def get_user_groups(self):
        """gets list of user groups"""
        return

    @abstractmethod
    def set_user_group(self, group):
        """adds user to group"""
        return

    @abstractmethod
    def set_user(self, username):
        """creates cookie given username"""
        return

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


@Authentication.register
class BasicAuthenticator:
    pass



class DummyAuth(BasicAuthenticator):
    def check_credentials(self, password, username):
        pass

class LDAPIspAuthenticator(BasicAuthenticator):

    @classmethod
    def guid_to_search(cls, guid):
        return escape_bytes(uuid.UUID(guid).bytes_le)


    @classmethod
    def get_all_groups(cls, log=logging):
        server = ldap3.Server('10.10.12.9')
        conn = ldap3.Connection(server, user='mailuser', password='mailuser', raise_exceptions=False)
        if conn.bind():
            log.debug("LDAP Connection established: server: {0}, user: {1}".format(server.host, conn.user))
        else:
            log.error("Unable to establish connection to LDAP server: {0}".format(server.host))

        search_filter = "(&(objectClass=group)(cn=*))"

        conn.search(search_base='dc=intra,dc=ispras,dc=ru', search_filter=search_filter,
                attributes=['sAMAccountName', 'objectGUID'], search_scope=ldap3.SUBTREE)
        if conn.entries:
            return {entry.objectGUID.value : entry.sAMAccountName.value for entry in conn.entries}

    @classmethod
    def get_group_name_by_id(cls, id, log=logging):
        server = ldap3.Server('10.10.12.9')
        conn = ldap3.Connection(server, user='mailuser', password='mailuser', raise_exceptions=False)
        if conn.bind():
            log.debug("LDAP Connection established: server: {0}, user: {1}".format(server.host, conn.user))
        else:
            log.error("Unable to establish connection to LDAP server: {0}".format(server.host))


        search_filter = "(&(objectGUID={0}))".format(cls.guid_to_search(id))


        conn.search(search_base='dc=intra,dc=ispras,dc=ru', search_filter=search_filter,
                attributes=['sAMAccountName'], search_scope=ldap3.SUBTREE, paged_size=1)
        if conn.entries:
            return conn.entries[0].sAMAccountName.value
        else:
            log.error("LDAP: No such group: GUID %s" % id)




    def initialize(self, executor):
        '''
        Establishes connection to a ldap server
        :return:
        '''
        super().initialize(executor)



        self.id = None


    def get_id(self):
        '''

        :return: Unique user identifier
        '''
        if not self.id:
            raise AuthenticationException()
        return self.id


    def check_credentials(self, password, username, log):
        '''
        Checks credentials
        :param password:
        :param username:
        :param log: logger
        '''
        server = ldap3.Server('10.10.12.9')
        conn = ldap3.Connection(server, user='mailuser', password='mailuser', raise_exceptions=False)
        if conn.bind():
            log.debug("LDAP Connection established: server: {0}, user: {1}".format(server.host, conn.user))
        else:
            log.error("Unable to establish connection to LDAP server: {0}".format(server.host))


        self.username=username
        self.password = password
        search_filter="(&(objectClass=person)(!(objectClass=computer))(!(UserAccountControl:1.2.840.113556.1.4.803:=2))(cn=*)(sAMAccountName=%s))" % username
        conn.search(search_base='dc=intra,dc=ispras,dc=ru',search_filter=search_filter,
        attributes=['givenName', 'mail'], search_scope=ldap3.SUBTREE, paged_size=1)
        if conn.entries:
           try:
               mail = conn.entries[0].mail[0]
               log.debug("Authentication entry found, e-mail: {0}".format(mail))


           except:
               raise AuthenticationUserNotFoundException(log,self)

           dn = conn.entries[0]
           check_login = ldap3.Connection(server, user=dn.entry_dn, password=password)
           try:
               if check_login.bind():
                   log.info("Authentication as {0} successful".format(username))
                   login_connection = check_login
                   check_login.search(search_base='dc=intra,dc=ispras,dc=ru', search_filter=search_filter,
               attributes=['objectGUID'], search_scope=ldap3.SUBTREE, paged_size=1)
                   self.id = check_login.entries[0].objectGUID.value
                   # find groups
                   conn.search(search_base='dc=intra,dc=ispras,dc=ru', search_filter=search_filter,
                               attributes=['memberOf'], search_scope=ldap3.SUBTREE, paged_size=1)
                   # group queue
                   search_filter = "(&(objectClass=group)(!(objectClass=computer))(!(UserAccountControl:1.2.840.113556.1.4.803:=2))(cn=*)(sAMAccountName=%s))"
                   log.info("Obtaining groups for %s" % username)
                   def get_group_id(name):
                       conn.search(search_base='dc=intra,dc=ispras,dc=ru', search_filter=search_filter % name,
                               attributes=['objectGUID'], search_scope=ldap3.SUBTREE, paged_size=1)
                       if conn.entries:
                           return conn.entries[0].objectGUID.value


                   groups = (group.split(',')[0].split('=')[1] for group in conn.entries[0].memberOf)
                   self.groups = {get_group_id(g): g for g in groups}


                   return
               else:
                   raise AuthenticationPasswordException(log,self)
           except: #empty password
               raise AuthenticationWithEmptyPasswordException(log,self)
        else:
            raise AuthenticationUserNotFoundException(log,self)


    def get_user_groups(self, username):
        '''
        Get dict of user groups: id -> name
        '''
        return self.groups

    def set_user_groups(self):
        raise NotImplementedError()


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
    def get(self, user_id):
        """ """
        # read from db
        self.write(json.dumps(list))


class PoolList(BaseHandler):
    def get(self):
        """ """
        # read from db
        self.write()


class TemplateList(BaseHandler):

    def get(self):
        """ """
        XenAdapter.list_templates()
        self.write()


class CreateVM(BaseHandler):

    def post(self):
        """ """
        # tmpl_uuid = '0124e204-5fae-48cf-beaa-05b79579ef28'
        # sr_uuid = '88458f94-2e69-6332-423a-00eba8f2008c'
        # net_uuid = '920b8d47-9945-63d8-4b04-ad06c65d950a'

        xen = XenAdapter(opts.group_dict('xenadapter'))
        try:
            tmpl_uuid = self.get_argument('template')
            sr_uuid = self.get_argument('storage')
            net_uuid = self.get_argument('network')
            vdi_size = self.get_argument('vdi_size')
            hostname = self.get_argument('hostname')
            name_label = self.get_argument('name_label')

        except:
            self.write_error(status_code=404)
            return

        os_kind = self.get_argument('os_kind', None)
        mode = self.get_argument('mode', 'pv')
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
        if os_kind == 'ubuntu' or os_kind == 'centos':
            # see os_kind-ks.cfg
            kwargs['fullname'] = self.get_argument('fullname')
            kwargs['username'] = self.get_argument('username')
            kwargs['password'] = self.get_argument('password')
            kwargs['mirror_url'] = self.get_argument('mirror_url')
            mirror_url = kwargs['mirror_url']
        scenario_url = 'http://'+ opts.vmemperor_url + ':' + str(opts.vmemperor_port) + XenAdapter.AUTOINSTALL_PREFIX + "/" + 'centos' + "?" + "&".join(
            ('{0}={1}'.format(k, v) for k, v in kwargs.items()))
        vm_uuid = xen.create_vm(tmpl_uuid, sr_uuid, net_uuid, vdi_size, hostname, os_kind, ip_tuple, mirror_url, scenario_url, mode,  name_label, True)

        self.write(json.dumps({'vm_uuid': vm_uuid}))


class NetworkList(BaseHandler):

    def get(self):
        """ """
        # read from db
        self.write()


class CreateNetwork(BaseHandler):

    def get(self):
        """ """
        xen = XenAdapter(opts.group_dict('xenadapter'))
        xen.create_network()
        # update db
        xen.list_networks()
        self.write()


class StartStopVM(BaseHandler):

    def post(self):
        """ """
        vm_uuid = self.get_argument('vm_uuid')
        enable = self.get_argument('enable')
        xen = XenAdapter(opts.group_dict('xenadapter'))
        xen.start_stop_vm(vm_uuid, enable)
        # update db
        self.write('ok')


class EnableDisableTemplate(BaseHandler):

    def post(self):
        """ """
        xen = XenAdapter(opts.group_dict('xenadapter'))
        xen.enable_disable_template()
        self.write()


class VNC(BaseHandler):

    def get(self):
        """http://xapi-project.github.io/xen-api/consoles.html"""
        xen = XenAdapter(opts.group_dict('xenadapter'))
        xen.get_vnc()
        self.write()


class AttachDetachDisc(BaseHandler):

    def post(self, enable):
        xen = XenAdapter(opts.group_dict('xenadapter'))
        xen.create_disk()
        xen.attach_disk()
        xen.detach_disk()
        xen.destroy_disk()
        # update db info
        self.write()


class DestroyVM(BaseHandler):

    def post(self):
        xen = XenAdapter(opts.group_dict('xenadapter'))
        xen.destroy_vm()
        # update db info
        self.write()


class ConnectVM(BaseHandler):

    def post(self):
        xen = XenAdapter(opts.group_dict('xenadapter'))
        xen.connect_vm()
        # update db info
        self.write()


class AnsibleHooks:
    # todo
    pass



class EventLoop:
    """every n seconds asks all vms about their status and updates collections (dbs, tables)
    of corresponding user, if they are logged in (have open connection to dbms notifications)
     and admin db if admin is logged in"""

    def __init__(self,   executor):
        self.executor = executor
        self.xen = XenAdapter(opts.group_dict('xenadapter'))
        self.conn = r.connect(opts.host, opts.port, opts.database).repl()
        if opts.database not in r.db_list().run():
            r.db_create(opts.database).run()
        self.db = r.db(opts.database)
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


def event_loop(executor, delay = 1000):
    ioloop = tornado.ioloop.IOLoop.instance()
    loop_object = EventLoop(executor)
    tornado.ioloop.PeriodicCallback(loop_object.vm_list_update, delay).start()  # read delay from ini

    return ioloop


class AutoInstall(BaseHandler):
    def get(self, os_kind):
        fullname = self.get_argument('fullname', default='')
        username = self.get_argument('username', default='')
        password = self.get_argument('password', default='')
        mirror_url = self.get_argument('mirror_url', default=None)

        # if not mirror_url:
        #     if os_kind == 'ubuntu':
        #         mirror_url = "http://mirror.corbina.net/ubuntu/"
        #     if os_kind == 'centos':
        #         mirror_url = "http://mirror.corbina.net/centos/7/os/x86_64/"
            # if os_kind == 'redhat':
            #     mirror_url = "ftp://mirror.corbina.net/redhat"
            # if not mirror_url:
            #     raise ValueError("No installation scenarios")
        self.render("templates/installation-scenarios/{0}-ks.cfg".format(os_kind), fullname = fullname, username = username, password = password, mirror_url=mirror_url)

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





def make_app(executor, auth_class=DummyAuth, debug = False):
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
    define('vmemperor_port', group = 'vmemperor', type = int, default = 8888)

    from os import path

    file_path = path.join(path.dirname(path.realpath(__file__)), 'login.ini')
    parse_config_file(file_path)

def main():
    """ reads settings in ini configures and starts system"""
    read_settings()
    executor = ThreadPoolExecutor(max_workers = opts.max_workers)
    app = make_app(executor, LDAPIspAuthenticator, opts.debug)
    #
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