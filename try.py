from configparser import ConfigParser
from XenAPI import Failure
from xenadapter import XenAdapter

def print_list (list):
    for x in list:
        name = x['name_label']
        print(name, ref)

def print_attributes (list):
    for x in list:
        for attr, value in x.items():
            print (attr)
        break

def choose_sr(records):
    for sr in records.values():
        name = sr['name_label']
        if name == 'Local storage':
            return sr['uuid']

def destroy_vms(xen):
    vms = xen.list_vms()
    for vm in vms:
        xen.destroy_vm(vm['uuid'])

def choose_tmpl (list):
    for x in list:
        if x['name_label'] == 'Ubuntu Trusty Tahr 14.04':
            return x['uuid']

def main():
    config = ConfigParser()
    config.read('login.ini')
    settings = config._sections['settings'] #dictionary
    print()

    xen = XenAdapter(settings)
    try:
        destroy_vms(xen)
        sr_uuid = choose_sr(xen.api.SR.get_all_records())
        tmpl_uuid = choose_tmpl(xen.list_templates())
        xen.create_vm(tmpl_uuid, sr_uuid, 'try_ku')
        vms = xen.list_vms()
        print(len(vms))
        # records = xen.api.VIF.get_all_records()
        # print("VIF", len(records))
        # records = xen.api.net

    finally:
        xen.session._logout()

if __name__ == '__main__':
    main()