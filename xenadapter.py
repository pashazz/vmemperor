import XenAPI
import json
import hooks


class XenAdapter:
    def __init__(self, endpoint, flask_session, login=None, password=None):
        """
        @type session: XenAPI.Session
        """
        self.endpoint = endpoint

        url = endpoint['url']
        session = XenAPI.Session(url)
        if not login or not password:
            if flask_session and \
                            url in flask_session and \
                            'login' in flask_session[url] and 'password' in flask_session[url]:
                login = flask_session[url]['login']
                password = flask_session[url]['password']
            else:
                raise Exception("Unauthorized")
        else:
            flask_session[url] = {'url': endpoint['url'], 'login': login, 'password': password}
        session.login_with_password(login, password)
        if session['Status'] == "Failure":
            raise Exception
        flask_session[url]['is_su'] = session.xenapi.session.get_is_local_superuser(session._session)
        self.session = session
        self.api = self.session.xenapi

    def get_template_list(self):
        print "Getting template list using fast method"
        template_list = []
        all_records = self.api.VM.get_all_records()
        for record in all_records.values():
            entry = dict()
            for field in ['is_control_domain', 'is_a_template', 'is_a_snapshot']:
                entry[field] = record[field] if field in record and record[field] != 'OpaqueRef:NULL' else None
            if not entry['is_control_domain'] and entry['is_a_template'] and not entry['is_a_snapshot']:
                for field in ['uuid', 'name_label', 'name_description', 'allowed_operations', 'tags', 'other_config']:
                    entry[field] = record[field] if field in record and record[field] != 'OpaqueRef:NULL' else None
                entry['other_config']['vmemperor_hooks'] = hooks.merge_with_dict(entry['other_config'].get('vmemperor_hooks'))

                entry['endpoint'] = self.endpoint
                if 'ubuntu' in record['name_label'].lower():
                    entry['default_mirror'] = 'http://mirror.yandex.ru/ubuntu/'
                elif 'debian' in record['name_label'].lower():
                    entry['default_mirror'] = 'http://mirror.yandex.ru/debian/'
                else:
                    entry['default_mirror'] = ''

                template_list.append(entry)
        return template_list

    def retrieve_pool_info(self):
        pool_info = dict()

        pools = self.api.pool.get_all_records()
        default_sr = None
        for pool in pools.values():
            default_sr = pool['default_SR']
        if default_sr != 'OpaqueRef:NULL':
            sr_info = self.api.SR.get_record(default_sr)
            pool_info['hdd_available'] = (int(sr_info['physical_size']) - int(sr_info['virtual_allocation']))/(1024*1024*1024)
        else:
            pool_info['hdd_available'] = None
        pool_info['host_list'] = []

        records = self.api.host.get_all_records()
        for host_ref, record in records.items():
            metrics = self.api.host_metrics.get_record(record['metrics'])
            host_entry = dict()
            for i in ['name_label', 'resident_VMs', 'software_version', 'cpu_info']:
                host_entry[i] = record[i]
            host_entry['memory_total'] = int(metrics['memory_total'])/(1024*1024)
            host_entry['memory_free'] = int(metrics['memory_free'])/(1024*1024)
            host_entry['live'] = metrics['live']
            host_entry['memory_available'] = int(self.api.host.compute_free_memory(host_ref))/(1024*1024)
            pool_info['host_list'].append(host_entry)
        print(pool_info)
        return pool_info

    def get_vms_list(self):
        vm_list = []
        all_records = self.api.VM.get_all_records()
        for record in all_records.values():
            entry = dict()
            for field in ['is_control_domain', 'is_a_template', 'is_a_snapshot']:
                entry[field] = record[field] if field in record and record[field] != 'OpaqueRef:NULL' else None
            if not max([x for x in entry.values()]):
                for field in ['uuid', 'name_label', 'name_description', 'allowed_operations',
                              'power_state', 'VCPUs_at_startup', 'memory_target', 'guest_metrics',
                              'memory_dynamic_min', 'memory_dynamic_max']:
                    entry[field] = record[field] if field in record and record[field] != 'OpaqueRef:NULL' else None
                entry['networks'] = self.api.VM_guest_metrics.get_record(entry['guest_metrics'])['networks'] if entry['guest_metrics'] else None
                entry['endpoint'] = self.endpoint

                vm_list.append(entry)

        return vm_list

    def capture_template(self, vm_uuid, enable):
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        try:
            if enable:
                self.api.VM.add_tags(vm_ref, 'vmemperor')
            else:
                self.api.VM.remove_tags(vm_ref, 'vmemperor')
            return {'status': 'success', 'details': 'template modified', 'reason': ''}, 200
        except XenAPI.Failure as e:
            return {'status': 'error', 'details': 'can not modify template', 'reason': e.details}, 409
        except Exception as e:
            return {'status': 'error', 'details': 'can not modify template', 'reason': str(e)}, 500

    def start_stop_vm(self, vm_uuid, enable):
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        try:
            if enable:
                self.api.VM.start(vm_ref, False, False)
            else:
                self.api.VM.shutdown(vm_ref)
            return {'status': 'success', 'details': 'VM power state changed', 'reason': ''}, 200
        except XenAPI.Failure as e:
            return {'status': 'error', 'details': 'Can not change VM power state', 'reason': e.details}, 409
        except Exception as e:
            return {'status': 'error', 'details': 'Can not change VM power state', 'reason': str(e)}, 500

    def set_install_options(self, vm_uuid, hooks_dict, mirror):
        vm_ref = self.api.VM.get_by_uuid(vm_uuid)
        internal_hooks = hooks.generate_other_config_entry(hooks_dict)
        try:
            self.api.VM.set_other_config(vm_ref, 'vmemperor_hooks', internal_hooks)
            self.api.VM.set_other_config(vm_ref, 'default_mirror', mirror)
            return {'status': 'success', 'details': 'Install options updated', 'reason': ''}, 200
        except XenAPI.Failure as e:
            return {'status': 'error', 'details': 'Can not set install options', 'reason': e.details}, 409
        except Exception as e:
            return {'status': 'error', 'details': 'Can not set install options', 'reason': str(e)}, 500
