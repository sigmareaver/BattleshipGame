"""
-------------------------------------------------------------------------------
Battleship Game - Native Event Handling
-------------------------------------------------------------------------------

File Name: NativeEventHandler.py

Description:
    This file implements platform-specific native event handling for the
    Battleship game. It defines a base event handler class and provides
    platform-dependent subclasses to manage custom keyboard events that
    interact directly with the underlying operating system. The implementation
    includes support for Linux, with stubs for Windows and macOS. The
    CustomKeyEvent class allows handling custom key inputs, enhancing game
    control capabilities through native events.

Author: sigmareaver
Date Created: 11/24/2024

License:
    This code is licensed under the MIT License. You can use,
    modify, and distribute this code under the terms of the MIT License.
    For more details, see the LICENSE file in the root directory of this
    project or visit [https://mit-license.org/].

Acknowledgements:
    This project utilizes the PyQt6 library for creating graphical interfaces
    and may include open-source components under their respective licenses.

-------------------------------------------------------------------------------
"""

import platform, ctypes
from PyQt6 import sip
from PyQt6.QtCore import QAbstractNativeEventFilter, QEvent
from PyQt6.QtWidgets import QApplication, QMainWindow


class CustomKeyEvent(QEvent):
    CustomEventType = QEvent.Type(QEvent.registerEventType())

    def __init__(self, key):
        super().__init__(CustomKeyEvent.CustomEventType)
        self._key = key

    def key(self):
        return chr(self._key)

    def raw_key(self):
        return self._key

    def is_ascii(self):
        return 0 <= self._key <= 255


class BaseNativeEventHandler(QAbstractNativeEventFilter):
    window = QMainWindow

    def __init__(self, window):
        super().__init__()
        self.window = window

    def nativeEventFilter(self, event_type, message):
        raise NotImplementedError("nativeEventFilter must be implemented in subclasses")


# Linux Implementation
if platform.system() == "Linux":
    try:
        from Xlib import display

        class LinuxNativeEventHandler(BaseNativeEventHandler):
            class XcbGenericEventT(ctypes.Structure):
                _fields_ = [
                    ('response_type', ctypes.c_uint8),
                    ('pad0', ctypes.c_uint8),
                    ('sequence', ctypes.c_uint16),
                    ('pad', ctypes.c_uint32 * 7),
                    ('full_sequence', ctypes.c_uint32)
                ]

            class XcbKeyPressEventT(ctypes.Structure):
                _fields_ = [
                    ('response_type', ctypes.c_uint8),
                    ('detail', ctypes.c_uint8),  # This is the keycode
                    ('sequence', ctypes.c_uint16),
                    ('time', ctypes.c_uint32),
                    ('root', ctypes.c_uint32),
                    ('event', ctypes.c_uint32),
                    ('child', ctypes.c_uint32),
                    ('root_x', ctypes.c_int16),
                    ('root_y', ctypes.c_int16),
                    ('event_x', ctypes.c_int16),
                    ('event_y', ctypes.c_int16),
                    ('state', ctypes.c_uint16),
                    ('same_screen', ctypes.c_uint8)
                ]

            def __init__(self, window):
                super().__init__(window)
                self.display = display.Display()

            def nativeEventFilter(self, event_type, message : sip.voidptr):
                retval, result = False, 0
                if event_type == "xcb_generic_event_t":
                    ptr = ctypes.cast(int(message), ctypes.POINTER(self.XcbGenericEventT))
                    event = ptr.contents
                    if event.response_type == 2:
                        key_event_ptr = ctypes.cast(ptr, ctypes.POINTER(self.XcbKeyPressEventT))
                        key_event = key_event_ptr.contents
                        keycode = key_event.detail
                        keysym = self.display.keycode_to_keysym(keycode, 0)
                        custom_event = CustomKeyEvent(keysym)
                        QApplication.postEvent(self.window, custom_event)
                return retval, result

        NativeEventHandler = LinuxNativeEventHandler

    except ImportError:
        print("Xlib not available. Linux NativeEventHandler cannot be used.")
elif platform.system() == 'Windows':
    # Windows Implementation (Stub)
    from ctypes import wintypes
    WM_KEYDOWN = 0x0100
    user32 = ctypes.windll.user32

    class WindowsNativeEventHandler(BaseNativeEventHandler):
        # Define MSG structure for use with ctypes
        class MSG(ctypes.Structure):
            _fields_ = [
                ("hwnd", wintypes.HWND),
                ("message", wintypes.UINT),
                ("wParam", wintypes.WPARAM),
                ("lParam", wintypes.LPARAM),
                ("time", wintypes.DWORD),
                ("pt", wintypes.POINT),
            ]

        def __init__(self, window):
            super().__init__(window)

        def nativeEventFilter(self, event_type, message):
            if event_type == "windows_generic_MSG":
                msg = ctypes.cast(message, ctypes.POINTER(self.MSG)).contents
                if msg.message == WM_KEYDOWN:
                    vk_code = msg.wParam
                    # Translate virtual-key into ASCII
                    ascii_key = user32.MapVirtualKeyW(vk_code, 2)
                    if ascii_key:
                        custom_event = CustomKeyEvent(ascii_key)
                        QApplication.postEvent(self.window, custom_event)
                    return True, 0
            return False, 0

    NativeEventHandler = WindowsNativeEventHandler
elif platform.system() == 'Darwin':  # macOS
    # macOS Implementation (Stub)
    class MacOSNativeEventHandler(BaseNativeEventHandler):
        def __init__(self, window):
            super().__init__(window)

        def nativeEventFilter(self, event_type, message):
            # Implement macOS-specific native event handling if necessary
            raise NotImplementedError("MacOS support has not been implemented yet.")
            # return False, 0

    NativeEventHandler = MacOSNativeEventHandler
else:
    class NativeEventHandler(BaseNativeEventHandler):
        def nativeEventFilter(self, event_type, message):
            # No-op on unsupported platforms or provide a basic implementation
            return False, 0
