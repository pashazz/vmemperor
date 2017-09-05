class EmperorException(Exception):
    def __init__(self, exc_obj, message):
        exc_obj.log.error("{0}: {1}".format(type(self).__name__, message))
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
    def __init__(self, exc_obj):
        super().__init__(exc_obj, "Realm {0} can't find user {1}".format(type(exc_obj).__name__, exc_obj.username))


class AuthenticationPasswordException(AuthenticationException):
    def __init__(self, exc_obj):
        super().__init__(exc_obj, "Realm {0} can't find authenticate user {1}: incorrect password".format(type(exc_obj).__name__, exc_obj.username))

class AuthenticationWithEmptyPasswordException(AuthenticationException):
    def __init__(self, exc_obj):
        super().__init__(exc_obj,
                         "Realm {0} can't find authenticate user {1}: empty password".format(type(exc_obj).__name__,
                                                                                                 exc_obj.username))

class UnauthorizedException(AuthenticationException):
    pass