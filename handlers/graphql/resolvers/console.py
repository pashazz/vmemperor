from authentication import with_authentication
from connman import ReDBConnection
from consolelist import ConsoleList
from handlers.graphql.graphql_handler import ContextProtocol
from handlers.graphql.resolvers import with_connection
from xenadapter.console import Console
from xenadapter.vm import VM
from tornado.options import options
from rethinkdb import RethinkDB
r = RethinkDB()


@with_authentication(access_class=VM, access_action='vnc', id_field='vm_uuid')
@with_connection
def resolve_console(root, info, vm_uuid):
    db = r.db(options.database)
    vm = db.table(VM.db_table_name).get(vm_uuid).pluck('ref').run()
    if not vm:
        return None
    vm_ref = vm['ref']
    console = db.table(Console.db_table_name).get_all(vm_ref, index='VM')\
        .pluck('location').coerce_to('array').run()
    if not len(console):
        return None
    secret = ConsoleList.create_secret(console[0]['location'])
    return f"/console?secret={secret}"

