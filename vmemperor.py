from flask import Flask
from flask import session as flask_session
from flask import render_template, jsonify
from functools import wraps
from flask import request, Response, redirect, url_for, abort

import XenAPI
import os
from getvminfo import get_vms_list
from gettemplateinfo import get_template_list
import json

app = Flask(__name__, static_url_path='/static')

#@app.route('/static/js/<path:path>', methods=['GET'])
#def static(path):
#    return app.send_static_file(os.path.join('js', path))



def get_xen_session(endpoint, login=None, password=None):
    url = endpoint['url']
    session = XenAPI.Session(url)
    if login and password:
        session.login_with_password(login, password)
    else:
        session.login_with_password((flask_session[url])['login'], (flask_session[url])['password'])
    print session
    return session


def retrieve_pool_info(endpoint):
    session = get_xen_session(endpoint)
    api = session.xenapi
    pool_info = dict()

    pools = api.pool.get_all_records()
    #there is always one pool in session in our case
    default_sr = None
    for pool in pools.values():
        default_sr = pool['default_SR']
    if default_sr != 'OpaqueRef:NULL':
        sr_info = api.SR.get_record(default_sr)
        pool_info['hdd_available'] = (int(sr_info['physical_size']) - int(sr_info['virtual_allocation']))/(1024*1024*1024)
    else:
        pool_info['hdd_available'] = None
    pool_info['host_list'] = []


    records = api.host.get_all_records()
#    return api.host.get_all_records()
    for host_ref, record in records.iteritems():
        metrics = api.host_metrics.get_record(record['metrics'])
        print record
        host_entry = dict()
        host_entry['name_label'] = record['name_label']
        host_entry['resident_VMs'] = record['resident_VMs']
        host_entry['software_version'] = dict()
        host_entry['software_version'] = record['software_version']
        host_entry['cpu_info'] = dict(record['cpu_info'])
        host_entry['memory_total'] = int(metrics['memory_total'])/(1024*1024)
        host_entry['memory_free'] = int(metrics['memory_free'])/(1024*1024)
        memory_available = api.host.compute_free_memory(host_ref)
        host_entry['memory_available'] = int(memory_available)/(1024*1024)
        host_entry['live'] = metrics['live']
        pool_info['host_list'].append(host_entry)
    print(pool_info)
    return pool_info


#    pool_master = ""

#    for pool in api.pool.get_all():
#    pool_master = api.pool.get_master(pool)

#    for host in api.host.get_all():
#        host_name_label = api.host.get_name_label(host)
#        free_mem = int(api.host.compute_free_memory(host))/(1024*1024)


def retrieve_vms_list(endpoint):
    session = get_xen_session(endpoint)
    vm_list = get_vms_list(session, endpoint)
    return vm_list


def retrieve_template_list(endpoint):
    session = get_xen_session(endpoint)
    api = session.xenapi
    template_list = get_template_list(session, endpoint)
    return template_list



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
    except Exception as e:
        print (e)
        return False


def check_if_superuser(session):
    try:
        is_a_superuser = session.xenapi.session.get_is_local_superuser(session._session)
        print ("Is a superuser?", is_a_superuser)
        return is_a_superuser
    except:
        return False


@app.route("/auth", methods=['GET', 'POST'])
def authenticate():
    """Sends a 401 response that enables basic auth"""
    if request.method == 'GET':
        return render_template("auth.html", xen_endpoints=app.config['xen_endpoints'])
    if request.method == 'POST':
        counter = 0
        is_su = True
        form = request.form if request.form else json.loads(request.data)
        for endpoint in app.config['xen_endpoints']:
            login = form['login' + str(counter)]
            password = form['password' + str(counter)]
            session = XenAPI.Session(endpoint['url'])
            if check_auth(login, password, session):
                flask_session[endpoint['url']] = {'url': endpoint['url'], 'login': login, 'password': password}
                print "Auth successful"
                is_su = check_if_superuser(session) and is_su
                print is_su
                #print flask_session[endpoint]['url']
            else:
                print "FAILED TO AUTH ON " + endpoint['description']
        flask_session['is_su'] = is_su

        return '[]'


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        for endpoint in app.config['xen_endpoints']:
            if endpoint['url'] in flask_session:
                if not flask_session[endpoint['url']]['url'] \
                        or not flask_session[endpoint['url']]['login'] \
                        or not flask_session[endpoint['url']]['password']:
                    response = jsonify({'status': 'error', 'details': url_for('authenticate'),
                                        'reason': 'This page requires auth: session expired or have logged out'})
                    response.status_code = 401
                    return response
            else:
                print ("Missing auth info for ", endpoint)
                response = jsonify({'status': 'error', 'details': url_for('authenticate'),
                                    'reason': 'This page requires auth: missing auth info for ' + endpoint['description']})
                response.status_code = 401
                return response

        return f(*args, **kwargs)
    return decorated


