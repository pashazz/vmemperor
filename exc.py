import json
from  rethinkdb import  RethinkDB
r = RethinkDB()
import tornado.options as opts
class EmperorException(Exception):
    def __init__(self, log, message):
        log.error("{0}: {1}".format(type(self).__name__, message))
        super().__init__()
        self.message = message
        self.log = log

    def __str__(self):
        return "<{0}>: {1}".format(self.__class__.__name__, self.message)


class XenAdapterException(EmperorException):
    pass



class XenAdapterConnectionError(XenAdapterException):
    pass

class XenAdapterUnauthorizedActionException(XenAdapterException):
    pass

class XenAdapterAPIError(XenAdapterException):
    def __init__(self, log, message, details=None):
        super().__init__(log, message=json.dumps({'message' : message, 'details' : self.print_details(details)}))

    @staticmethod
    def print_details(details):
        if details[0] == 'VDI_MISSING':
            db = r.db(opts.database)
            sr = db.table('srs').get_all(details[1], index='ref').pluck('uuid', 'content_type').coerce_to('array').run()[0]
            if sr['content_type'] == 'iso':
                table_name = 'isos'
            else:
                table_name = 'vdis'
            disk = db.table(table_name).get_all(details[2], index='ref').pluck('uuid').run()[0]

            return {
                "error_code" : details[0],
                "SR": sr['uuid'],
                "content_type": sr['content_type'],
                "VDI": disk['uuid'],
            }
        elif details[0] == 'UUID_INVALID':
            return {
                "error_code": details[0],
                "object_type": details[1],
                "uuid": details[2],
            }
        else:
            return details





class XenAdapterArgumentError(XenAdapterException):
    pass


class AuthenticationException(EmperorException):
    pass

class AuthenticationRealmException(AuthenticationException):
    pass

class AuthenticationUserNotFoundException(AuthenticationException):
    def __init__(self, log, realm):
        super().__init__(log, f"Realm {type(realm).__name__} can't find user {realm.username}")


class AuthenticationPasswordException(AuthenticationException):
    def __init__(self, log, realm):
        super().__init__(log,
                         f"Realm {type(realm).__name__} can't find authenticate user {realm.get_id()}: incorrect password")

class AuthenticationWithEmptyPasswordException(AuthenticationException):
    def __init__(self, log, realm):
        super().__init__(log,
                         f"Realm {type(realm).__name__} can't find authenticate user {realm.username}: empty password")

class UnauthorizedException(AuthenticationException):
    pass