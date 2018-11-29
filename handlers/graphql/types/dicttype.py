import graphene
class ObjectType(graphene.ObjectType):
    '''
    Implements mapping and iterable iterfaces around graphene's ObjectType so
    we could pass our objects to other functions pythonically
    '''

    def __iter__(self):
        for element in self._meta.fields:
            yield element, getattr(self, element)

    def keys(self):
        return self._meta.fields.keys()

    def __getitem__(self, item):
        return getattr(self, item)

