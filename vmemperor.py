from flask import Flask
from flask import session as flask_session
from flask import render_template
from functools import wraps
from flask import request, Response, redirect, url_for

import XenAPI
import pprint
import random
import string
import time
from getvminfo import get_vms_list


app = Flask(__name__)


def get_xen_session(endpoint):
    url = endpoint['url']
    print url
    session = XenAPI.Session(url)
    session.login_with_password((flask_session[url])['login'], (flask_session[url])['password'])
    return session


def retrieve_vms_list(endpoint):
    session = get_xen_session(endpoint)
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
#    pp.pprint(api.VM.get_all())
#    pp.pprint(api.VM_guest_metrics.get_all_records())

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
        if 'Status' in session:
            print session
            if session['Status'] == 'Failure':
                return False
        return True
    except:
        return False

@app.route("/auth", methods=['GET', 'POST'])
def authenticate():
    """Sends a 401 response that enables basic auth"""
    if request.method == 'GET':
        return render_template("auth.html", xen_endpoints=app.config['xen_endpoints'])
    if request.method == 'POST':
        counter = 0
        for endpoint in app.config['xen_endpoints']:
            login = request.form['login' + str(counter)]
            password = request.form['password' + str(counter)]
            session = XenAPI.Session(endpoint['url'])
            if check_auth(login, password, session):
                flask_session[endpoint['url']] = {'url': endpoint['url'], 'login': login, 'password': password}
                print "Auth successful"
                #print flask_session[endpoint]['url']
            else:
                print "FAILED TO AUTH ON " + endpoint['description']

        return redirect("/")


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        for endpoint in app.config['xen_endpoints']:
            if endpoint['url'] in flask_session:
                if not flask_session[endpoint['url']]['url'] \
                        or not flask_session[endpoint['url']]['login'] \
                        or not flask_session[endpoint['url']]['password']:
                    return redirect(url_for('authenticate'))
            else:
                print ("Missing auth info for ", endpoint)
                return redirect(url_for('authenticate'))

        return f(*args, **kwargs)
    return decorated


@app.route('/')
@requires_auth
def secret_page():
    if 'xen_session_list' in flask_session:
        print "I have saved sessions:"
        for xen_session in flask_session['xen_session_list']:
            print (xen_session)
    start = time.clock()
    vm_list = []
    for endpoint in app.config['xen_endpoints']:
        vm_list.extend(retrieve_vms_list(endpoint))
    vm_list = sorted(vm_list, key=lambda k: (k['power_state'].lower(), k['name_label'].lower()))
    date = time.strftime("%d/%m/%y")
    profiling = time.clock() - start
    return render_template('index.html', vm_list=vm_list, date=date, profiling=profiling, len_vm_list=len(vm_list))

app.secret_key = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
if __name__ == '__main__':
    #app.config.update(SESSION_COOKIE_SECURE=True)
    app.config['xen_endpoints'] = [{'url': 'https://localhost:1443/', 'description': 'Pool A'},
                                   {'url': 'https://localhost:1444/', 'description': 'Pool Z'}]
    #retrieve_vms_list(session)
    app.run(debug=True)