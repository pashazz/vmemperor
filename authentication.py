from abc import ABCMeta, abstractmethod

import logging

class Authentication(metaclass=ABCMeta):


    @abstractmethod
    def check_credentials(self, password, username):
        """asserts credentials using inner db, or some outer authentication system"""
        return

    @abstractmethod
    def get_user_groups(self):
        """gets list of user groups"""
        return

    @abstractmethod
    def set_user_group(self, group):
        """adds user to group"""
        return

    @abstractmethod
    def set_user(self, username):
        """creates cookie given username"""
        return






@Authentication.register
class BasicAuthenticator:
    @classmethod
    def class_name(cls):
        return cls.__name__



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