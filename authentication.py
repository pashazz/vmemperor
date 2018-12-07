from abc import ABCMeta, abstractmethod

import logging

class Authentication(metaclass=ABCMeta):


    @abstractmethod
    def check_credentials(self, password, username, log=logging):
        """
        asserts credentials using inner db, or some outer authentication system
        You should set username to self.username
        You should set password to self.password
        :param log: logging-like vmemperor logger
        :return None
        :raise AuthenticationUserNotFoundException if user is not found
        :raise AuthenticationPasswordException if password is wrong
        :raise AuthenticationWithEmptyPasswordException if password is empty
        All exceptions are in exc.py
        """
        return

    @abstractmethod
    def get_user_groups(self):
        """
        Return a dict of user's groups with id as key and name as value"
        """
        return

    @classmethod
    @abstractmethod
    def get_all_users(cls, log=logging):
        '''
        Return a list of all users available in format of a list of dicts with the following fields:
        {
        "id": Unique id for an user
        "username": Unique username that the user uses for login and this username is checked in check_credentials
        "name": User's full name
        }

        This may be an resource-intensive method that is being called each N seconds and its results are uploaded to a cache database
        :param log:
        :return: list

        '''
        return

    @classmethod
    @abstractmethod
    def get_all_groups(cls, log=logging):
        '''
        Return a list of all groups available in format of a list of dicts with the following fields:
        {
        "id": Unique id for a group
        "username": Unique username that the group user uses for login and this username is checked in check_credentials if your realm supports login into a group OR you can use the same value as ID
        "name": Group's full name
        }

        This may be an resource-intensive method that is being called each N seconds and its results are uploaded to a cache database
        :param log:
        :return: list

        '''
        return









@Authentication.register
class BasicAuthenticator:
    @classmethod
    def class_name(cls):
        return cls.__name__

    def get_user_groups(self):
        return {}



class AdministratorAuthenticator(BasicAuthenticator):
    # TODO Implement check_credentials

    def __init__(self, user_auth: type):
        self.auth = False
        self.user_auth = user_auth


    def check_credentials(self, password, username, log=logging):
        from exc import AuthenticationPasswordException, XenAdapterConnectionError
        from xenadapter import XenAdapter
        from vmemperor import opts
        params = {**opts.group_dict('xenadapter'), **opts.group_dict('rethinkdb')}
        params['username'] = username
        params['password'] = password
        self.id = username
        try:

            xen = XenAdapter(params, nosingleton=True)
        except XenAdapterConnectionError as e:
            raise AuthenticationPasswordException(e.log, self)



    def get_id(self):
        return self.id

    def get_name(self):
        return self.id

    def class_name(self):
        return self.user_auth.__name__






class DebugAuthenticator(AdministratorAuthenticator): #used by tests
    def check_credentials(self, password, username):
        pass #not rly used

    def __init__(self, user_auth):

        from xenadapter import XenAdapter
        from vmemperor import opts
        self.xen = XenAdapter({**opts.group_dict('xenadapter'), **opts.group_dict('rethinkdb')})

        super().__init__(user_auth)

class DummyAuth(BasicAuthenticator):

    def check_credentials(self, password, username):
        pass

    def __init__(self, id='', name=''):
        self.id = id
        self.name = name


    def get_id(self):
        return self.id

    def get_name(self):
        return self.name


class NotAuthenticatedException(Exception):
    def __init__(self):
        super().__init__("You are not authenticated")

class NotAuthenticatedAsAdminException(Exception):
    def __init__(self):
        super().__init__("You are not authenticated as administrator")

def with_authentication(method):
    def decorator(root, info, *args, **kwargs):
        if not hasattr(info.context, 'user_authenticator'):
            raise NotAuthenticatedException()

        return method(root, info, *args, **kwargs)
    return decorator

def with_admin_authentication(method):
    def decorator(root, info, *args, **kwargs):
        if not hasattr(info.context, 'user_authenticator'):
            raise NotAuthenticatedException()

        return method(root, info, *args, **kwargs)
    return decorator

