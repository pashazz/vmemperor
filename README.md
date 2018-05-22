# VMEmperor

## Configuration

File: `login.ini`

### Example
    debug = True
    username = 'root' # Xen username
    password = 'password' # Xen password
    url = 'http://10.10.10.18:80/' # XenServer URL
    database = 'vmemperor' # RethinkDB DB name
    host = '10.10.10.102' # RethinkDB host name
    delay = 5000 # Delay before Xen events update, in ms
    max_workers = 16
    vmemperor_port = 8889 # My port, specify it in URL of VMEmperor CLI
    log_

## Logging


# CLI
    make_request.py <action> <options>

## Configuration
Specify `url` on line 16


## Available actions
* `createvm` - Create VM
* `vminfo` - Get VM info
* `installstatus` - Get install status
* `start` - Start VM
* `stop` - Stop VM
* `destroy` - Destroy VM
* `vnc` - Get VNC url (use HTTP CONNECT method with this URL)
## Get help
    make_request.py <action> --help


## Example

### Create a VM named `vm1` with hostname `xenvm`

    ./make_request.py createvm --name_label "vm1" --hostname "xenvm"

## Output format
Line 1: API output<br>
Line 2: HTTP status code

### Example
    ./make_request.py createvm --name_label "test13" --hostname "test13"
    904754ee-db21-0fd6-0a23-dfdaa34fdcc9
    200


## Default options
### `createvm`

        "--template", help='Template UUID or name_label', default="Ubuntu Precise Pangolin 12.04 (64-bit)"
        "--mode", help="VM mode: pv or hvm", default="pv", choices=['pv','hvm']
        "--storage", help="Storage repository UUID",  default="88458f94-2e69-6332-423a-00eba8f2008c"
        "--network", help="Network UUID", default="920b8d47-9945-63d8-4b04-ad06c65d950a"
        "--vdi_size", help="Disk size in megabytes", default="20480"
        "--ram_size", help="RAM size in megabytes", default="2048"
        "--name_label", help="Human-readable VM name", required=True
        "--hostname", help="Host name", required=True
        "--ip", help="Static IP address"
        "--netmask", help="Netmask"
        "--gateway", help="Gateway"
        "--dns0", help="DNS Server IP"
        "--dns1", help="Second DNS Server IP"
        "--os_kind", help="OS Type", default="ubuntu xenial"
        "--fullname", help="User's full name", default="John Smith"
        "--username", help="UNIX username", default='john'
        "--password", help="UNIX password", default='john'
        "--mirror_url", help="Repository URL (for network installation)", default="http://mirror.corbina.net/ubuntu"
        "--partition", help="Disk partition map", default="/-15359--/home-4097-"