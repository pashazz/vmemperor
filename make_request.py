#!/usr/bin/env python3
import requests
import argparse
import sys
import json
import pprint

def login(method):
    def decorator(self, *args, **kwargs):
        if not self.jar:
            self._login()
        method(self, *args, **kwargs)

    return decorator

class Main():

    url = 'http://localhost:8889'

    def __init__(self):
        self.jar = None
        p = argparse.ArgumentParser(description="VMEmperor CLI Utility", usage="%s <API call> <args>" % sys.argv[0])
        p.add_argument("api_call", help="API call to request")
        args = p.parse_args(sys.argv[1:2])
        if not hasattr(self, args.api_call) or args.api_call[0] == '_':
            print("Unknown API call: %s" % args.api_call)
            return

        getattr(self, args.api_call)()


    def _login(self):
        r = requests.post("%s/login" % self.url)
        self.jar = r.cookies

    @login
    def createvm(self):
        p = argparse.ArgumentParser(description="Create a VM, return its UUID")
        p.add_argument("--template", help='Template UUID or name_label', default="Ubuntu Precise Pangolin 12.04 (64-bit)")
        p.add_argument("--mode", help="VM mode: pv or hvm", default="pv", choices=['pv','hvm'])
        p.add_argument("--storage", help="Storage repository UUID",  default="88458f94-2e69-6332-423a-00eba8f2008c")
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
        p.add_argument("--mirror_url", help="Repository URL (for network installation)", default="http://mirror.corbina.net/ubuntu")
        p.add_argument("--partition", help="Disk partition map", default="/-15359--/home-4097-")
        args = p.parse_args(sys.argv[2:])
        r = requests.post("%s/createvm" % self.url, cookies=self.jar, data=dict(args._get_kwargs()))
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def installstatus(self):
        p = argparse.ArgumentParser(description="Check installation status of a VM")
        p.add_argument('uuid', help="VM UUID")
        args = p.parse_args(sys.argv[2:])
        r = requests.post("%s/installstatus" % self.url, cookies=self.jar, data=dict(uuid=args.uuid))
        print(r.text)
        print(r.status_code, file=sys.stderr)


    @login
    def vminfo(self):
        p = argparse.ArgumentParser(description="Get VM state information")
        p.add_argument('uuid', help="VM UUID")
        args = p.parse_args(sys.argv[2:])
        r = requests.post("%s/vminfo" % self.url, cookies=self.jar, data=dict(uuid=args.uuid))
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def start(self):
        p = argparse.ArgumentParser(description="Start VM")
        p.add_argument('uuid', help='VM UUID')
        args = p.parse_args(sys.argv[2:])
        r = requests.post("%s/startstopvm" % self.url, cookies=self.jar, data=dict(uuid=args.uuid, enable=True))
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def stop(self):
        p = argparse.ArgumentParser(description="Stop VM")
        p.add_argument('uuid', help='VM UUID')
        args = p.parse_args(sys.argv[2:])
        r = requests.post("%s/startstopvm" % self.url, cookies=self.jar, data=dict(uuid=args.uuid, enable=False))
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def destroy(self):
        p = argparse.ArgumentParser(description="Destroy VM")
        p.add_argument('uuid', help='VM UUID')
        args = p.parse_args(sys.argv[2:])
        r = requests.post("%s/destroyvm" % self.url, cookies=self.jar, data=dict(uuid=args.uuid))
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def vnc(self):
        p = argparse.ArgumentParser(description="Get VNC URL (use HTTP CONNECT method)")
        p.add_argument('uuid', help='VM UUID')
        args = p.parse_args(sys.argv[2:])
        r = requests.post("%s/vnc" % self.url, cookies=self.jar, data=dict(uuid=args.uuid))
        print(r.text)
        print(r.status_code, file=sys.stderr)

    @login
    def vmlist(self):
        r = requests.get("%s/vmlist" % self.url, cookies=self.jar)
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)

    @login
    def isolist(self):
        r = requests.get("%s/isolist" % self.url, cookies=self.jar)
        js = json.loads(r.text)
        pprint.pprint(js)
        print(r.status_code, file=sys.stderr)

if __name__ == '__main__':
    Main()