import rethinkdb as r
import queue
from xenadapter import singleton
from loggable import Loggable
class ReDBConnection(Loggable, metaclass=singleton.Singleton):
    def __init__(self):
        self.init_log()

    def set_options(self, host, port, db=None, user='admin', password=None):
        self.conn_queue = queue.Queue()
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password

        self.log.info("Options set: {0}".format(repr(self)))

    def __repr__(self):
        return "ReDBConnection <host {0}, port {1}, db '{2}', user '{3}', password '{4}'>".format(self.host, self.port, self.db, self.user, self.password)

    def _get_new_connection(self):
        class Connection:
            def __enter__(myself):
                if not hasattr(myself, 'conn') or not myself.conn  or not myself.conn.is_open():
                    myself.conn = r.connect(self.host, self.port,self.db, user=self.user, password=self.password)
                    self.log.info("Connecting using connection: {0}".format(myself))

                self.log.info("Repl-ing connection: {0}".format(myself))
                myself.conn.repl()

                return myself.conn

            def __exit__(myself, exc_type, exc_val, exc_tb):
                # TODO handle if connection is closed

                self.conn_queue.put_nowait(myself)
                self.log.info("Releasing connection into Queue: {0}".format(myself))

            def __repr__(myself):
                return repr(self)

        return Connection()



    def get_connection(self):
        try:
            conn =  self.conn_queue.get_nowait()
            self.log.info("Getting connection from Queue: {0}".format(conn))
            if not conn.conn.is_open():
                self.log.warn("Connection from queue is not opened, skipping")
                return self._get_new_connection()

            return conn
        except queue.Empty:
            self.log.info("No connections in Queue, creating a new one...")
            return self._get_new_connection()







