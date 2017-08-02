from xenadapter import XenAdapter
import tornado.web
import tornado.escape
import json
from abc import ABCMeta, abstractmethod


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
views which get information should only get reverse polling with notifications from db (RethinkDB or CouchDB)
information should be different for different users
information in db should be updated in event loop


list vms
list vdi
list networks
create network?
create vm
start vm
stop vm
get vnc connection  -  http://xapi-project.github.io/xen-api/consoles.html
attach vbd
detach vbd
destroy vm
connect vm to network

list templates
enable template
capture template

"""


class AnsibleHooks:
    pass


def event_loop():
    pass


def make_app(auth_class = DummyAuth):
    return tornado.web.Application([
        (r"/login", auth_class),
    ])


def main():
    """ reads config in ini and configures system"""

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
