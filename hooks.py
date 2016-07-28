import json
predefined_hooks = {
    "Nginx reverse-proxy config": {
        "ansible_playbook_file": "ansible/nginx.yml",
        "manifest": {
            "options": [
                    {
                         "legend": "HTTP port on Nginx",
                         "field": "http_in",
                         "default_value": "80"
                    },
                    {
                        "legend":   "forward to HTTP port on VM",
                        "field": "http_out",
                        "default_value": "8080"
                    },
                    {
                        "legend": "HTTPS port on Nginx",
                        "field": "https_in",
                        "default_value": "443"
                    },
                    {
                        "legend":   "forward to HTTPS port on VM",
                        "field": "https_out",
                        "default_value": "443"
                    },
            ],
            "header": "Nginx reverse-proxy configuration",
            "help": "This scenario generates a configuration file to passthrough your HTTP/HTTPS traffic into your virtual machine and puts it on Nginx host. If you don't want it, don't forget to disable checkbox"
        }
    }
}


def merge_with_dict(other_config_entry):
    merged = {hook: False for hook in predefined_hooks}
    if other_config_entry:
        hooks = json.loads(other_config_entry)
        for hook_name, value in hooks.items():
            merged[hook_name] = value
    return merged


def generate_other_config_entry(hooks):
    filtered = {}
    for hook_name, value in hooks.items():
        if value:
            filtered[hook_name] = True
    return json.dumps(filtered)


def get_hooks_with_manifest(other_config_entry):
    if type(other_config_entry) is str:
        hooks = json.loads(other_config_entry)
    else:
        hooks = other_config_entry
    return {hook: predefined_hooks[hook]["manifest"] for hook in hooks}


a = generate_other_config_entry({'Nginx reverse-proxy config': True})
print (a)
b = merge_with_dict(a)
print (b)
c = get_hooks_with_manifest(a)
print (c)