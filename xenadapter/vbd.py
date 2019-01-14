from xenadapter.xenobject import XenObject
import rethinkdb as r


class VBD(XenObject):
    api_class = 'VBD'
    EVENT_CLASSES = ['vbd']

    @classmethod
    def process_event(cls, auth, event, db, authenticator_name):
        from .vm import VM
        from .disk import ISO, VDI
        from rethinkdb_helper import CHECK_ER
        from XenAPI import Failure
        cls.create_db(db)


        if event['class'] in cls.EVENT_CLASSES:
            if event['operation'] == 'del':
                CHECK_ER(db.table(VM.db_table_name).replace(r.row.without({'disks': event['ref']})).run())
                return

            record = event['snapshot']

            if event['operation'] in ('mod', 'add'):
                vm = VM(auth=auth, ref=record['VM'])
                if record['empty']:
                    vdi = None
                elif record['type'] == 'CD':
                    vdi = ISO(auth=auth, ref=record['VDI']).uuid
                else:
                    vdi = VDI(auth=auth, ref=record['VDI']).uuid
                try:
                    new_rec = {'uuid': vm.uuid, 'disks': {event['ref'] :
                    {'VDI': vdi, 'bootable': record['bootable'], 'attached': record['currently_attached'], 'type' : record['type'],
                     'mode': record['mode'], 'device': record['device'] }}}
                    CHECK_ER(db.table(vm.db_table_name).insert(new_rec, conflict='update').run())
                except Failure as f:
                    auth.log.error("Failed to process VBD event due to XenAPI Failure: {0}".format(f.details))


