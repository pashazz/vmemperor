from xenadapter import XenAdapter
import tornado.web
import tornado.escape
import tornado.httpserver
import json
from abc import ABCMeta, abstractmethod
import configparser

from tornado import gen, ioloop
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

import rethinkdb as r
from rethinkdb.errors import ReqlDriverError

executor = ThreadPoolExecutor(max_workers=16)  # read from settings

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
class DummyAuth(BaseHandler):
    def check_credentials(self, password, username):
        return True

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

        conn = r.connect(db='vmemperor').repl()
        db = r.db('vmemperor').run()

        try:
            doc = db.table('user').get(user_id).run()
            list = doc['VMs']
        finally:
            conn.close(noreply_wait = False)
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

    @tornado.web.authenticated
    def post(self):
        """ """
        XenAdapter.create_vm()
        self.write()


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
        r.connect(host_db, port_db, name_db).repl()
        if name_db not in r.db_list().run():
            r.db_create(name_db).run()
        self.db = r.db(name_db)
        tables = self.db.table_list().run()
        if 'vms' in tables:
            pass
        else:
            self.db.table_create('vms', durability='soft', primary_key='uuid').run()


    @run_on_executor
    def heavy_task(self):
        # vms = self.xen.list_vms()
        # for uuid in vms.keys():
        #     ret = self.db.table('vms').insert(vms[uuid], conflict = 'update').run()
        #     if ret['errors']:
        #         raise ValueError(ret['first_error'])

        pass
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
        self.opts['mirror_url'] = "http://mirror.corbina.net"
        self.opts['mirror_path'] = '/ubuntu'
        self.opts['fullname'] = 'John Doe'
        self.opts['username'] = 'john'
        self.opts['password'] = 'john'

    def get(self, template_name):
        self.render("templates/installation-scenarios/{0}.jinja2".format(template_name), opts=self.opts)

    


def make_app(auth_class=DummyAuth, debug = False):
    settings = {
        "cookie_secret": "sdvizxlklkjdsajk;jf;dsal",
        "login_url": "/login",
        "debug": debug
    }
    return tornado.web.Application([
        (r"/login", auth_class),
        (r'/test', Test),
        (r'/scenarios/test/([^/]+)', ScenarioTest)
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
    server.listen(8888)
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
