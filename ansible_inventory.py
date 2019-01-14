#!/usr/bin/env python3
from ruamel.yaml import YAML
import argparse

yaml = YAML(typ='safe')
if __name__ == '__main__':
    p = argparse.ArgumentParser(description="VMEmperor Ansible inventory generator")
    p.add_argument('--list', action='store_true')
    p.add_argument('--host')

    args = p.parse_args()
    if args.list:
        print('generate host list')

    if args.host:
        print('print host info: ', args.host)

with open('ansible/wordpress-nginx/group_vars/all') as file:
    print(yaml.load(file))

with open('ansible/wordpress-nginx/vmemperor.conf') as file:
    print(yaml.load(file))