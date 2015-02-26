import pytest

from pyvmmonitor_core.plugins import PluginManager
from pyvmmonitor_framework.extensions.ep_models_container import EPModelsContainer
from pyvmmonitor_framework.implementations.models_container_impl import ModelsContainer


def test_model_and_plugin():
    pm = PluginManager()
    pm.register(EPModelsContainer, 'pyvmmonitor_framework.implementations.models_container_impl.ModelsContainer', keep_instance=True)
    model = pm.get_instance(EPModelsContainer)

    class M1(object):
        pass

    m1 = model['m1'] = M1()
    assert m1.model() is model
    assert m1.pm() is pm


def test_find_instance():
    model = ModelsContainer()

    class M1(object):
        pass

    class M2(object):
        pass

    model['m1'] = M1()
    model['m2'] = M2()

    assert isinstance(model.find_instance(M1), M1)
    assert 'm1' in model
    with pytest.raises(AssertionError):
        model['m1'] = M2()


def test_model_as_root():
    model = ModelsContainer()

    class Item:
        pass

    model['root'] = Item()
    assert len(model) == 1
    model.add_child('', 'root', Item())
    assert len(model) == 2
    model.add_child(None, 'root', Item())
    assert len(model) == 3


def test_model():
    model = ModelsContainer()

    class Item:
        pass

    changes = []

    def on_add(obj_id, obj):
        changes.append(('add', obj_id))

    def on_remove(obj_id, obj):
        changes.append(('remove', obj_id))

    model.on_add.register(on_add)
    model.on_remove.register(on_remove)
    model['root'] = Item()
    assert [('add', 'root')] == changes

    with pytest.raises(AssertionError):
        model['root'] = Item()
    model['root.c1'] = Item()
    model['root.c2'] = Item()
    t = model['root.c2.bar'] = Item()
    assert t.obj_id == 'root.c2.bar'

    assert 4 == len(model)
    assert 4 == len(list(model.itertree()))

    del model['root']
    assert t.obj_id is None

    assert 0 == len(model._root.children)
    assert 0 == len(model)
    assert 0 == len(list(model.itertree()))

    model['root'] = Item()
    assert 'root' == model['root'].obj_id
    item = model.add_child('root', 'c_', Item())
    del model[item.obj_id]

    found = '\n'.join('%s: %s' % x for x in changes)
    assert '''add: root
add: root.c1
add: root.c2
add: root.c2.bar
remove: root.c1
remove: root.c2.bar
remove: root.c2
remove: root
add: root
add: root.c_001
remove: root.c_001'''.replace('\r\n', '\n') == found
