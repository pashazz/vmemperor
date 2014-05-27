import XenAPI
import pprint
import getpass
from getvminfo import get_vms_list


def main(session):
    api = session.xenapi
    pp = pprint.PrettyPrinter()
    pool_master = ""
    for pool in api.pool.get_all():
        pool_master = api.pool.get_master(pool)

        for host in api.host.get_all():
            host_name_label = api.host.get_name_label(host)
            free_mem = int(api.host.compute_free_memory(host))/(1024*1024)
            metrics = api.host.get_metrics(host)
            pp.pprint("Free memory on host " + host_name_label + ": " + str(free_mem) + " MB")
            #resident_vms_list = api.host.get_resident_VMs(host)

            #pp.pprint(api.host_metrics.get_memory_actual(metrics))

    vm_list = get_vms_list(session)
    pp.pprint(vm_list)



# VM_metrics.get_all()
# VM_metrics.get_start_time()
# VM_metrics.get_os_version()
# VM_metrics.get_install_time()
# VM_metrics.get_memory_actual()
# VM_metrics.get_VCPU/utilisation() #map int->float
# VM_metrics.get_state()


if __name__ == '__main__':
    url = 'https://localhost:1443/'
    username = 'root'
    password = getpass.getpass()
    # First acquire a valid session by logging in:
    session = XenAPI.Session(url)
    session.xenapi.login_with_password(username, password)

    main(session)