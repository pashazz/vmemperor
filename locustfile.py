from locust import HttpLocust, TaskSet

import time
import gevent
import json

import six

from locust import HttpLocust, TaskSet, task
from locust.events import request_success
import requests
from configparser import ConfigParser
import asyncio
import websocket
import sys
sys.path.append('/home/pasha/.local/share/JetBrains/Toolbox/apps/PyCharm-P/ch-0/173.4301.16/debug-eggs/pycharm-debug-py3k.egg')
import pydevd
pydevd.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)
#import pdb
#pdb.set_trace()


def login(host, port, username, password):
    '''
    Login into the system
    :param username:
    :param password:
    :return:  dict with ['Cookie'] set

    '''


    r = requests.post("%s/login" % 'http://{0}:{1}'.format(host,port), data=dict(username=username, password=password))

    headers = {}
    #pydevd.settrace()
    headers['Cookie'] = r.headers['Set-Cookie']

    #print("hello debugger")
    return headers




class VmListTaskSet(TaskSet):
    def on_start(self):
        # load host/port from file
        host = 'localhost'
        with open('login.ini') as file:
            for line in file:
                keys = [string.strip() for string in line.split('=')]
                if keys[0] == 'vmemperor_port':
                    port = keys[1]
                    break
            else:
                raise AttributeError("Port not found in config file")

        parser = ConfigParser()
        with open('make_request.ini') as file:
            parser.read_file(file)
            username = parser.get('login', 'username')
            password = parser.get('login', 'password')


        self.headers = login(host, port, username, password)


        ws = websocket.create_connection('ws://{0}:{1}/vmlist'.format(host,port), header=self.headers)
        self.ws = ws


    @task
    def receive(self):
        while True:
            start_at = time.time()
            res = self.ws.recv()
            data = json.loads(res)
            print(data)
            end_at = time.time()
            response_time = int((end_at - start_at) * 1000000)
            request_success.fire(
                request_type='WebSocket Recv',
                name='test/ws/echo',
                response_time=response_time,
                response_length=len(res),

            )




    def on_quit(self):
       self.ws.close()

class VmListLocust(HttpLocust):
    task_set = VmListTaskSet
    host = 'http://localhost:8889'
    min_wait = 0
    max_wait = 1000
