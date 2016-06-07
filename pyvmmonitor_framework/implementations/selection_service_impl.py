# License: LGPL
#
# Copyright: Brainwy Software
import sys

from pyvmmonitor_core import overrides
from pyvmmonitor_core.iterables import remove_duplicates
from pyvmmonitor_core.thread_utils import is_in_main_thread
from pyvmmonitor_framework.extensions.ep_selection_service import EPSelectionService


if sys.version_info[0] < 3:
    basestring = basestring
else:
    basestring = (str, bytes)


class SelectionService(EPSelectionService):

    def __init__(self):
        EPSelectionService.__init__(self)
        self._selection = ()
        self._source = None

    @overrides(EPSelectionService.set_selection)
    def set_selection(self, source, selection):
        if isinstance(selection, basestring):
            selection = (selection,)

        # Note: besides removing the duplicates, will also convert the type to a tuple.
        selection = remove_duplicates(selection, ret_type=tuple)

        assert isinstance(selection, tuple)

        assert is_in_main_thread(), 'Can only change selection in main thread.'

        if selection == self._selection:
            return False

        self._selection = selection
        self._source = source

        self._do_selection(source, selection)
        return True

    def _do_selection(self, source, selection):
        '''
        Available for subclasses to override.
        '''
        self.on_selection_changed(source, selection)

    @overrides(EPSelectionService.get_selection)
    def get_selection(self):
        return self._selection

    @overrides(EPSelectionService.get_source)
    def get_source(self):
        return self._source
