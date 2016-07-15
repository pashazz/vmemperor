import json
predefined_hooks = {
    "Nginx reverse-proxy config": {
        "ansible_playbook_file": "ansible/nginx.yml",
        "params": {
            "HTTP port on Nginx ->":    "http_in",
             "-> HTTP port on VM":      "http_out",
             "HTTPS port on Nginx ->":  "https_in",
             "-> HTTPS port on VM":     "https_out"
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


def get_hooks_parameters(other_config_entry):
    hooks = json.loads(other_config_entry)
    return {hook: predefined_hooks[hook]["params"].keys() for hook in hooks}


a = generate_other_config_entry({'Nginx reverse-proxy config': True})
print (a)
b = merge_with_dict(a)
print (b)
c = get_hooks_parameters(a)
print (c)