from rethinkdb import RethinkDB

import queue
from xenadapter import singleton
from loggable import Loggable
from utils import  inspect_caller
class ReDBConnection(Loggable, metaclass=singleton.Singleton):
    def __init__(self):

        self.conn_queue : queue.Queue
        self.host : str = None
        self.port : int = None
        self.db = None
        self.user : str = None
        self.password : str = None
        self.init_log()

    def set_options(self, host, port, db=None, user='admin', password=None):
        self.conn_queue = queue.Queue()
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password

        self.log.info(f"Options set: {repr(self)}")

    def __repr__(self):
        return f"ReDBConnection <host {self.host}, port {self.port}, db '{self.db}', user '{'set' if self.user else 'default'}', password '{'set' if self.password else 'default'}'>"





    def get_connection(self):
        from rethinkdb import RethinkDB
        r = RethinkDB()
        return r.connect(self.host, self.port, self.db, user=self.user, password=self.password).repl()










