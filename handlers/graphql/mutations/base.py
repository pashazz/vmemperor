from typing import NewType, Callable, Sequence, Any
import graphene


from handlers.graphql.graphql_handler import ContextProtocol
from xenadapter.xenobject import XenObject


@dataclass
class MutationMethod():
    func : Callable[[ContextProtocol, XenObject,   ...], None] = None
    action_name : str = None,



@dataclass
class MutationHelper():
    mutations : Sequence[MutationMethod] = []
    ctx : ContextProtocol = None
    mutable_object : XenObject = None

    def perform_mutations(self):
        for item in self.mutations:
            print(item)





