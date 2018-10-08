from .xenobject import XenObject
class Task(XenObject):
    api_class = 'task'
    EVENT_CLASSES = ['task']
