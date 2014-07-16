### This module can fetch template info using two methods. ###
from XenAPI import Failure

### Get info about VMs using plain xe protocol. Should fit for any XenServer version that uses xe. ###
def get_template_info_fallback(session, endpoint):
    print "Getting template list using fallback method"
    api = session.xenapi
    template_list = []
    all_vms = api.VM.get_all()
    for vm in all_vms:
        entry = dict()
        entry['is_control_domain'] = api.VM.get_is_control_domain(vm)
        entry['is_a_template'] = api.VM.get_is_a_template(vm)
        entry['is_a_snapshot'] = api.VM.get_is_a_snapshot(vm)
        if not entry['is_control_domain'] and not entry['is_a_template'] and not entry['is_a_snapshot']:
            entry['allowed_operations'] = api.VM.get_allowed_operations(vm)
            entry['name_label'] = api.VM.get_name_label(vm)
            entry['name_description'] = api.VM.get_name_description(vm)
            entry['power_state'] = api.VM.get_power_state(vm)
            entry['VCPUs_at_startup'] = api.VM.get_VCPUs_at_startup(vm)
            entry['networks'] = api.VM_guest_metrics.get_networks(api.VM.get_metrics(vm))
            entry['memory_target'] = api.VM.get_memory_target(vm)
            entry['memory_dynamic_min'] = api.VM.get_memory_dynamic_min(vm)
            entry['memory_dynamic_max'] = api.VM.get_memory_dynamic_max(vm)
            entry['endpoint'] = endpoint

            template_list.append(entry)
    return template_list


### Get info about VMs parsing JSON-like structure from XenServer 6.1-6.2 ###
def get_template_info_fast(session, endpoint):
    print "Getting template list using fast method"
    api = session.xenapi
    template_list = []
    all_records = api.VM.get_all_records()
    for record in all_records.values():
        entry = dict()
        for field in ['is_control_domain', 'is_a_template', 'is_a_snapshot']:
            entry[field] = record[field] if field in record and record[field] != 'OpaqueRef:NULL' else None
        if not entry['is_control_domain'] and entry['is_a_template'] and not entry['is_a_snapshot']:
            for field in ['uuid', 'name_label', 'name_description', 'allowed_operations', 'tags', 'other_config']:
                entry[field] = record[field] if field in record and record[field] != 'OpaqueRef:NULL' else None

            entry['endpoint'] = endpoint
            if 'ubuntu' in record['name_label'].lower():
                entry['default_mirror'] = 'http://mirror.yandex.ru/ubuntu/'
            elif 'debian' in record['name_label'].lower():
                entry['default_mirror'] = 'http://mirror.yandex.ru/debian/'
            else:
                entry['default_mirror'] = ''

            template_list.append(entry)
    return template_list


### Returns list of virtual machines (DomN, not control domains or templates or snapshots). ###
def get_template_list(session, endpoint):
    template_list = []
    try:
        template_list = get_template_info_fast(session, endpoint)
    except Failure as e:
        print ("Fast method failed; using fallback.", e.details)
        try:
            template_list = get_vms_info_fallback(session, endpoint)
        except Failure as e2:
            print ("Fallback failed too, details:", e2.details)
    return template_list
