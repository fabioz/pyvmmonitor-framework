# License: LGPL
#
# Copyright: Brainwy Software
from pyvmmonitor_core.callback import Callback
from pyvmmonitor_framework.extensions.ep_selection_history import EPSelectionHistory


class EPSelectionService(EPSelectionHistory):

    def __init__(self):
        self.on_selection_changed = Callback()  # Called as on_selection_changed(source, selection)

    def set_selection(self, source, selection):
        '''
        Changes the selection and notifies users through on_selection_changed.
        
        :param source:
            The object that's the source of the selection (could be anything).
            
        :param list(str) selection:
            A list with the obj_ids selected in EPModelsContainer.
        '''

    def get_source(self):
        pass

    def get_selection(self):
        '''
        :rtype list(str):
            Returns a list with the selected item(s)
        '''
