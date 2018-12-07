from handlers.graphql.resolvers import with_connection
import rethinkdb as r
from tornado.options import options

from typing import Optional, List, Union

def resolve_vdi(root, info, **args):
    from xenadapter.disk import VDI, ISO
    if not root:
        return None

    if root.type == 'Disk':
        return ISO.resolve_one(index='ref', field_name='VDI')(root, info)
    elif root.type == 'CD':
        return VDI.resolve_one(index='ref', field_name='VDI')(root, info)

def resolve_vdis(root, info, **args):
    '''
    Resolve VDI list of VDIs by ref
    :param root:
    :param info:
    :param args:
    :return:
    '''
    from xenadapter.disk import VDI, ISO
    if root.content_type == 'iso':
        return ISO.resolve_many(field_name='VDIs', index='ref')(root, info, **args)
    else:
        return VDI.resolve_many(field_name='VDIs', index='ref')(root, info, **args)


def vdiType():
    from xenadapter.disk import DiskImage
    return DiskImage