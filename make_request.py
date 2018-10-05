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
        p.add_argument('--login', help='login as user (see sections in make_request.ini). If admin=True, we will try Administrator login')
        p.add_argument('--host', help='VMEmperor host', default=config._sections['config']['host'])
        p.add_argument('-p','--port', help='VMEmperor port', default=int(config._sections['config']['port']), type=int)
        p.set_defaults(login='login')

        self.subparsers = p.add_subparsers()
        self.parser = p

        #add parser for createvm
        p = self.subparsers.add_parser('createvm', description="Create a VM, return its UUID",
                                       usage="createvm <options>")
        p.add_argument("--template", help='Template UUID or name_label',
                       default="Debian Wheezy 7.0 (64-bit)")
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
        p.add_argument("--mirror_url", help="Repository URL (for network installation)")
        p.add_argument("--partition", help="Disk partition map", default="/-15359--/home-4097-")
        p.set_defaults(func=self.createvm)

        #add parser for setaccess
        p = self.subparsers.add_parser('setaccess', description="Set/revoke access rights")
        p.add_argument('uuid', help='object UUID')
        p.add_argument('--type', help='object type', required=True)
        p.add_argument('--action', help='action to set', required=True)
        p.add_argument('--revoke', help='Do we need to revoke it?', action='store_true')
        p.add_argument('--user')
        p.add_argument('--group')
        p.set_defaults(func=self.setaccess)

        #add parser for getaccess
        p = self.subparsers.add_parser('getaccess', description="Query access information")
        p.add_argument('uuid', help='Object UUID')
        p.add_argument('--type', help='object type', required=True)
        p.set_defaults(func=self.getaccess)

        #add parser for destroy
        p = self.subparsers.add_parser('destroy', description="Destroy VM")
        p.add_argument('uuid', help='VM UUID')
        p.set_defaults(func=self.destroy)

        #add parser for vnc
        p = self.subparsers.add_parser('vnc', description="Get VNC url (for WebSocket)")
        p.add_argument('uuid', help='VM UUID')
        p.set_defaults(func=self.vnc)

        #add parser for console
        p = self.subparsers.add_parser('console', description="Read data from WebSocket console")
        p.add_argument('url', help='VNC URL')
        p.set_defaults(func=self.console)

        #add parser for installstatus
        p = self.subparsers.add_parser('installstatus', description="Check VM install status")
        p.add_argument('taskid', help='Installation Task ID')
        p.set_defaults(func=self.installstatus)

        #add parser for vminfo
        p = self.subparsers.add_parser('vminfo', description="Print VM info")
        p.add_argument('uuid', help='VM UUID')
        p.set_defaults(func=self.vminfo)

        # add parser for vmdiskinfo
        p = self.subparsers.add_parser('vmdiskinfo', description="Print VM disks full info")
        p.add_argument('uuid', help='VM UUID')
        p.set_defaults(func=self.vmdiskinfo)

        # add parser for vmnetinfo
        p = self.subparsers.add_parser('vmnetinfo', description="Print VM networks full info")
        p.add_argument('uuid', help='VM UUID')
        p.set_defaults(func=self.vmnetinfo)

        #add parser for start
        p = self.subparsers.add_parser('start', description="Start VM")
        p.add_argument('uuid', help='VM UUID')
        p.set_defaults(func=self.start)

        #add parser for stop
        p = self.subparsers.add_parser('stop', description="Stop VM")
        p.add_argument('uuid', help='VM UUID')
        p.set_defaults(func=self.stop)

        #add parser for netinfo
        p = self.subparsers.add_parser('netinfo', description="Print Network info")
        p.add_argument('uuid', help='Network UUID')
        p.set_defaults(func=self.netinfo)

        # add parser for vdiinfo
        p = self.subparsers.add_parser('vdiinfo', description="Print VDI info")
        p.add_argument('uuid', help='VDI UUID')
        p.set_defaults(func=self.vdiinfo)

        # add parser for isoinfo
        p = self.subparsers.add_parser('isoinfo', description="Print ISO info")
        p.add_argument('uuid', help='ISO UUID')
        p.set_defaults(func=self.isoinfo)

        #add parser for turntemplate
        p = self.subparsers.add_parser('turntemplate', description="Enable/disable template in vmemperor (Administrator only)")
        p.add_argument('action', choices=['on', 'off'])
        p.add_argument('uuid', help='Template UUID')
        p.set_defaults(func=self.turntemplate)

        #add parser for convertvm
        p = self.subparsers.add_parser('convertvm', description="Convert VM type (PV/HVM)")
        p.add_argument('uuid', help='VM UUID')
        p.add_argument('mode', choices=['pv', 'hvm'])
        p.set_defaults(func=self.convertvm)

        #add parser for reboot
        p = self.subparsers.add_parser('reboot', description="Reboot VM (clean if possible)")
        p.add_argument('uuid', help='VM UUID')
        p.set_defaults(func=self.reboot)

        # add parser for vdilist
        p = self.subparsers.add_parser('vdilist', description="VDI list")
        p.add_argument('--page', help="page number, 0 to disable pagination", default=0)
        p.add_argument('--pageSize', help="page size, default 10", default=10)
        p.set_defaults(func=self.vdilist)

        #add parser for attachdetachvdi
        p = self.subparsers.add_parser('attachdetachvdi', description="attach/detach VDI")
        p.add_argument('--uuid', help="VM UUID", required=True)
        p.add_argument('--vdi', help="VDI UUID", required=True)
        p.add_argument('--action', choices=['attach', 'detach'], required=True)
        p.set_defaults(func=self.attachdetachvdi)

        # add parser for networkaction
        p = self.subparsers.add_parser('netaction', description="attach/detach network (more actions in future)")
        p.add_argument('--uuid', help="VM UUID", required=True)
        p.add_argument('--net', help="Network UUID", required=True)
        p.add_argument('--action', choices=['attach', 'detach'], required=True)
        p.set_defaults(func=self.networkaction)

        p = self.subparsers.add_parser('taskstatus', description="Check async task status")
        p.add_argument('task', help="Task ID")
        p.set_defaults(func=self.taskstatus)

        #add parser for execute playbook
        p = self.subparsers.add_parser('execplaybook', description="Execute a playbook")
        p.add_argument('playbook', help="Playbook ID")
        p.add_argument('vms', help="VM UUIDs", nargs='+')
        p.set_defaults(func=self.execute_playbook)

        #add parser for alltemplates
        p = self.subparsers.add_parser('alltemplates', description="List all templates. including disabled")
        p.set_defaults(func=self.alltemplates)


        #add parser for everything else
        for method in inspect.getmembers(self, predicate=inspect.ismethod):
            if method[0].startswith('_') or method[0] in self.subparsers.choices:
                continue

            p = self.subparsers.add_parser(method[0])
            p.set_defaults(func=method[1])

        args, unknown = self.parser.parse_known_args(sys.argv[1:])
        self.url = f'http://{args.host}:{args.port}'
        self.ws_url = self.url.replace('http://', 'ws://')

        if 'func' not in dir(args):
            print('Wrong API call, choose from {0}'.format(tuple(self.subparsers.choices.keys())), file=sys.stderr)
            return
        self.login_opts = config._sections[args.login]

        args.func(args, unknown)




    def _login(self):
        if 'admin' in self.login_opts and self.login_opts['admin'].lower() == 'true':
            url = f'{self.url}/adminauth'
        else:
            url = f'{self.url}/login'

        r = requests.post(url, data=self.login_opts)
        self.jar = r.cookies
        self.headers={}
        self.headers['Cookie'] = r.headers['Set-Cookie']
        if r.text: print(r.text)

    @login
    def createvm(self, args, unknown):
        r = requests.post("%s/createvm" % self.url, cookies=self.jar, data=dict(args._get_kwargs()))
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def setaccess(self, args, unknown):
        print("Send data: ", dict(args._get_kwargs()))
        r = requests.post("%s/setaccess" % self.url, cookies=self.jar, data=dict(args._get_kwargs()))
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def getaccess(self, args, unknown):
        print("Send data: ", dict(args._get_kwargs()))
        r = requests.post("%s/getaccess" % self.url, cookies=self.jar, data=dict(args._get_kwargs()))
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def installstatus(self, args, unknown):
        r = requests.post("%s/createvm" % self.url, cookies=self.jar, data=dict(taskid=args.taskid))
        print(r.text)
        print(r.status_code, file=sys.stderr)


    @login
    def vminfo(self, args, unknown):
        r = requests.post("%s/vminfo" % self.url, cookies=self.jar, data=dict(uuid=args.uuid))

        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)

    @login
    def turntemplate(self, args, unknown):
        r = requests.post("%s/turntemplate" % self.url, cookies=self.jar, data=dict(uuid=args.uuid, action=args.action))
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)

    @login
    def convertvm(self, args, unknown):
        r = requests.post("%s/convertvm" % self.url, cookies=self.jar,
        data=dict(uuid=args.uuid, mode=args.mode))
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)

    @login
    def reboot(self, args, unknown):
        r = requests.post("%s/rebootvm" % self.url, cookies=self.jar,
        data=dict(uuid=args.uuid))
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)

    @login
    def netinfo(self, args, unknown):
        r = requests.post("%s/netinfo" % self.url, cookies=self.jar, data=dict(uuid=args.uuid))
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)


    @login
    def vdiinfo(self, args, unknown):
        r = requests.post("%s/vdiinfo" % self.url, cookies=self.jar, data=dict(uuid=args.uuid))
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)

    @login
    def attachdetachvdi(self, args, unknown):
        r = requests.post("%s/attachdetachvdi" % self.url, cookies=self.jar, data=dict(uuid=args.uuid, vdi=args.vdi, action=args.action))
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)

    @login
    def networkaction(self, args, unknown):
        r = requests.post("%s/netaction" % self.url, cookies=self.jar, data=dict(uuid=args.uuid, net=args.net, action=args.action))
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)

    @login
    def isoinfo(self, args, unknown):
        r = requests.post("%s/isoinfo" % self.url, cookies=self.jar, data=dict(uuid=args.uuid))
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)

    @login
    def vmdiskinfo(self, args, unknown):
        r = requests.post("%s/vmdiskinfo" % self.url, cookies=self.jar, data=dict(uuid=args.uuid))
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)

    @login
    def vmnetinfo(self, args, unknown):
        r = requests.post("%s/vmnetinfo" % self.url, cookies=self.jar, data=dict(uuid=args.uuid))
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)

    @login
    def start(self, args, unknown):
        r = requests.post("%s/startstopvm" % self.url, cookies=self.jar, data=dict(uuid=args.uuid, enable=True))
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def stop(self, args, unknown):
        r = requests.post("%s/startstopvm" % self.url, cookies=self.jar, data=dict(uuid=args.uuid, enable=False))
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def destroy(self, args, unknown):
        r = requests.post(f"{self.url}/destroyvm", cookies=self.jar, data=dict(uuid=args.uuid))
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def execute_playbook(self, args, unknown):
        d = {'vms': args.vms, 'playbook': args.playbook}
        for arg in unknown:
            name, value=arg.split('=')
            name = name[1:].strip()
            value = value.strip().replace('"', '').replace("'", '')
            d[name] = value
        r = requests.post(f'{self.url}/executeplaybook', cookies=self.jar, json=d)
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def taskstatus(self, args, unknown):
        r = requests.post(f"{self.url}/taskstatus", cookies=self.jar,
                          data=dict(task=args.task))
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)

    @login
    def vnc(self, args, unknown):
        r = requests.post("%s/vnc" % self.url, cookies=self.jar, data=dict(uuid=args.uuid))
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def tmpllist(self, args, unknown):
        r = requests.get("%s/tmpllist" % self.url, cookies=self.jar)
        pprint.pprint(r.json())
        print(r.status_code, file=sys.stderr)




    @login
    def playbooks(self, args, unknown):
        r = requests.get("%s/playbooks" % self.url, cookies=self.jar)
        pprint.pprint(r.json())
        print(r.status_code, file=sys.stderr)

    @login
    def userinfo(self, args, unknown):
        r = requests.get(f"{self.url}/userinfo", cookies=self.jar)
        pprint.pprint(r.json())
        print(r.status_code, file=sys.stderr)

    @login
    def userlist(self, args, unknown):
        r = requests.get(f"{self.url}/userlist", cookies=self.jar)
        for name in r.json():
            print(name)
        print(r.status_code, file=sys.stderr)

    @login
    def grouplist(self, args, unknown):
        r = requests.get(f"{self.url}/grouplist", cookies=self.jar)
        for name in r.json():
            print(name)
        print(r.status_code, file=sys.stderr)

    async def _vmlist_async(self):
        async with websockets.connect(self.ws_url + "/vmlist", extra_headers=self.headers) as socket:
            while not ev.is_set():
                    msg = await socket.recv()
                    print(msg, end='\n\n')

    async def _playbook_async(self, args, unknown):
        async with websockets.connect(self.ws_url + "/playbookoutput?id=" + args.id, extra_headers=self.headers) as socket:
            while not ev.is_set():
                msg = await socket.recv()
                print(msg, end='\n\n')

    async def _console_async(self, args):
        async with websockets.connect(args.url) as socket:
            while not ev.is_set():
                msg = await socket.recv()
                print(msg, end='\n\n')

    @login
    def vmlist(self, args, unknown):
        self._async_call(self._vmlist_async)


    def console(self, args, unknown):
        self._async_call(self._console_async, args)

    @login
    def playbook_output(self, args, unknown):
        self._async_call(self._playbook_async, args)


    @login
    def networklist(self, args, unknown):
        r = requests.get("%s/netlist" % self.url, cookies=self.jar)
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)

    @login
    def poollist(self, args, unknown):
        r = requests.get("%s/poollist" % self.url, cookies=self.jar)
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)



    @login
    def isolist(self, args, unknown):
        r = requests.get("%s/isolist" % self.url, cookies=self.jar)
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)


    @login
    def vdilist(self, args, unknown):
        r = requests.get("%s/vdilist" % self.url, cookies=self.jar, data=dict(page=args.page, page_size=args.pageSize))
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)

    @login
    def alltemplates(self, args, unknown):
        r = requests.get(f"{self.url}/alltemplates", cookies=self.jar)
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)

if __name__ == '__main__':
    try:
        Main()
    except KeyboardInterrupt:
        print ("Keyboard Interrupt")