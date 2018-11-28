def resolve_networks():
    from ..types.network import Network
    return Network.many()

def resolve_network():
    from ..types.network import Network
    return Network.one()
