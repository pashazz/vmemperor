import threading
from typing import Dict

from playbook import Playbook
from xenadapter.disk import VDI
from xenadapter.network import Network
from xenadapter.vm import VM

logger = None # global logger
POSTINST_ROUTE = r'/postinst'


#These objects are thouse who have ACL enabled
objects = [VM, Network, VDI]

user_table_ready = threading.Event()
first_batch_of_events = threading.Event()
need_exit = threading.Event()
xen_events_run = threading.Event()  # called by USR2 signal handler
URL = ""
ansible_pubkey = ""
auth_class_name = ""
playbooks = Dict[str, Playbook]
secrets = {}