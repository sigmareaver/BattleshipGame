"""
-------------------------------------------------------------------------------
Battleship Game - Application Interface
-------------------------------------------------------------------------------

File Name: Application.py

Description:
    This file contains the implementation of the application for a Battleship
    game using PyQt6. It manages the window and native event handling components,
    and the application metadata.

Author: sigmareaver
Date Created: 12/02/2024

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

from PyQt6.QtWidgets import QApplication

import Globals
from NativeEventHandler import NativeEventHandler
from Window import BattleshipWindow


class BattleshipApplication(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setOrganizationName(Globals.org_name)
        self.setOrganizationDomain(Globals.org_domain)
        self.setApplicationName(Globals.app_name)

        self.battleship_window = BattleshipWindow()
        self.battleship_window.show()

        self.native_event_handler = NativeEventHandler(self.battleship_window)
        self.installNativeEventFilter(self.native_event_handler)
