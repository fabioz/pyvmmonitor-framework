import time

from pyvmmonitor_core import compat
from pyvmmonitor_core.thread_utils import is_in_main_thread


def _assert_condition_within_timeout(condition, timeout=2.):
    assert is_in_main_thread()
    initial = time.time()
    while True:
        c = condition()
        if isinstance(c, bool):
            if c:
                return
        elif isinstance(c, (compat.bytes, compat.unicode)):
            if not c:
                return
        else:
            raise AssertionError('Expecting bool or string as the return.')

        if time.time() - initial > timeout:
            raise AssertionError(
                u'Could not reach condition before timeout: %s (condition return: %s)' %
                (timeout, c))

        # process_events()
        time.sleep(1 / 60.)


def test_selection_service():
    from pyvmmonitor_framework.implementations.selection_service_impl import SelectionService
    s = SelectionService()

    called_result = []

    def func(*args):
        raise AssertionError('should not be called')
    s.on_selection_changed.register(func)

    def call():
        try:
            s.set_selection(None, 'bar')
            called_result.append('error')
        except:
            called_result.append('ok')  # we expect the exception

    import threading
    threading.Thread(target=call).start()

    def check():
        return len(called_result) > 0

    _assert_condition_within_timeout(check)
    assert called_result[0] == 'ok'
