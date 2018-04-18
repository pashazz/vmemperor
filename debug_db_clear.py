#!/usr/bin/env python3
from vmemperor import read_settings, opts

import rethinkdb as r
if __name__ == '__main__':
    read_settings()
    conn = r.connect(opts.host, opts.port).repl()
    base_query = r.db('rethinkdb').table('db_config').filter(r.row['name'].match('^' + opts.database))
    cur = base_query.pluck('name').run()
    for value in cur:
        name = value['name']
        try:
            r.db_drop(name).run()
        except Exception as e:
            print("Exception: ", e)
