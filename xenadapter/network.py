from .xenobject import *
from . import use_logger

class VIF(XenObject, metaclass=XenObjectMeta):
    api_class = 'VIF'
    @classmethod
    def create(cls, auth, *args, **kwargs):
        attr = cls.__class__.__getattr__(cls, 'create')
        return VIF(auth, ref=attr(auth.xen, *args, **kwargs))




class Network(XenObject):
    from .vm import VM
    api_class = "network"
    def __init__(self, auth, uuid):
        super().__init__(auth, uuid)

    @use_logger
    def attach(self, vm: VM) -> VIF:
        self.check_access('attach')

        args = {'VM': vm.ref, 'network': self.ref , 'device': str(len(vm.get_VIFs())),
                'MAC': '', 'MTU': self.get_MTU() , 'other_config': {},
                'qos_algorithm_type': '', 'qos_algorithm_params': {}}
        try:

            vif = VIF.create(self.auth, args)
            #vif_uuid = self.auth.xen.api.VIF.get_uuid(vif_ref)

            self.log.info("VM is connected to network: VIF UUID {0}".format(vif.uuid))
        except XenAdapterAPIError as f:
            raise XenAdapterAPIError(self.auth.xen.log, "Failed to create VIF: {0}".format(f.details))

        return vif
