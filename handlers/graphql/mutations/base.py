from dataclasses import dataclass
from typing import NewType, Callable, Sequence, Any, Optional
import graphene
from authentication import AdministratorAuthenticator, NotAuthenticatedAsAdminException

from handlers.graphql.graphql_handler import ContextProtocol
from xenadapter.xenobject import XenObject


@dataclass
class MutationMethod:
    '''
    Represents a mutation method - a function equipped with action name that is passed to check_access.
    Here, action_name = None has a special meaning: if action_name is None, then it is checked whether the user is an administrator, thus this
    value is suitable for administrator actions
    '''
    #func : Callable[[ContextProtocol, XenObject, InputObject, OutputObject, ...], None]
    func : Callable
    action_name : Optional[str]



@dataclass
class MutationHelper():
    mutations : Sequence[MutationMethod]
    ctx : ContextProtocol
    mutable_object : XenObject

    def perform_mutations(self, changes):
        for item in self.mutations:
            if item.action_name is None:
                if self.ctx.user_authenticator.is_admin():
                    item.func(self.ctx, self.mutable_object, changes)
                else:
                    raise NotAuthenticatedAsAdminException()
            else:
                if self.mutable_object.check_access(item.action_name):
                    item.func(self.ctx, self.mutable_object, changes)






