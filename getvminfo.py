### This module can fetch VM info using two methods. ###

### Get info about VMs using plain xe protocol. Should fit for any XenServer version that uses xe. ###
def get_vms_info_fallback(session):
    print "Getting VM list using fallback method"
    api = session.xenapi
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
            entry['power_state'] = api.VM.get_power_state(vm)
            entry['VCPUs_at_startup'] = api.VM.get_VCPUs_at_startup(vm)
            entry['VIFs'] = api.VM.get_VIFs(vm)
            entry['memory_target'] = str(int(api.VM.get_memory_target(vm))/(1024*1024))

            vm_list.append(entry)
    return vm_list


### Get info about VMs parsing JSON-like structure from XenServer 6.1-6.2 ###
def get_vms_info_fast(session):
    print "Getting VM list using fast method"
    api = session.xenapi
    vm_list = []
    all_records = api.VM.get_all_records()
    for record in all_records.values():
        is_control_domain = record['is_control_domain']
        is_a_template = record['is_a_template']
        is_a_snapshot = record['is_a_snapshot']
        if not is_control_domain and not is_a_template and not is_a_snapshot:
            entry = dict()
            entry['name_label'] = None or record['name_label']
            entry['allowed_operations'] = None or record['allowed_operations']
            entry['power_state'] = None or record['power_state']
            entry['VCPUs_at_startup'] = None or record['VCPUs_at_startup']
            entry['VIFs'] = None or record['VIFs']
            entry['memory_target'] = None or str(int(record['memory_target'])/(1024*1024))

            vm_list.append(entry)
    return vm_list


### Returns list of virtual machines (DomN, not control domains or templates or snapshots). ###
def get_vms_list(session):
    vm_list = []
    try:
        vm_list = get_vms_info_fast(session)
    except:
        print ("Fast method failed; using fallback.")
        vm_list = get_vms_info_fallback(session)
    finally:
        return vm_list
