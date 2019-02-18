from xenadapter.xenobject import XenObject

from rethinkdb import RethinkDB
r = RethinkDB()

class VBD(XenObject):
    api_class = 'VBD'
    EVENT_CLASSES = ['vbd']

    @classmethod
    def process_event(cls, auth, event, db, authenticator_name):
        from .vm import VM
        from rethinkdb_tools.helper import CHECK_ER
        from XenAPI import Failure


        if event['class'] in cls.EVENT_CLASSES:
            if event['operation'] == 'del':
                CHECK_ER(db.table(VM.db_table_name).replace(r.row.without({'disks': event['ref']})).run())
                return

            record = event['snapshot']

            if event['operation'] in ('mod', 'add'):
                vm = VM(auth=auth, ref=record['VM'])
                if vm.get_is_a_snapshot():
                    return # TODO Handle snapshots
                try:
                    new_rec = {'uuid': vm.uuid, 'disks': {event['ref'] :
                    {'VDI': record['VDI'], 'bootable': record['bootable'], 'attached': record['currently_attached'], 'type' : record['type'],
                     'mode': record['mode'], 'device': record['device'] }}}
                    CHECK_ER(db.table(VM.db_table_name).insert(new_rec, conflict='update').run())
                except Failure as f:
                    auth.log.error(f"Failed to process VBD event due to XenAPI Failure: {f.details}")



    def delete(self) -> bool:
        '''

        :return: False if unable to unplug device from running VM
        '''
        from .vm import VM
        vm = VM(auth=self.auth, ref=self.get_VM())

        if vm.get_power_state() == 'Running' and self.get_unpluggable():
            self.unplug()
        else:
            return False

        self.destroy()
        return True
