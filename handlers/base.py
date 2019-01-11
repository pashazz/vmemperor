import json
import time
from typing import Optional

from rethinkdb import RethinkDB
r = RethinkDB()
import tornado.ioloop
import tornado.web
from tornado.options import options as opts
from tornado.websocket import WebSocketHandler

from authentication import BasicAuthenticator
from connman import ReDBConnection
from constants import first_batch_of_events
from exc import XenAdapterUnauthorizedActionException, EmperorException
from loggable import Loggable
from tasks import Operations
from xenadapter.task import Task


class HandlerMethods(Loggable):
    def init_executor(self, executor):
        self.executor = executor
        self.debug = opts.debug
        self.init_log()
        self.conn = ReDBConnection().get_connection()
        first_batch_of_events.wait()
        self.actions_log = self.create_additional_log('actions')

    def get_current_user(self):
        return self.get_secure_cookie('user')

class RequestHandler(tornado.web.RequestHandler):
    def initialize(self, *args, **kwargs):
        super().initialize()

class BaseHandler(RequestHandler, HandlerMethods):
    _ASYNC_KEY = None


    def initialize(self, *args, **kwargs):

        self.init_executor(kwargs['pool_executor'])
        del kwargs['pool_executor']
        super().initialize(*args, **kwargs)

        self.user_authenticator = Optional[BasicAuthenticator]
        self.op = Operations(r.db(opts.database))





    def get_current_user(self):
        return self.get_secure_cookie("user")


    def async_run(self, task_ref):
        '''
        Run asyncronous task in executor
        :param task_ref: Task reference
        :return:
        '''
        ioloop = tornado.ioloop.IOLoop.instance()
        ioloop.run_in_executor(self.executor, self._run_async_task, task_ref)


    def _run_async_task(self, task_ref):
        task = Task(auth=self.user_authenticator, ref=task_ref)

        with ReDBConnection().get_connection():
            write_in = {'id' : task_ref}
            self.op.set_operation(self.user_authenticator, write_in)
            write_in['created'] = task.get_created()
            while task.get_status() == 'pending':
                write_in['status'] = task.get_status()
                write_in['progress'] =  task.get_progress()
                self.op.set_operation(None, write_in)
                time.sleep(1)

            write_in['finished'] = task.get_finished()
            write_in['status'] = task.get_status()
            write_in['progress'] = task.get_progress()

            if write_in['status'] == 'failure':
                write_in['error_info'] = task.get_error_info()


            self.op.set_operation(None, write_in)
        task.destroy()


    def try_xenadapter(self, func, post_hook=None):
        '''
        Call a xenadapter method, handle exceptions
        :param func:
        :param post_hook: call this function with a xenadapter method's return value and an authenticator object  as arguments argument (optional)        :return:
        '''
        auth = self.user_authenticator

        try:
            ret = func(auth)

        except XenAdapterUnauthorizedActionException as ee:
            self.set_status(403)
            self.write(json.dumps({'status': 'not allowed', 'details': ee.message}))
            self.finish()


        except EmperorException as ee:
            self.set_status(400)
            self.write(json.dumps({'status': 'error', 'details': ee.message}))
            self.finish()



        else:
            if ret:
                self.write(ret)
            else:
                self.write(json.dumps({'status': 'ok'}))

            self.finish()
            try:
                if post_hook:
                    post_hook(ret, auth)
            except EmperorException as e:
                self.log.error("try_xenadapter: exception catched in post_hook: %s" % e.message)


class BaseWSHandler(WebSocketHandler, HandlerMethods):
    def initialize(self, *args, **kwargs):
        self.init_executor(kwargs['pool_executor'])
        del kwargs['pool_executor']
        super().initialize()


        self.user_authenticator = Optional[BasicAuthenticator]
        self.op = Operations(r.db(opts.database))

    def check_origin(self, origin):
        return True
