# License: LGPL
#
# Copyright: Brainwy Software
from pyvmmonitor_core.plugins import PluginManager
from pyvmmonitor_framework.extensions.ep_models_container import EPModelsContainer
from pyvmmonitor_framework.extensions.ep_selection_history import EPSelectionHistory
from pyvmmonitor_framework.extensions.ep_selection_service import EPSelectionService


def _setup():
    pm = PluginManager()
    pm.register(
        EPSelectionHistory,
        'pyvmmonitor_framework.implementations.selection_history_impl.SelectionHistory',
        keep_instance=True)

    pm.register(
        EPSelectionService,
        'pyvmmonitor_framework.implementations.selection_service_impl.SelectionService',
        keep_instance=True)
    pm.register(
        EPModelsContainer,
        'pyvmmonitor_framework.implementations.models_container_impl.ModelsContainer',
        keep_instance=True)

    class Stub(object):
        pass

    models = pm.get_instance(EPModelsContainer)

    sel_history = pm.get_instance(EPSelectionHistory)
    sel_history.start_tracking()
    assert sel_history.get_current_selection() == ()

    sel_service = pm.get_instance(EPSelectionService)
    models['a'] = Stub()
    models['b'] = Stub()
    models['c'] = Stub()
    models['d'] = Stub()
    return sel_service, sel_history, models, pm


def test_selection_removal_history():
    sel_service, sel_history, models, pm = _setup()
    sel_service.set_selection(None, ['a'])
    sel_service.set_selection(None, ['b'])
    sel_service.set_selection(None, ['c'])
    sel_service.set_selection(None, ['d'])

    del models['c']
    assert sel_service.get_selection() == ('d',)
    sel_history.go_backward()
    assert sel_service.get_selection() == ('b',)


def test_selection_history():
    sel_service, sel_history, models, pm = _setup()

    sel_service.set_selection(None, ['a'])
    assert len(sel_history) == 1
    sel_service.set_selection(None, ['b'])
    sel_service.set_selection(None, ['b', 'c'])

    assert len(sel_history) == 3

    assert sel_history.get_current_selection() == ('b', 'c')
    sel_history.go_backward()
    assert sel_history.get_current_selection() == ('b',)
    sel_history.go_backward()
    assert sel_history.get_current_selection() == ('a',)
    sel_history.go_backward()  # Can't go past the first one
    assert sel_history.get_current_selection() == ('a',)

    assert len(sel_history) == 3

    sel_history.go_forward()
    assert sel_history.get_current_selection() == ('b',)
    sel_history.go_forward()
    assert sel_history.get_current_selection() == (('b', 'c'))
    sel_history.go_forward()  # Can't go past the last one
    assert sel_history.get_current_selection() == (('b', 'c'))

    sel_history.go_backward()
    assert sel_history.get_current_selection() == ('b',)
    assert sel_service.get_selection() == ('b',)
    assert len(sel_history) == 3

    sel_service.set_selection(None, 'd')
    assert sel_history.get_current_selection() == ('d',)
    assert len(sel_history) == 3

    del models['d']
    sel_history.go_forward()
    assert len(sel_history) == 3
    assert sel_history.get_current_selection() == ('d',)

    # Go backward is ok
    sel_history.go_backward()
    assert sel_history.get_current_selection() == ('b',)
    assert len(sel_history) == 3

    # We can't go forward anymore...
    sel_history.go_forward()
    assert sel_history.get_current_selection() == ('b',)
    assert len(sel_history) == 2

    sel_history.go_forward()
    assert sel_history.get_current_selection() == ('b',)
    assert len(sel_history) == 2

    sel_history.go_backward()
    assert sel_history.get_current_selection() == ('a',)
    assert len(sel_history) == 2

    del models['a']
    sel_history.go_backward()
    assert sel_history.get_current_selection() == ('a',)
    assert len(sel_history) == 2

    sel_history.go_forward()
    assert sel_history.get_current_selection() == ('b',)
    assert len(sel_history) == 2

    sel_history.go_backward()
    assert sel_history.get_current_selection() == ('b',)
    assert len(sel_history) == 1

    del models['b']
    sel_history.go_backward()
    assert sel_history.get_current_selection() == ('b',)
    sel_history.go_forward()
    assert sel_history.get_current_selection() == ('b',)
    assert len(sel_history) == 1
