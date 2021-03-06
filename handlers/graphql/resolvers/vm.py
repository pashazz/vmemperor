def resolve_vms(*args, **kwargs):
    from xenadapter.vm import VM
    field_name = None
    if 'field_name' in kwargs:
        field_name = kwargs['field_name']
        del kwargs['field_name']
    return VM.resolve_many(index='ref', field_name=field_name)(*args, **kwargs)


def vmType():
    from xenadapter.vm import GVM
    return GVM