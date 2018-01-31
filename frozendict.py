import collections
import types

class frozendict(collections.UserDict):
    '''
    Implements a hashable dictionary, converting all lists and
    '''
    def __init__(self, d, **kw):
        def list_to_frozenset(x):
            if issubclass(type(x), list) or issubclass(type(x), set):
                return frozenset((list_to_frozenset(i) for i in x))
            else:
                return x

        if d:
            d = d.copy()
            d.update(kw)
        else:
            d = kw

        self.data = types.MappingProxyType({k: list_to_frozenset(v) for k,v in d.items()})

    _h = None
    def __hash__(self):
        if self._h is None:
            self._h = sum(map(hash, self.data.items()))
        return self._h

    def __repr__(self):
        return "frozendict(%s)" % repr(dict(self))