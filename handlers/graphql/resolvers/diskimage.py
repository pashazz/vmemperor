from handlers.graphql.resolvers import with_connection
import rethinkdb as r
from tornado.options import options

from typing import Optional, List, Union

def resolve_vdi(root, info, **args):
    from ..types.vdi import VDI
    from ..types.iso import ISO
    if not root:
        return None
    uuid = root.VDI

    if root.type == 'Disk':
        return VDI.one()(root, info, uuid=uuid)
    elif root.type == 'CD':
        return ISO.one()(root, info, uuid=uuid)

def resolve_vdis(root, info, **args):
    '''
    Resolve VDI list of VDIs by ref
    :param root:
    :param info:
    :param args:
    :return:
    '''
    from ..types.vdi import VDI
    from ..types.iso import ISO
    if root.content_type == 'iso':
        return ISO.many(field_name='VDIs', index='ref')(root, info, **args)
    else:
        return VDI.many(field_name='VDIs', index='ref')(root, info, **args)


