def resolve_hosts(*args, **kwargs):
    from xenadapter.host import Host
    field_name = None
    if 'field_name' in kwargs:
        field_name = kwargs['field_name']
        del kwargs['field_name']
    return Host.resolve_many(index='ref', field_name=field_name)(*args, **kwargs)


def hostType():
    from xenadapter.host import GHost
    return GHost

def resolve_host(*args, **kwargs):
    from xenadapter.host import Host
    return Host.resolve_one()(*args, **kwargs)