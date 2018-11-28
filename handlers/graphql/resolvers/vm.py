def resolve_vms(*args, **kwargs):
    from ..types.vm import VM
    return VM.many()(*args, **kwargs)



