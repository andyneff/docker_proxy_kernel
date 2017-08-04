try:
    import ctypes
except:
    ctypes = None
import os
import sys
import platform
import signal
import time
try:
    from _thread import interrupt_main  # Py 3
except ImportError:
    from thread import interrupt_main  # Py 2

from traitlets.log import get_logger

import warnings

from ipykernel.parentpoller import (
    ParentPollerWindows as IpyKParentPollerWindows,
    ParentPollerUnix as IpyKParentPollerUnix
)

# Modification of ipykernel.parentpoller that allows for a custom exit call


class ParentPollerUnix(IpyKParentPollerUnix):
    def __init__(self, exit_call=None):
        self.exit_call = exit_call
        super(ParentPollerUnix, self).__init__()

    def run(self):
        # We cannot use os.waitpid because it works only for child processes.
        from errno import EINTR
        while True:
            try:
                if os.getppid() == 1:
                    get_logger().warning("Parent appears to have exited, "
                                         "shutting down.")
                    if self.exit_call:
                        self.exit_call()
                    else:
                        os._exit(1)
                time.sleep(1.0)
            except OSError as e:
                if e.errno == EINTR:
                    continue
                raise


class ParentPollerWindows(IpyKParentPollerWindows):

    def __init__(self, interrupt_handle=None, parent_handle=None,
                 exit_call=None):
        self.exit_call = exit_call
        super(ParentPollerWindows, self).__init__()

    def run(self):

        try:
            from _winapi import WAIT_OBJECT_0, INFINITE
        except ImportError:
            from _subprocess import WAIT_OBJECT_0, INFINITE

        # Build the list of handle to listen on.
        handles = []
        if self.interrupt_handle:
            handles.append(self.interrupt_handle)
        if self.parent_handle:
            handles.append(self.parent_handle)
        arch = platform.architecture()[0]
        c_int = ctypes.c_int64 if arch.startswith('64') else ctypes.c_int

        # Listen forever.
        while True:
            result = ctypes.windll.kernel32.WaitForMultipleObjects(
                len(handles),                            # nCount
                (c_int * len(handles))(*handles),        # lpHandles
                False,                                   # bWaitAll
                INFINITE)                                # dwMilliseconds

            if WAIT_OBJECT_0 <= result < len(handles):
                handle = handles[result - WAIT_OBJECT_0]

                if handle == self.interrupt_handle:
                    # check if signal handler is callable
                    # to avoid 'int not callable' error (Python issue #23395)
                    if callable(signal.getsignal(signal.SIGINT)):
                        interrupt_main()

                elif handle == self.parent_handle:
                    get_logger().warning("Parent appears to have exited, "
                                         "shutting down.")
                    if self.exit_call:
                        self.exit_call()
                    else:
                        os._exit(1)
            elif result < 0:
                # wait failed, just give up and stop polling.
                warnings.warn("""Parent poll failed.  If the frontend dies,
                the kernel may be left running.  Please let us know
                about your system (bitness, Python, etc.) at
                ipython-dev@scipy.org""")
                return


def setup_parent_poller(exit_call):
    ''' Duplicate ipykernel behavior '''
    parent_handle = int(os.environ.get('JPY_PARENT_PID') or 0),
    if sys.platform == 'win32':
        interrupt = int(os.environ.get('JPY_INTERRUPT_EVENT') or 0)
        if interrupt or parent_handle:
            poller = ParentPollerWindows(interrupt, parent_handle, exit_call)
    elif parent_handle and parent_handle != 1:
        poller = ParentPollerUnix(exit_call)

    if poller:
        poller.start()