@app.route('/list-vms')
@requires_auth
def list_vms():
    vm_list = []
    for endpoint in app.config['xen_endpoints']:
        vm_list.extend(retrieve_vms_list(endpoint))
    return json.dumps(vm_list)
    # vm_list = sorted(vm_list, key=lambda k: (k['power_state'].lower(), k['name_label'].lower()))
    # return render_template('vms.html', vm_list=vm_list)

@app.route('/list-templates')
@requires_auth
def list_templates():
    template_list = []
    if 'is_su' in flask_session and flask_session['is_su']:
        for endpoint in app.config['xen_endpoints']:
            template_list.extend(retrieve_template_list(endpoint))
        template_list = sorted(template_list, key=lambda k: (-len(k['tags']), k['name_label'].lower()))
    return json.dumps(template_list)
    # return render_template('vm_templates.html', template_list=template_list)


@app.route('/get-create-vm-params', methods=['GET'])
@requires_auth
def list_enabled_templates():
    endpoint_url = request.args.get('pool-select')
    if not endpoint_url:
        response = {'status': 'error', 'details': 'Syntax error in your query', 'reason': 'missing argument'}
        return jsonify(response), 406
    if endpoint_url == '--':
        response = jsonify({"": "Select template"})
        response.status_code = 200
        return response

    endpoint = {'url': endpoint_url, 'description': ''}
    template_list = []
    template_list.extend(item for item in retrieve_template_list(endpoint) if 'tags' in item and 'vmemperor' in item['tags'])
    template_dict = {}
    for item in template_list:
        template_dict[item['uuid']] = item['name_label']
    response = jsonify(template_dict)
    response.status_code = 200
    return response



@app.route('/create-vm', methods=['GET', 'POST'])
@requires_auth
def create_vm():
    if request.method == 'GET':
        return render_template('create_vm.html', xen_endpoints=app.config['xen_endpoints'])


@app.route('/')
def secret_page():
    return render_template('index.html')


@app.route('/start-vm', methods=['POST'])
@requires_auth
def start_vm():
    form = request.form if request.form else json.loads(request.data)
    vm_uuid = form.get('vm_uuid')
    endpoint_url = form.get('endpoint_url')
    endpoint_description = form.get('endpoint_description')
    if not vm_uuid or not endpoint_url or not endpoint_description:
        response = {'status': 'error', 'details': 'Syntax error in your query', 'reason': 'missing argument'}
        return jsonify(response), 406

    endpoint = {'url': endpoint_url, 'description': endpoint_description}
    session = get_xen_session(endpoint)
    api = session.xenapi
    vm_ref = api.VM.get_by_uuid(vm_uuid)
    try:
        api.VM.start(vm_ref, False, False)
        response = jsonify({'status': 'success', 'details': 'VM started', 'reason': ''})
        response.status_code = 200
        return response
    except XenAPI.Failure as e:
        print e.details
        response = jsonify({'status': 'error', 'details': 'Can not start VM', 'reason': e.details})
        response.status_code = 409
        return response

@app.route('/shutdown-vm', methods=['POST'])
@requires_auth
def shutdown_vm():
    form = request.form if request.form else json.loads(request.data)
    vm_uuid = form.get('vm_uuid')
    endpoint_url = form.get('endpoint_url')
    endpoint_description = form.get('endpoint_description')
    if not vm_uuid or not endpoint_url or not endpoint_description:
        response = {'status': 'error', 'details': 'Syntax error in your query', 'reason': 'missing argument'}
        return jsonify(response), 406

    endpoint = {'url': endpoint_url, 'description': endpoint_description}
    session = get_xen_session(endpoint)
    api = session.xenapi
    vm_ref = api.VM.get_by_uuid(vm_uuid)
    try:
        api.VM.shutdown(vm_ref)
        response = jsonify({'status': 'success', 'details': 'VM shutdown', 'reason': ''})
        response.status_code = 200
        return response
    except XenAPI.Failure as e:
        print e.details
        response = jsonify({'status': 'error', 'details': 'Can not shutdown VM', 'reason': e.details})
        response.status_code = 409
        return response


@app.route('/enable-template', methods=['POST'])
@requires_auth
def enable_template():
    form = request.form if request.form else json.loads(request.data)
    vm_uuid = form.get('vm_uuid')
    endpoint_url = form.get('endpoint_url')
    endpoint_description = form.get('endpoint_description')
    if not vm_uuid or not endpoint_url or not endpoint_description:
        response = {'status': 'error', 'details': 'Syntax error in your query', 'reason': 'missing argument'}
        return jsonify(response), 406

    endpoint = {'url': endpoint_url, 'description': endpoint_description}
    session = get_xen_session(endpoint)
    api = session.xenapi
    vm_ref = api.VM.get_by_uuid(vm_uuid)
    try:
        api.VM.add_tags(vm_ref, 'vmemperor')
        response = jsonify({'status': 'success', 'details': 'template is ready to use', 'reason': ''})
        response.status_code = 200
        return response
    except XenAPI.Failure as e:
        print e.details
        response = jsonify({'status': 'error', 'details': 'Can not add template to user interface', 'reason': e.details})
        response.status_code = 409
        return response


