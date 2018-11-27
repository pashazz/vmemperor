
from . import with_connection
from tornado.options import options as opts
import rethinkdb as r
from typing import  List

@with_connection
def resolve_all_vms(root, info):
    '''
    Get all vms from
    :param root:
    :param info:
    :return:
    '''
    from ..types.vm import VM
    db = r.db(opts.database)
    return [VM(**item) for item in db.table('vms').run()]

#@with_connection

@with_connection
def resolve_vms(root, info, **args):
    from ..types.vm import VM
    db = r.db(opts.database)
    return [VM(**item) for item in db.table('vms').get_all(*root.VMs).run()]



