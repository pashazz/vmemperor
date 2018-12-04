

def resolve_interfaces(root, info, **args):
    def resolve_interface(key, value):
        from ..types.interface import Interface
        return Interface(**{'id': key, **value})

    return [resolve_interface(k, v) for k,v in root.interfaces.items()]