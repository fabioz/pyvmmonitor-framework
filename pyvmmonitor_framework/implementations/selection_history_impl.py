# License: LGPL
#
# Copyright: Brainwy Software
from pyvmmonitor_framework.extensions.ep_models_container import EPModelsContainer
from pyvmmonitor_framework.extensions.ep_selection_history import EPSelectionHistory
from pyvmmonitor_framework.extensions.ep_selection_service import EPSelectionService


class SelectionHistory(object):

    def __init__(self):
        self._selection_history = []
        self._curr_selection = 0
        self._changing = 0
        self._max_size = 100  # Default max size

    def start_tracking(self):
        pm = self.pm()
        if pm is None or pm.exited:
            return
        sel_service = pm.get_instance(EPSelectionService)
        sel_service.on_selection_changed.register(self._on_selection_changed)

    def _on_selection_changed(self, source, selection):
        if self._changing or source is self:
            return

        # Delete from the point we were in
        del self._selection_history[self._curr_selection:]
        self._selection_history.append(selection)
        self._curr_selection = len(self._selection_history)
        self._trim_size()

    def get_current_selection(self):
        try:
            return self._selection_history[self._curr_selection - 1]
        except IndexError:
            return ()

    def __len__(self):
        return len(self._selection_history)

    def _get_new_selection_removing_ids_no_longer_available(self, backward):
        pm = self.pm()
        if pm is None or pm.exited:
            return
        models = pm.get_instance(EPModelsContainer)

        while True:
            curr = self._selection_history[self._curr_selection - 1]
            for c in curr:
                if c not in models:
                    # Only create copy/update contents if we find one removed
                    curr = tuple(x for x in curr if x in models)
                    self._selection_history[self._curr_selection - 1] = curr
                    break

            if curr:
                return curr

            # It was changed and became empty... remove that entry and check the next one.
            del self._selection_history[self._curr_selection - 1]

            if backward:
                if self._curr_selection <= 1:  # Can't go past the first
                    return ()
                self._curr_selection -= 1
            else:
                if self._curr_selection > len(self._selection_history):  # Can't go past the last
                    # Must fix it to point to the last as the previous last was removed.
                    self._curr_selection = len(self._selection_history)
                    return ()

                if self._curr_selection == len(self._selection_history):  # Can't go past the last
                    return ()

    def _go(self, backward):
        pm = self.pm()
        if pm is None or pm.exited:
            return
        sel_service = pm.get_instance(EPSelectionService)
        self._changing += 1
        try:
            new_sel = self._get_new_selection_removing_ids_no_longer_available(backward=backward)
            if new_sel:
                sel_service.set_selection(self, new_sel)
        finally:
            self._changing -= 1

    def go_forward(self):
        if self._curr_selection >= len(self._selection_history):  # Can't go past the last
            return
        self._curr_selection += 1
        self._go(False)

    def go_backward(self):
        if self._curr_selection <= 1:  # Can't go past the first
            return
        self._curr_selection -= 1
        self._go(True)

    def set_max_size(self, max_size):
        if max_size < 2:
            raise ValueError('Max size must be >= 2')
        self._max_size = max_size
        self._trim_size()

    def _trim_size(self):
        max_size = self._max_size
        while len(self._selection_history) > max_size:
            del self._selection_history[0]


def start_tracking(pm):
    selection_history = pm.get_instance(EPSelectionHistory)
    selection_history.start_tracking()
