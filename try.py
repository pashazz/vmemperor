from configparser import ConfigParser
from xenadapter import XenAdapter
import rethinkdb as r
from rethinkdb.errors import ReqlDriverError
import sys

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

def main():
    config = ConfigParser()
    config.read('login.ini')
    settings = config._sections['settings'] #dictionary
    print()

    try:
        conn = r.connect(db='vmemperor').repl()
    except ReqlDriverError as e:
        print ("Failed to establish connection: {0}".format(e))
        sys.exit(1)

    try:
        db = r.db('vmemperor')
        # doc = {
        #     'name': 'kukuku',
        #     'description': 'testing insert'
        # }
        # ret = db.table('user').insert(doc, conflict = 'error').run()
        # if ret['errors']:
        #     raise ValueError(ret['first_error'])
        print(db.table('user').pluck('name').count().run())
        print(db.table('user').get('60bf5c40-a34e-45ae-9414-a6636309e8b8').run())
    finally:
        conn.close(noreply_wait = False)


if __name__ == '__main__':
    main()