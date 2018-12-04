def resolve_vms(*args, **kwargs):
    from xenadapter.vm import VM
    return VM.resolve_many(index='ref')(*args, **kwargs)


def vmType():
    from xenadapter.vm import GVM
    return GVM