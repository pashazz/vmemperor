import rethinkdb as r
from tornado.options import options as opts

from handlers.graphql.resolvers import with_connection

from ..types.network import Network
@with_connection
def resolve_networks(root, info, **args):
    db = r.db(opts.database)
    return [Network(**item) for item in db.table('nets').get_all(*root.networks).run()]

@with_connection
def resolve_network(root, info, **args):
    from ..types.network import Network
    db = r.db(opts.database)
    net_record = db.table('nets').get(root.network).run()
    return Network(**net_record)
