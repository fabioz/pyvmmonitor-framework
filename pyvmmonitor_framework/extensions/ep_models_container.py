# License: LGPL
#
# Copyright: Brainwy Software
from pyvmmonitor_core import abstract
from pyvmmonitor_core.callback import Callback
from collections import OrderedDict

class EPModelsContainerNode(object):
    '''
    Identifies a node in the models container (so that we have items in tree-order).
    '''
    
    def __init__(self, parent, obj_id, data):
        '''
        :param EPModelsContainerNode parent: parent node
        :param str obj_id:
        :param object data:
        '''
        self.parent = parent
        self.obj_id = obj_id
        self.data = data
        self.children = OrderedDict()


class EPModelsContainer(object):
    '''
    This is a container of models.

    There are some protocols which may be expected by the objects added to this container:

    1. It'll receive an 'obj_id' automatically when it's added to the container (which will be
    the same id under it's added to -- note that ids must be unique in the model).

    2. It'll have a method called 'before_remove()' called before it's removed (if it does have that
    method)
    '''

    def __init__(self):
        self.on_add = Callback()  # Called as on_add(obj_id, obj)
        self.on_remove = Callback()  # Called as on_remove(obj_id, obj)

    @abstract
    def __setitem__(self, obj_id, obj):
        raise NotImplementedError

    @abstract
    def __getitem__(self, obj_id):
        raise NotImplementedError

    @abstract
    def get(self, obj_id, default=None):
        raise NotImplementedError

    @abstract
    def __contains__(self, obj_id):
        raise NotImplementedError

    @abstract
    def __delitem__(self, obj_id):
        raise NotImplementedError

    @abstract
    def clear(self):
        raise NotImplementedError

    @abstract
    def add_child(self, root_id, prefix, obj):
        '''
        Adds the passed child under root_id (with the given prefix) and returns
        the passed obj back.

        root_id may be empty.
        '''

    @abstract
    def __len__(self):
        raise NotImplementedError

    @abstract
    def print_rep(self, node=None, level=0, stream=None):
        raise NotImplementedError

    @abstract
    def itertree(self, node=None, recursive=True, class_=None):
        '''
        Iters children of the node sorted in tree order.

        :note: Usually to get all classes it'd be better to use iter_instances and
        to iterate all iteritems() (if the order is not important).

        Yields obj_id and the obj
        '''

    @abstract
    def get_node(self, obj_id):
        '''
        Returns the node for the given obj_id (to be passed
        in itertree or itertreenodes).

        :return EPModelsContainerNode:
        :raise KeyError: if the node is not available.
        '''

    @abstract
    def itertreenodes(self, node=None):
        '''
        Iter through nodes sorted in tree order (siblings may appear in any order).
        
        :param EPModelsContainerNode node:
        :return iterator(obj).
        '''

    @abstract
    def iteritems(self):
        '''
        Iterates over all the items in the model (obj_id, obj).
        '''

    @abstract
    def itervalues(self):
        '''
        Iterates over all the instances in the model (unsorted).
        '''

    @abstract
    def find_instance(self, class_):
        '''
        Finds an instance of the given class and returns it (returns None if it does not exist).
        
        :raise ValueError: If more than one instance is found for the given class.
        '''

    @abstract
    def iter_instances(self, class_):
        '''
        Returns an iterator over all the instances that implement a given class.
        '''
        