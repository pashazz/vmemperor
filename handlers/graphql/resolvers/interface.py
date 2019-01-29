

def resolve_interfaces(root, info, **args):
    def resolve_interface(key, value):
        from ..types.interface import Interface
        value = {k:v for k,v in value.items() if k in Interface._meta.fields}
        return Interface(**{'id': key, **value})

    return [resolve_interface(k, v) for k,v in root.interfaces.items()]