### This module can fetch VM info using two methods. ###
from XenAPI import Failure

### Get info about VMs using plain xe protocol. Should fit for any XenServer version that uses xe. ###
def get_vms_info_fallback(session, endpoint):
    print "Getting VM list using fallback method"
    vm_list = []
    api = session.xenapi
    all_vms_list = api.VM.get_all()
    for vm in all_vms_list:
        is_control_domain = api.VM.get_is_control_domain(vm)
        is_a_template = api.VM.get_is_a_template(vm)
        is_a_snapshot = api.VM.get_is_a_snapshot(vm)
        if not is_control_domain and not is_a_template and not is_a_snapshot:
            entry = dict()
            entry['uuid'] = api.VM.get_uuid(vm)
            entry['name_label'] = api.VM.get_name_label(vm)
            entry['name_description'] = api.VM.get_name_description(vm)
            entry['allowed_operations'] = api.VM.get_allowed_operations(vm)
            entry['power_state'] = api.VM.get_power_state(vm)
            entry['VCPUs_at_startup'] = api.VM.get_VCPUs_at_startup(vm)
            entry['memory_target'] = api.VM.get_memory_target(vm)
            entry['memory_dynamic_min'] = api.VM.get_memory_dynamic_min(vm)
            entry['memory_dynamic_max'] = api.VM.get_memory_dynamic_max(vm)
            get_guest_metrics = lambda x: x if x != 'OpaqueRef:NULL' else None
            entry['guest_metrics'] = get_guest_metrics(api.VM.get_guest_metrics(vm))
            entry['networks'] = api.VM_guest_metrics.get_networks(entry['guest_metrics']) if entry['guest_metrics'] else None
            entry['endpoint'] = endpoint

            vm_list.append(entry)
    return vm_list


### Get info about VMs parsing JSON-like structure from XenServer 6.1-6.2 ###
def get_vms_info_fast(session, endpoint):
    print "Getting VM list using fast method"
    api = session.xenapi
    vm_list = []
    all_records = api.VM.get_all_records()
    for record in all_records.values():
        entry = dict()
        for field in ['is_control_domain', 'is_a_template', 'is_a_snapshot']:
            entry[field] = record[field] if field in record and record[field] != 'OpaqueRef:NULL' else None
        if not max([x for x in entry.values()]):
            for field in ['uuid', 'name_label', 'name_description', 'allowed_operations',
                          'power_state', 'VCPUs_at_startup', 'memory_target', 'guest_metrics',
                          'memory_dynamic_min', 'memory_dynamic_max']:
                entry[field] = record[field] if field in record and record[field] != 'OpaqueRef:NULL' else None
            entry['networks'] = api.VM_guest_metrics.get_record(entry['guest_metrics'])['networks'] if entry['guest_metrics'] else None
            entry['endpoint'] = endpoint

            vm_list.append(entry)

    return vm_list


### Returns list of virtual machines (DomN, not control domains or templates or snapshots). ###
def get_vms_list(session, endpoint):
    vm_list = []
    try:
        vm_list = get_vms_info_fast(session, endpoint)
    except Failure as e:
        print ("Fast method failed, details:", e.details)
        try:
            vm_list = get_vms_info_fallback(session, endpoint)
        except Failure as e2:
            print ("Fallback method failed too", e2.details)

    return vm_list