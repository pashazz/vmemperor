import json
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
        super().__init__(log, message=json.dumps({'message' : message, 'details' : details }))


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