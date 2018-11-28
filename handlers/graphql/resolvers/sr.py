def resolve_sr(*args, **kwargs):
    from ..types.sr import SR
    return SR.one()(*args, **kwargs)