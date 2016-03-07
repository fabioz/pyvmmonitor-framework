# License: LGPL
#
# Copyright: Brainwy Software
from pyvmmonitor_core import abstract
from pyvmmonitor_core.callback import Callback
from pyvmmonitor_framework.extensions.ep_selection_history import EPSelectionHistory


class EPSelectionService(EPSelectionHistory):
    '''
    Note: the PluginManager is able to keep instances alive through each context, so, if there are
    many incompatible selections, one could ask for different selection contexts.

    I.e.:

    PluginManager.get_instance(EPSelectionHistory) as the default data selected and
    PluginManager.get_instance(EPSelectionHistory, 'window') for the window selected.
    '''

    def __init__(self):
        self.on_selection_changed = Callback()  # Called as on_selection_changed(source, selection)

    @abstract
    def set_selection(self, source, selection):
        '''
        Changes the selection and notifies users through on_selection_changed.

        :param source:
            The object that's the source of the selection (could be anything).

        :param object selection:
            The selected object (usually a string which maps to an obj_id in the model).
        '''

    @abstract
    def get_source(self):
        pass

    @abstract
    def get_selection(self):
        '''
        :rtype object:
            Return the selection selected.
        '''
