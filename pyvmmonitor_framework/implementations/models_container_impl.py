# License: LGPL
#
# Copyright: Brainwy Software
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import sys

from pyvmmonitor_core import thread_utils, overrides, compat
from pyvmmonitor_core.weak_utils import get_weakref
from pyvmmonitor_framework.extensions.ep_models_container import EPModelsContainer,\
    EPModelsContainerNode


class _Node(EPModelsContainerNode):

    __slots__ = ['parent', 'data', 'obj_id', 'children', '_prefix_to_id']

    def add_child(self, node):
        self.children[node.obj_id] = node

    def next_id(self, prefix):
        if not hasattr(self, '_prefix_to_id'):
            self._prefix_to_id = {}

        i = self._prefix_to_id.get(prefix, 0) + 1
        self._prefix_to_id[prefix] = i
        return i


class ModelPart(object):

    '''
    Instances added to the ModelsContainer will have the attributes below set when they enter the model.

    :ivar str obj_id: This is the id of the object in the model.
    :ivar PluginManager pm: weak-reference to the PluginManager.
    :ivar EPModelsContainer model: weak-reference to the model the instance is in.
    '''

    def __init__(self):
        self.obj_id = ''
        self.pm = \
            self.model = get_weakref(None)


class ModelsContainer(EPModelsContainer):

    '''
    This is the model of the application. Objects start living when added to it and should die
    (i.e.: be garbage-collected) when removed.
    '''

    __slots__ = ['_fast', '_root', 'on_add', 'on_remove']

    def __init__(self):
        self._fast = {}
        self._root = _Node(None, None, None)
        self._class_to_object_ids = {}

        # Will be set by the PluginManager later if done as an instance.
        self.pm = get_weakref(None)

        self._weak_self = get_weakref(self)
        EPModelsContainer.__init__(self)

    @overrides(EPModelsContainer.__setitem__)
    def __setitem__(self, obj_id, obj):
        assert thread_utils.is_in_main_thread()
        assert obj_id not in self._fast

        try:
            i = obj_id.rindex('.')
        except ValueError:
            parent_node = self._root
        else:
            parent_node = self._fast[obj_id[:i]]

        self._add_child_node(parent_node, obj_id, obj)
        return obj

    def _add_child_node(self, parent_node, obj_id, obj):
        node = _Node(parent_node, obj_id, obj)
        obj.obj_id = obj_id
        obj.pm = self.pm
        obj.model = self._weak_self

        self._fast[obj_id] = node
        s = self._class_to_object_ids.get(obj.__class__)
        if s is None:
            s = self._class_to_object_ids[obj.__class__] = set()
        s.add(obj_id)

        parent_node.add_child(node)
        self.on_add(obj_id, obj)

    @overrides(EPModelsContainer.__getitem__)
    def __getitem__(self, obj_id):
        return self._fast[obj_id].data

    @overrides(EPModelsContainer.get)
    def get(self, obj_id, default=None):
        node = self._fast.get(obj_id)
        if node is None:
            return default
        return node.data

    @overrides(EPModelsContainer.__contains__)
    def __contains__(self, obj_id):
        return obj_id in self._fast

    @overrides(EPModelsContainer.__delitem__)
    def __delitem__(self, obj_id):
        node = self._fast[obj_id]
        for child_obj_id in list(node.children):
            del self[child_obj_id]

        self.on_remove(obj_id, node.data)
        if hasattr(node.data, 'before_remove'):
            node.data.before_remove()
        del node.parent.children[obj_id]

        self._class_to_object_ids.get(node.data.__class__).remove(obj_id)
        del self._fast[obj_id]
        node.data.obj_id = None  # Set the obj_id to None after it's removed.

    @overrides(EPModelsContainer.clear)
    def clear(self):
        for obj_id in list(self._root.children):
            del self[obj_id]

    @overrides(EPModelsContainer.add_child)
    def add_child(self, root_id, prefix, obj):
        assert thread_utils.is_in_main_thread()

        if root_id:
            parent_node = self._fast[root_id]
            prefix = '%s.%s' % (root_id, prefix)
        else:
            parent_node = self._root

        obj_id = '%s%03d' % (prefix, parent_node.next_id(prefix))
        while obj_id in self._fast:
            obj_id = '%s%03d' % (prefix, parent_node.next_id(prefix))

        self._add_child_node(parent_node, obj_id, obj)
        return obj

    @overrides(EPModelsContainer.__len__)
    def __len__(self):
        return self._fast.__len__()

    @overrides(EPModelsContainer.print_rep)
    def print_rep(self, node=None, level=0, stream=None):
        if stream is None:
            stream = sys.stdout

        if node is None:
            node = self._root

        pre = ' ' * (2 * level)
        for child in node.children.itervalues():
            stream.write('%s%s: %s\n' % (pre, child.obj_id, child.data.__class__.__name__))
            self.print_rep(child, level + 1, stream)

    def __str__(self, *args, **kwargs):
        stream = StringIO()
        self.print_rep(stream=stream)
        return stream.getvalue()

    @overrides(EPModelsContainer.itertree)
    def itertree(self, node=None, recursive=True, class_=None):
        '''
        Iters children of the node sorted in tree order.

        :note: Usually to get all classes it'd be better to use iter_instances and
        to iterate all iteritems() (if the order is not important).

        Yields obj_id and the obj
        '''
        assert thread_utils.is_in_main_thread()
        if node is None:
            node = self._root

        if recursive:
            if not class_:
                return self._iter_recursive_no_class(node)
            else:
                return self._iter_recursive_class(node, class_)

        else:
            if class_:
                return self._iter_no_recursive_class(node, class_)
            else:
                return self._iter_no_recursive_no_class(node)

    def _iter_no_recursive_class(self, node, class_):
        for obj_id, child in compat.iteritems(node.children):
            if isinstance(child.data, class_):
                yield obj_id, child.data

    def _iter_no_recursive_no_class(self, node):
        for obj_id, child in compat.iteritems(node.children):
            yield obj_id, child.data

    def _iter_recursive_no_class(self, node):
        for obj_id, child in compat.iteritems(node.children):
            yield obj_id, child.data

            for data in self._iter_recursive_no_class(child):
                yield data

    def _iter_recursive_class(self, node, class_):
        for obj_id, child in compat.iteritems(node.children):
            if isinstance(child.data, class_):
                yield obj_id, child.data

            for data in self._iter_recursive_class(child, class_):
                yield data

    @overrides(EPModelsContainer.get_node)
    def get_node(self, obj_id):
        return self._fast[obj_id]

    @overrides(EPModelsContainer.itertreenodes)
    def itertreenodes(self, node=None):
        if node is None:
            node = self._root

        for child in compat.itervalues(node.children):
            yield child

            for data in self.itertreenodes(child):
                yield data

    @overrides(EPModelsContainer.iteritems)
    def iteritems(self):
        for key, node in compat.iteritems(self._fast):
            yield key, node.data

    @overrides(EPModelsContainer.itervalues)
    def itervalues(self):
        for node in self._fast.itervalues():
            yield node.data

    @overrides(EPModelsContainer.find_instance)
    def find_instance(self, class_):
        ids = self._class_to_object_ids.get(class_, [])
        ids_len = ids.__len__()

        if ids_len == 1:
            return self[compat.next(ids.__iter__())]

        elif ids_len == 0:
            return None

        else:
            raise ValueError('Found: %s instances of %s' % (len(ids), class_))

    @overrides(EPModelsContainer.iter_instances)
    def iter_instances(self, class_):
        ids = self._class_to_object_ids.get(class_, [])

        for obj_id in ids:
            yield self[obj_id]

    def plugins_exit(self):
        self.clear()
