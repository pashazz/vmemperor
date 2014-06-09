### This module can fetch VM info using two methods. ###


### Get info about VMs using plain xe protocol. Should fit for any XenServer version that uses xe. ###
def get_template_info_fallback(session, endpoint):
    print "Getting template list using fallback method"
    vm_list = []
    all_vms_list = api.VM.get_all()
    for vm in all_vms_list:
        is_control_domain = api.VM.get_is_control_domain(vm)
        is_a_template = api.VM.get_is_a_template(vm)
        is_a_snapshot = api.VM.get_is_a_snapshot(vm)
        if not is_control_domain and not is_a_template and not is_a_snapshot:
            entry = dict()
            entry['allowed_operations'] = api.VM.get_allowed_operations(vm)
            entry['name_label'] = api.VM.get_name_label(vm)
            entry['name_description'] = api.VM.get_name_description(vm)
            entry['power_state'] = api.VM.get_power_state(vm)
            entry['VCPUs_at_startup'] = api.VM.get_VCPUs_at_startup(vm)
            entry['networks'] = api.VM_guest_metrics.get_networks(api.VM.get_metrics(vm))
            entry['memory_target'] = str(int(api.VM.get_memory_target(vm))/(1024*1024))
            entry['endpoint'] = endpoint

            vm_list.append(entry)
    return vm_list


### Get info about VMs parsing JSON-like structure from XenServer 6.1-6.2 ###
def get_template_info_fast(session, endpoint):
    print "Getting template list using fast method"
    api = session.xenapi
    template_list = []
    all_records = api.VM.get_all_records()
    for record in all_records.values():
        is_control_domain = record['is_control_domain']
        is_a_template = record['is_a_template']
        is_a_snapshot = record['is_a_snapshot']
        if not is_control_domain and is_a_template and not is_a_snapshot:
            entry = dict()
            if 'install-repository' in record['other_config']:
                print (record['name_label'])
                if 'install-distro' in record['other_config']:
                    print(record['other_config']['install-distro'])
                if 'install-repository' in record['other_config']:
                    print(record['other_config']['install-repository'])
            entry['uuid'] = record['uuid']
            entry['name_label'] = None or record['name_label']
            entry['name_description'] = None or record['name_description']
            entry['allowed_operations'] = None or record['allowed_operations']
            entry['tags'] = [] if 'tags' not in record or len(record['tags']) == 0 else record['tags']
            entry['endpoint'] = endpoint
            entry['other_config'] = record['other_config']

            template_list.append(entry)
    return template_list


### Returns list of virtual machines (DomN, not control domains or templates or snapshots). ###
def get_template_list(session, endpoint):
    template_list = []
#    try:
    template_list = get_template_info_fast(session, endpoint)
#    except:
#        print ("Fast method failed; using fallback.")
#        template_list = get_vms_info_fallback(session, endpoint)
#    finally:
    return template_list