@app.route('/disable-template', methods=['POST'])
@requires_auth
def disable_template():
    form = request.form if request.form else json.loads(request.data)
    vm_uuid = form.get('vm_uuid')
    endpoint_url = form.get('endpoint_url')
    endpoint_description = form.get('endpoint_description')
    if not vm_uuid or not endpoint_url or not endpoint_description:
        response = jsonify({'status': 'error', 'details': 'Syntax error in your query', 'reason': 'missing argument'})
        response.status_code = 406
        return response

    endpoint = {'url': endpoint_url, 'description': endpoint_description}
    session = get_xen_session(endpoint)
    api = session.xenapi
    vm_ref = api.VM.get_by_uuid(vm_uuid)
    try:
        api.VM.remove_tags(vm_ref, 'vmemperor')
        response = jsonify({'status': 'success', 'details': 'template removed from user interface', 'reason': ''})
        response.status_code = 200
        return response
    except XenAPI.Failure as e:
        print e.details
        response = jsonify({'status': 'error', 'details': 'Can not remove template from user interface', 'reason': e.details})
        response.status_code = 409
        return response

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    flask_session.clear()
    response = jsonify({'status': 'success', 'details': 'Logout successful', 'reason': ''})
    response.status_code = 200
    return response

@app.route('/get-pool-info', methods=['POST'])
@requires_auth
def get_pool_info():
    pool = request.form.get('pool-select')
    if not pool or pool == '--':
        response = jsonify({'status': 'error', 'details': 'You must choose a pool', 'reason': 'Pool is not specified'})
        response.status_code = 406
        return response
    pool_exists = False
    for endpoint in app.config['xen_endpoints']:
        if endpoint['url'] == pool:
            pool_exists = True
    if not pool_exists:
        response = jsonify({'status': 'error', 'details': 'You have chosen unknown pool or server', 'reason': 'Pool url is invalid'})
        response.status_code = 406
        return response
    endpoint = {'url': pool, 'description': ''}
    pool_info = retrieve_pool_info(endpoint)
    return render_template("pool_info.html", pool_info=pool_info)


@app.route('/list-pools', methods=['GET'])
@requires_auth
def list_pools():
    pool_list = []
    for pool in app.config['xen_endpoints']:
        pool_info = retrieve_pool_info(pool)
        pool_info.update(pool)
        pool_list.append(pool_info)
        template_list = []
        template_list.extend(item for item in retrieve_template_list(pool) if 'tags' in item and 'vmemperor' in item['tags'])
        template_dict = {}
        for item in template_list:
            template_dict[item['uuid']] = item['name_label']
        pool_info['templates_enabled'] = template_dict
    return json.dumps(pool_list)


@app.route('/pools/<pool_id>/auth', methods=['POST'])
def check_auth_for_pool(pool_id):
    try:
        request_data = json.loads(request.data)
        if not request_data.get('login') or not request_data.get('password'):
            return generate_response(406, 'error', 'Missing params', 'You must provide credentials for auth')

        endpoint = None
        for pool in app.config['xen_endpoints']:
            if pool['id'] == pool_id:
                endpoint = pool
        if not endpoint:
            return generate_response(404, 'error', 'Invalid pool id', 'No Xen endpoint with such id exists')

        session = XenAPI.Session(endpoint['url'])


    except TypeError as e:
        return generate_response(406, 'error', 'Wrong params', 'Provided JSON is invalid or missing: ' + e)
    except:
        return generate_response(500, 'error', 'Unknown error', 'Internal server error')








#app.secret_key = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
app.secret_key = 'SADFccadaeqw221fdssdvxccvsdf'
if __name__ == '__main__':
    #app.config.update(SESSION_COOKIE_SECURE=True)
    app.config['SESSION_COOKIE_HTTPONLY'] = False
    app.config['xen_endpoints'] = [{'id': 'sadasdasdasdas', 'url': 'http://172.31.0.14:80/', 'description': 'Pool A'},
                                   {'id': 'cxbvccvbbxcxcx', 'url': 'http://172.31.0.32:80/', 'description': 'Pool Z'}]
    app.config['supported-distros'] = {'debianlike': 'all'}
    app.config['enabled-distros'] = app.config['supported-distros']
    app.config['supported-reverse-proxies'] = {'vmemperor-nginx': 'Nginx configuration files'}
    app.config['enabled-reverse-proxies'] = app.config['supported-reverse-proxies']
    #retrieve_vms_list(session)
    app.run(debug=True)
