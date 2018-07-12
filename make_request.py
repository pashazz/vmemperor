#!/usr/bin/env python3
import requests
import argparse
import sys
import json
import pprint
import websockets
import asyncio
import urllib.parse
from configparser import ConfigParser
import inspect
ev = asyncio.Event()


def login(method):
    def decorator(self, *args, **kwargs):
        if not self.jar:
            self._login()
        method(self, *args, **kwargs)

    return decorator

class Main():



    def _async_call(self, method, *args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
            task = asyncio.ensure_future(method(*args, **kwargs))
            loop.run_until_complete(task)
        except KeyboardInterrupt as e:
            print("Caught keyboard interrupt. Canceling tasks...")
            task.cancel()
            loop.run_forever()
        finally:
            loop.close()


    def __init__(self):

        self.jar = None
        config = ConfigParser()
        self.login_opts = {}
        with open("make_request.ini") as f:
            config.read_file(f)


        p = argparse.ArgumentParser(description="VMEmperor CLI Utility")
        p.add_argument('--login', help='login as user (see sections in make_request.ini)')
        p.add_argument('--host', help='VMEmperor host', default='localhost')
        p.add_argument('-p','--port', help='VMEmperor port', default=8889, type=int)
        p.set_defaults(login='login')

        self.subparsers = p.add_subparsers()
        self.parser = p

        #add parser for createvm
        p = self.subparsers.add_parser('createvm', description="Create a VM, return its UUID",
                                       usage="createvm <options>")
        p.add_argument("--template", help='Template UUID or name_label',
                       default="Ubuntu Precise Pangolin 12.04 (64-bit)")
        p.add_argument("--mode", help="VM mode: pv or hvm", default="pv", choices=['pv', 'hvm'])
        p.add_argument("--storage", help="Storage repository UUID", default="88458f94-2e69-6332-423a-00eba8f2008c")
        p.add_argument("--network", help="Network UUID", default="920b8d47-9945-63d8-4b04-ad06c65d950a")
        p.add_argument("--vdi_size", help="Disk size in megabytes", default="20480")
        p.add_argument("--ram_size", help="RAM size in megabytes", default="2048")
        p.add_argument("--name_label", help="Human-readable VM name", required=True)
        p.add_argument("--hostname", help="Host name", required=True)
        p.add_argument("--ip", help="Static IP address")
        p.add_argument("--netmask", help="Netmask")
        p.add_argument("--gateway", help="Gateway")
        p.add_argument("--dns0", help="DNS Server IP")
        p.add_argument("--dns1", help="Second DNS Server IP")
        p.add_argument("--os_kind", help="OS Type", default="ubuntu xenial")
        p.add_argument("--fullname", help="User's full name", default="John Smith")
        p.add_argument("--username", help="UNIX username", default='john')
        p.add_argument("--password", help="UNIX password", default='john')
        p.add_argument("--mirror_url", help="Repository URL (for network installation)",
                       default="http://mirror.corbina.net/ubuntu")
        p.add_argument("--partition", help="Disk partition map", default="/-15359--/home-4097-")
        p.set_defaults(func=self.createvm)

        #add parser for setaccess
        p = self.subparsers.add_parser('setaccess', description="Set/revoke access rights")
        p.add_argument('uuid', help='object UUID')
        p.add_argument('--type', help='object type')
        p.add_argument('--action', help='action to set')
        p.add_argument('--revoke', help='Do we need to revoke it?', action='store_true')
        p.add_argument('--user')
        p.add_argument('--group')
        p.set_defaults(func=self.setaccess)

        #add parser for destroy
        p = self.subparsers.add_parser('destroy', description="Destroy VM")
        p.add_argument('uuid', help='VM UUID')
        p.set_defaults(func=self.destroy)

        #add parser for vnc
        p = self.subparsers.add_parser('vnc', description="Get VNC url (CONNECT method)")
        p.add_argument('uuid', help='VM UUID')
        p.set_defaults(func=self.vnc)

        #add parser for console
        p = self.subparsers.add_parser('console', description="Read data from WebSocket console")
        p.add_argument('url', help='VNC URL')
        p.set_defaults(func=self.console)

        #add parser for installstatus
        p = self.subparsers.add_parser('installstatus', description="Check VM install status")
        p.add_argument('uuid', help='VM UUID')
        p.set_defaults(func=self.installstatus)

        #add parser for vminfo
        p = self.subparsers.add_parser('vminfo', description="Print VM info")
        p.add_argument('uuid', help='VM UUID')
        p.set_defaults(func=self.vminfo)

        #add parser for start
        p = self.subparsers.add_parser('start', description="Start VM")
        p.add_argument('uuid', help='VM UUID')
        p.set_defaults(func=self.vminfo)

        #add parser for stop
        p = self.subparsers.add_parser('start', description="Start VM")
        p.add_argument('uuid', help='VM UUID')
        p.set_defaults(func=self.vminfo)



        #add parser for everything else
        for method in inspect.getmembers(self, predicate=inspect.ismethod):
            if method[0].startswith('_') or method[0] in self.subparsers.choices:
                continue

            p = self.subparsers.add_parser(method[0])
            p.set_defaults(func=method[1])

        args = self.parser.parse_args(sys.argv[1:])
        self.url = 'http://{0}:{1}'.format(args.host, args.port)
        self.ws_url = self.url.replace('http://', 'ws://')

        if 'func' not in dir(args):
            print('Wrong API call, choose from {0}'.format(tuple(self.subparsers.choices.keys())), file=sys.stderr)
            return
        self.login_opts = config._sections[args.login]

        args.func(args)




    def _login(self):
        r = requests.post("%s/login" % self.url, data=self.login_opts)
        self.jar = r.cookies
        self.headers={}
        self.headers['Cookie'] = r.headers['Set-Cookie']
        if r.text: print(r.text)

    @login
    def createvm(self, args):
        r = requests.post("%s/createvm" % self.url, cookies=self.jar, data=dict(args._get_kwargs()))
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def setaccess(self, args):
        print("Send data: ", dict(args._get_kwargs()))
        r = requests.post("%s/setaccess" % self.url, cookies=self.jar, data=dict(args._get_kwargs()))
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def getaccess(self, args):
        print("Send data: ", dict(args._get_kwargs()))
        r = requests.post("%s/getaccess" % self.url, cookies=self.jar, data=dict(args._get_kwargs()))
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def installstatus(self, args):
        r = requests.post("%s/installstatus" % self.url, cookies=self.jar, data=dict(uuid=args.uuid))
        print(r.text)
        print(r.status_code, file=sys.stderr)


    @login
    def vminfo(self, args):
        r = requests.post("%s/vminfo" % self.url, cookies=self.jar, data=dict(uuid=args.uuid))

        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)

    @login
    def start(self, args):
        r = requests.post("%s/startstopvm" % self.url, cookies=self.jar, data=dict(uuid=args.uuid, enable=True))
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def stop(self, args):
        r = requests.post("%s/startstopvm" % self.url, cookies=self.jar, data=dict(uuid=args.uuid, enable=False))
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def destroy(self, args):
        r = requests.post("%s/destroyvm" % self.url, cookies=self.jar, data=dict(uuid=args.uuid))
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def vnc(self, args):
        r = requests.post("%s/vnc" % self.url, cookies=self.jar, data=dict(uuid=args.uuid))
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def tmpllist(self, args):
        r = requests.get("%s/tmpllist" % self.url, cookies=self.jar)
        pprint.pprint(r.json())
        print(r.status_code, file=sys.stderr)

    async def _vmlist_async(self):
        async with websockets.connect(self.ws_url + "/vmlist", extra_headers=self.headers) as socket:
            while not ev.is_set():
                    msg = await socket.recv()
                    print(msg, end='\n\n')

    async def _console_async(self, args):
        async with websockets.connect(args.url, extra_headers=self.headers) as socket:
            while not ev.is_set():
                msg = await socket.recv()
                print(msg, end='\n\n')

    @login
    def vmlist(self, args):
        self._async_call(self._vmlist_async)

    @login
    def console(self, args):
        self._async_call(self._console_async, args)


    @login
    def networklist(self, args):
        r = requests.get("%s/netlist" % self.url, cookies=self.jar)
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)

    @login
    def poollist(self, args):
        r = requests.get("%s/poollist" % self.url, cookies=self.jar)
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)



    @login
    def isolist(self, args):
        r = requests.get("%s/isolist" % self.url, cookies=self.jar)
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)

if __name__ == '__main__':
    try:
        Main()
    except KeyboardInterrupt:
        print ("Keyboard Interrupt")