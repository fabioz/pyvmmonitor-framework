# License: LGPL
#
# Copyright: Brainwy Software
from pyvmmonitor_core.callback import Callback


class EPSelectionService(object):

    DEFAULT_CONTEXT = None

    def __init__(self):
        self.on_selection_changed = Callback()  # Called as on_selection_changed(source, selection)

    def set_selection(self, source, selection):
        pass

    def get_source(self):
        pass

    def get_selection(self):
        '''
        :rtype list(str):
            Returns a list with the selected item(s)
        '''
