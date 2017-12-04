from abc import ABCMeta, abstractmethod



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
    def init(self, xen):
        self.xen = xen

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