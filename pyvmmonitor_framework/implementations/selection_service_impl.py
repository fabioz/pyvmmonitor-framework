# License: LGPL
#
# Copyright: Brainwy Software
from pyvmmonitor_core import overrides
from pyvmmonitor_core.thread_utils import is_in_main_thread
from pyvmmonitor_framework.extensions.ep_selection_service import EPSelectionService


class SelectionService(EPSelectionService):

    def __init__(self):
        EPSelectionService.__init__(self)
        self._selection = ()
        self._source = None
        self._in_selection = 0

    @overrides(EPSelectionService.set_selection)
    def set_selection(self, source, selection):
        if isinstance(selection, list):
            selection = tuple(selection)

        if isinstance(selection, basestring):
            selection = (selection,)

        assert isinstance(selection, tuple)

        assert is_in_main_thread(), 'Can only change selection in main thread.'

        if selection == self._selection and self._in_selection:
            # I.e.: a selection by some object triggered a selection in another object for the
            # same elements (in which case we can safely ignore it).
            return

        self._selection = selection
        self._source = source

        self._in_selection += 1
        try:
            self.on_selection_changed(source, selection)
        finally:
            self._in_selection -= 1

    @overrides(EPSelectionService.get_selection)
    def get_selection(self):
        return self._selection

    @overrides(EPSelectionService.get_source)
    def get_source(self):
        return self._source
