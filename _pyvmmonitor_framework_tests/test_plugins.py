from py.test import raises

from pyvmmonitor_core.plugins import PluginManager, NotInstanceError
from pyvmmonitor_framework.extensions.ep_models_container import EPModelsContainer
from pyvmmonitor_framework.extensions.ep_selection_service import EPSelectionService


def test_plugins():
    pm = PluginManager()
    pm.register(
        EPModelsContainer,
        'pyvmmonitor_framework.implementations.models_container_impl.ModelsContainer',
        keep_instance=True
    )
    model = pm.get_instance(EPModelsContainer)
    assert model is not None
    assert model is pm.get_instance(EPModelsContainer)
    from pyvmmonitor_framework.implementations.models_container_impl import ModelsContainer
    assert isinstance(model, ModelsContainer), 'Expected ModelsContainer. Found: %s' % (model,)


def test_instance_in_context():
    pm = PluginManager()
    pm.register(
        EPSelectionService,
        'pyvmmonitor_framework.implementations.selection_service_impl.SelectionService',
        keep_instance=True)
    s0 = pm.get_instance(EPSelectionService)
    s1 = pm.get_instance(EPSelectionService, 'window')
    assert s0 is not s1
    assert s0.pm() is pm


def test_get_impl_for_non_instance_kept():
    pm = PluginManager()
    pm.register(
        EPSelectionService,
        'pyvmmonitor_framework.implementations.selection_service_impl.SelectionService')
    with raises(NotInstanceError):
        pm.get_instance(EPSelectionService)
    assert len(pm.get_implementations(EPSelectionService)), 2
