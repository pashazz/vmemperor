from flask import Flask
from flask import session as flask_session
from flask import render_template
from functools import wraps
from flask import request, Response

import XenAPI
import pprint
import random
import string
import time
from getvminfo import get_vms_list


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


def retrieve_vms_list(session):
    api = session.xenapi
    pp = pprint.PrettyPrinter()
    pool_master = ""
    for pool in api.pool.get_all():
        pool_master = api.pool.get_master(pool)

        for host in api.host.get_all():
            host_name_label = api.host.get_name_label(host)
            free_mem = int(api.host.compute_free_memory(host))/(1024*1024)
            metrics = api.host.get_metrics(host)
            pp.pprint("Free memory on host " + host_name_label + ": " + str(free_mem) + " MB")
            #resident_vms_list = api.host.get_resident_VMs(host)

            #pp.pprint(api.host_metrics.get_memory_actual(metrics))

    vm_list = get_vms_list(session)
    vm_list = sorted(vm_list, key=lambda k: (k['power_state'].lower(), k['name_label'].lower()))
    return vm_list



# VM_metrics.get_all()
# VM_metrics.get_start_time()
# VM_metrics.get_os_version()
# VM_metrics.get_install_time()
# VM_metrics.get_memory_actual()
# VM_metrics.get_VCPU/utilisation() #map int->float
# VM_metrics.get_state()

def check_auth(username, password, session):
    # First acquire a valid session by logging in:
    try:
        session.xenapi.login_with_password(username, password)
        return True
    except:
        return False


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        url = 'https://localhost:1443/'
        session = XenAPI.Session(url)
        if not auth or not check_auth(auth.username, auth.password, session):
            return authenticate()
        flask_session['xen_session'] = session
        return f(*args, **kwargs)
    return decorated


@app.route('/secret-page')
@requires_auth
def secret_page():
    start = time.clock()
    vm_list = retrieve_vms_list(flask_session['xen_session'])
    date = time.strftime("%d/%m/%y")
    profiling = time.clock() - start
    return render_template('index.html', vm_list=vm_list, date=date, profiling=profiling, len_vm_list=len(vm_list))


if __name__ == '__main__':
    app.secret_key = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
    #retrieve_vms_list(session)
    app.run(debug=True)