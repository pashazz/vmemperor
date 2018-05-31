import json
class EmperorException(Exception):
    def __init__(self, log, message):
        log.error("{0}: {1}".format(type(self).__name__, message))
        super().__init__()
        self.message = message
        self.log = log


class XenAdapterException(EmperorException):
    pass



class XenAdapterConnectionError(XenAdapterException):
    pass

class XenAdapterUnauthorizedActionException(XenAdapterException):
    pass

class XenAdapterAPIError(XenAdapterException):
    def __init__(self, log, message, details=None):
        super().__init__(log, message=json.dumps({'message' : message, 'details' : details }))


class XenAdapterArgumentError(XenAdapterException):
    pass


class AuthenticationException(EmperorException):
    pass

class AuthenticationRealmException(AuthenticationException):
    pass

class AuthenticationUserNotFoundException(AuthenticationException):
    def __init__(self, log, realm):
        super().__init__(log, "Realm {0} can't find user {1}".format(type(realm).__name__, realm.username))


class AuthenticationPasswordException(AuthenticationException):
    def __init__(self, log, realm):
        super().__init__(log, "Realm {0} can't find authenticate user {1}: incorrect password".format(type(realm).__name__, realm.get_id()))

class AuthenticationWithEmptyPasswordException(AuthenticationException):
    def __init__(self, log, realm):
        super().__init__(log,
                         "Realm {0} can't find authenticate user {1}: empty password".format(type(realm).__name__,
                                                                                                 realm.username))

class UnauthorizedException(AuthenticationException):
    pass