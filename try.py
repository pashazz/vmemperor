from configparser import ConfigParser
from xenadapter import XenAdapter
import rethinkdb as r
from rethinkdb.errors import ReqlDriverError
import sys
from ldap3 import Server, Connection, SUBTREE, ALL
from ldap3.core.exceptions import *

import netifaces

def print_list (list):
    for x in list:
        name = x['name_label']
        print(name)

def print_attributes (list):
    for x in list:
        for attr, value in x.items():
            print (attr)
        break

def choose_sr(records):
    sr_uuid = [sr['uuid'] for sr in records.values() if sr['name_label'] == 'Local storage']
    return sr_uuid[0]

def destroy_vms(xen):
    vms = xen.list_vms()
    for vm in vms:
        xen.destroy_vm(vm['uuid'])

def choose_tmpl (list):
    for x in list:
        if x['name_label'] == 'Ubuntu Trusty Tahr 14.04':
            return x['uuid']

def choose_net (records):
    for x in records.values():
        if x['name_label'] == 'Pool-wide network associated with eth0':
            return x['uuid']

def db():
    print()

    try:
        conn = r.connect(db='vmemperor').repl()
    except ReqlDriverError as e:
        print ("Failed to establish connection: {0}".format(e))
        sys.exit(1)

    config = ConfigParser()
    config.read('login.ini')
    settings = config._sections['xenadapter']
    xen = XenAdapter(settings)

    try:
        db = r.db('vmemperor')

        vms = xen.list_vms()
        db_vms = db.table('vms').pluck('uuid')
        if len(vms) != db_vms.count().run():
            db_vms = db_vms.run()
            vm_uuid = [vm['uuid'] for vm in vms]
            for doc in db_vms:
                if doc['uuid'] not in vm_uuid:
                    print(db.table('vms').get(doc['uuid']).delete().run())
                    break
    finally:
        conn.close(noreply_wait = False)

def xen():
    print()
    config = ConfigParser()
    config.read('login.ini')
    settings = config._sections['xenadapter']
    xen = XenAdapter(settings)

    try:
        # tmpl_uuid = '0124e204-5fae-48cf-beaa-05b79579ef28'
        # sr_uuid = '88458f94-2e69-6332-423a-00eba8f2008c'
        # net_uuid = '920b8d47-9945-63d8-4b04-ad06c65d950a'
        # xen.create_vm(tmpl_uuid, sr_uuid, net_uuid, '512', 'kuku', 'ubuntu', 'http://localhost:5000/preseed', 'kukuku')
        vm_uuid = '44900640-5c28-c93a-3925-78340eec50d9'
        # xen.destroy_vm(vm_uuid)
        # vm_ref = xen.api.VM.get_by_uuid(vm_uuid)
        # tmpl_ref = xen.api.VM.get_by_uuid(tmpl_uuid)
        # vm = xen.api.VM.get_record(vm_ref)
        # tmpl = xen.api.VM.get_record(tmpl_ref)
        # for key, val in vm.items():
        #     if key not in tmpl or val != tmpl[key]:
        #         print(key, val, tmpl[key])

    finally:
        xen.session._logout()

def connect():
    username = 'mailuser'
    password = 'mailuser'

    server = Server('10.10.12.9')
    conn = Connection(server, user=username, password = password, raise_exceptions=False)
    print(server.info)
    conn.bind()

    search_filter = ("(&(objectClass=person)(!(objectClass=computer))(!(UserAccountControl:1.2.840.113556.1.4.803:=2))"
                     "(cn=*)(sAMAccountName=%s))") % username
    conn.search(search_base='dc=intra,dc=ispras,dc=ru', search_filter=search_filter, attributes=['dn', 'givenName', 'mail'],
                search_scope=SUBTREE, paged_size=1)
    if conn.entries:
        try:
            mail = conn.entries[0].mail[0]
        except:
            raise ValueError('NoUserException()')
        dn = conn.entries[0].entry_get_dn()
        check_login = Connection(server, user=dn, password=password)
        if check_login.bind():
            return "Auth successful", mail
        else:
            raise ValueError('PasswordException()')
    else:
        raise ValueError('NoUserException()')

def network():
    print(type(netifaces.ifaddresses('virbr0')[netifaces.AF_INET][0]['addr']))


if __name__ == '__main__':
    network()