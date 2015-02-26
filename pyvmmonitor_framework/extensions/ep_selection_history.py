# License: LGPL
#
# Copyright: Brainwy Software
class EPSelectionHistory(object):
    '''
    Works with EPSelectionService and EPModelsContainer to go back/forward in the selection.
    '''

    def start_tracking(self):
        '''
        When called we'll start tracking the EPSelectionService for changes and will store any
        change (the EPSelectionService is gotten from its current 'pm' attribute, so, it must
        be registered in the PluginManager to work).
        '''

    def go_backward(self):
        '''
        Goes to the previous selection.
        '''

    def go_forward(self):
        '''
        Goes forward in the selection.
        '''

    def set_max_size(self, max_size):
        '''
        Changes the current maximum size of the selection history (initial size is 100 items).
        
        :param int max_size:
            The maximum size of the selection history.
        '''
