class EmperorException(Exception):
    def __init__(self, log, message):
        log.error("{0}: {1}".format(type(self).__name__, message))
        super().__init__()
        self.message = message


class XenAdapterException(EmperorException):
    pass


class XenAdapterConnectionError(XenAdapterException):
    pass


class XenAdapterAPIError(XenAdapterException):
    pass


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
        super().__init__(log, "Realm {0} can't find authenticate user {1}: incorrect password".format(type(realm).__name__, realm.username))

class AuthenticationWithEmptyPasswordException(AuthenticationException):
    def __init__(self, log, realm):
        super().__init__(log,
                         "Realm {0} can't find authenticate user {1}: empty password".format(type(realm).__name__,
                                                                                                 realm.username))

class UnauthorizedException(AuthenticationException):
    pass