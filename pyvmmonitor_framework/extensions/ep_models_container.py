# License: LGPL
#
# Copyright: Brainwy Software
from pyvmmonitor_core.callback import Callback


class EPModelsContainer(object):
    '''
    This is a container of models.

    There are some protocols which may be expected by the objects added to this container:

    1. It'll receive an 'obj_id' automatically when it's added to the container

    2. It'll have a method called 'before_remove()' called before it's removed (if it does have that
    method)
    '''

    def __init__(self):
        self.on_add = Callback()  # Called as on_add(obj_id, obj)
        self.on_remove = Callback()  # Called as on_remove(obj_id, obj)

    def __setitem__(self, obj_id, obj):
        raise NotImplementedError

    def __getitem__(self, obj_id):
        raise NotImplementedError

    def get(self, obj_id, default=None):
        raise NotImplementedError

    def __contains__(self, obj_id):
        raise NotImplementedError

    def __delitem__(self, obj_id):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def add_child(self, root_id, prefix, obj):
        '''
        Adds the passed child under root_id (with the given prefix) and returns
        the passed obj back.

        root_id may be empty.
        '''
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def print_rep(self, node=None, level=0, stream=None):
        raise NotImplementedError

    def itertree(self, node=None, recursive=True, class_=None):
        '''
        Iters children of the node sorted in tree order.

        :note: Usually to get all classes it'd be better to use iter_instances and
        to iterate all iteritems() (if the order is not important).

        Yields obj_id and the obj
        '''
        raise NotImplementedError

    def get_node(self, obj_id):
        '''
        Returns the node for the given obj_id (to be passed
        in itertree or itertreenodes).

        :raise KeyError: if the node is not available.
        '''

    def itertreenodes(self, node=None):
        '''
        Iter nodes sorted in tree order
        '''
        raise NotImplementedError

    def iteritems(self):
        '''
        Iter unsorted
        '''
        raise NotImplementedError

    def itervalues(self):
        raise NotImplementedError

    def find_instance(self, class_):
        raise NotImplementedError

    def iter_instances(self, class_):
        raise NotImplementedError