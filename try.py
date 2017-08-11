from configparser import ConfigParser
from xenadapter import XenAdapter

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

    xen = XenAdapter(settings)
    try:
        # destroy_vms(xen)

        # sr_uuid = choose_sr(xen.api.SR.get_all_records())
        # tmpl_uuid = choose_tmpl(xen.list_templates())
        # net_uuid = choose_net(xen.api.network.get_all_records())
        # vdi_size = 57767936
        # xen.create_vm(tmpl_uuid, sr_uuid, net_uuid, str(vdi_size), 'try_kuku')
        # vms = xen.list_vms()
        # print (vms[-1]['uuid'])
        # print(len(vms))

        # vms = xen.list_vms()
        # vm = vms[-1]
        # vm_uuid = vm['uuid']
        # if (vm['power_state'] != 'Running'):
        #     xen.start_stop_vm(vm_uuid, True)
        # vm_ref = xen.api.VM.get_by_uuid(vm_uuid)
        # consoles = xen.api.VM.get_consoles(vm_ref) #references
        # if (len(consoles) == 0):
        #     print('Failed to find console')
        # else:
        #     cons_ref = consoles[0]
        #     console = xen.api.console.get_record(cons_ref)
        #     url = xen.api.console.get_location(cons_ref)
        #     print(url)


        # todo что за хрень?????
        templates = xen.list_templates()
        ku = [x for x in templates if x['name_label'] == 'try_ku']
        print(len(ku))


    finally:
        xen.session._logout()

if __name__ == '__main__':
    main()