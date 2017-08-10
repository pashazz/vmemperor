from xenadapter import XenAdapter
import tornado.web
import tornado.escape
import json
from abc import ABCMeta, abstractmethod
import configparser


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
            self.write(json.dumpscd({}))
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

class AdminAuth(BaseHandler):
    def post(self):
        """ """
        self.write()


class VMList(BaseHandler):
    def get(self):
        """ """
        # read from db
        self.write()


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
        XenAdapter.create_vm()
        self.write()


class NetworkList(BaseHandler):
    def get(self):
        """ """
        # read from db
        self.write()


class CreateNetwork(BaseHandler):
    def get(self):
        """ """
        XenAdapter.create_network()
        # update db
        XenAdapter.list_networks()
        self.write()


class StartStopVM(BaseHandler):
    def post(self):
        """ """
        XenAdapter.start_stop_vm()
        # update db
        self.write()


class EnableDisableTemplate(BaseHandler):
    def post(self):
        """ """
        XenAdapter.enable_disable_template()
        self.write()


class VNC(BaseHandler):
    def get(self):
        """http://xapi-project.github.io/xen-api/consoles.html"""
        XenAdapter.get_vnc()
        self.write()


class AttachDetachDisc(BaseHandler):
    def post(self):
        XenAdapter.create_disk()
        XenAdapter.attach_disk()
        XenAdapter.detach_disk()
        XenAdapter.destroy_disk()
        # update db info
        self.write()


class DestroyVM(BaseHandler):
    def post(self):
        XenAdapter.destroy_vm()
        # update db info
        self.write()


class ConnectVM(BaseHandler):
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
    XenAdapter.list_vms()
    pass


def start_event_loop():
    pass


def make_app(auth_class = DummyAuth):
    return tornado.web.Application([
        (r"/login", auth_class),
    ])


def read_settings():
    """reads settings from ini"""
    settings = configparser.ConfigParser()
    settings.read('*.ini')
    return settings


def main():
    """ reads settings in ini configures and starts system"""
    settings = read_settings()
    make_app()
    start_event_loop()
    return

if __name__ == '__main__':
    main()

# @app.route('/')
# def secret_page():
#     return render_template('index.html')
#
#
# @app.route('/pool-index', methods=["GET"])
# def pool_index():
#     return jsonify(app.config['xen_endpoints'])


# #app.secret_key = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
# app.secret_key = 'SADFccadaeqw221fdssdvxccvsdf'
# if __name__ == '__main__':  # everything should be loaded from ini
#     #app.config.update(SESSION_COOKIE_SECURE=True)
#     app.config['SESSION_COOKIE_HTTPONLY'] = False
#     app.config['xen_endpoints'] = [
#         {'id': 'http://10.10.10.18:80/', 'url': 'http://10.10.10.18:80/', 'description': 'Pool A'},
#         #{'id': 'http://10.10.10.18:80//', 'url': 'http://10.10.10.18:80/', 'description': 'Pool Z'},
#         #{'id': 'http://172.31.0.32:80/', 'url': 'http://172.31.0.32:80/', 'description': 'Pool Z'}
#         ]
#     app.config['supported-distros'] = {'debianlike': 'all'}
#     app.config['enabled-distros'] = app.config['supported-distros']
#     app.config['supported-reverse-proxies'] = {'vmemperor-nginx': 'Nginx configuration files'}
#     app.config['enabled-reverse-proxies'] = app.config['supported-reverse-proxies']
#     app.config['vmemperor-address'] = 'http://localhost:5000/'
#     #retrieve_vms_list(session)
#     app.run(debug=True, use_reloader=True, threaded=False, host="0.0.0.0", port=5000)
