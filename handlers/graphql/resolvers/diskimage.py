from handlers.graphql.resolvers import with_connection
import rethinkdb as r
from tornado.options import options
from ..types.vdi import VDI
from ..types.iso import ISO
from typing import Optional, List, Union


@with_connection
def resolve_vdi(root, info, **args) -> Optional[Union[VDI, ISO]]:
    if not root:
        return None
    uuid = root.VDI
    db = r.db(options.database)
    if root.type == 'Disk':
        vdi_record = db.table('vdis').get(uuid).run()
        return VDI(**vdi_record)
    elif root.type == 'CD':
        vdi_record = db.table('isos').get(uuid).run()
        return ISO(**vdi_record)

@with_connection
def resolve_vdis(root, info, **args) -> List[Union[VDI, ISO]]:
    db = r.db(options.database)
    if root.content_type == 'iso':
        return [ISO(**item) for item in db.table('isos').get_all(*root.VDIs).run()]
    else:
        return [VDI(**item) for item in db.table('vdis').get_all(*root.VDIs).run()]


