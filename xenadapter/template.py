from .abstractvm import AbstractVM
from exc import *
import XenAPI
from .vm import VM
from . import use_logger


class Template(AbstractVM):
    ALLOW_EMPTY_XENSTORE = True

    @classmethod
    def filter_record(cls, record):
        return record['is_a_template']

    @classmethod
    def process_record(self, auth, record):
        keys = ['hvm', 'name_label', 'uuid']
        new_rec = {k: v for k, v in record.items() if k in keys}
        if record['HVM_boot_policy'] == '':
            new_rec['hvm'] = False
        else:
            new_rec['hvm'] = True
        return new_rec

    @use_logger
    def clone(self, name_label):
        try:

            new_vm_ref = self.__getattr__('clone')(name_label)
            vm = VM(self.auth, ref=new_vm_ref)
            self.insert_log_entry('cloned', 'Cloned to %s' % vm.uuid)
            self.log.info("New VM is created: UUID {0}".format(vm.uuid))
            return vm
        except XenAPI.Failure as f:
            self.insert_log_entry('failed', f.details)
            raise XenAdapterAPIError(self.log, "Failed to clone template: {0}".format(f.details))

    @use_logger
    def enable_disable(self, enable):
        '''
        Adds/removes tag 'vmemperor'
        :param enable:
        :return:
        '''
        try:
            if enable:
                self.add_tags('vmemperor_enabled')
                self.log.info("Enabled template UUID {0}".format(self.uuid))
            else:
                self.remove_tags('vmemperor_enabled')
                self.log.info("Disabled template UUID {0}".format(self.uuid))
        except XenAPI.Failure as f:
            raise XenAdapterAPIError(self.log, "Failed to {0} template: {1}".format(
                'enable' if enable else 'disable', f.details))
