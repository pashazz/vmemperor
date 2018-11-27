from handlers.graphql.resolvers import with_connection
from tornado.options import options as opts
import rethinkdb as r

@with_connection
def resolve_sr(root, info, **args):
    from ..types.sr import SR
    db = r.db(opts.database)
    sr_record = db.table('srs').get(root.SR).run()
    return SR(**sr_record)