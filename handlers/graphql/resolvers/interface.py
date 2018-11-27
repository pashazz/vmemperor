from ..types.interface import Interface
from typing import List

def resolve_interfaces(root, info, **args) -> List[Interface]:
    def resolve_interface(key, value):
        return Interface(**{'id': key, **value})

    return [resolve_interface(k, v) for k,v in root.interfaces.items()]