"""
-------------------------------------------------------------------------------
Battleship Game - Application User Data
-------------------------------------------------------------------------------

File Name: Data.py

Description:
    This file contains user data variables for the Battleship game.
    It tracks user statistics such as wins and losses.

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

from PyQt6.QtCore import QStandardPaths, QSettings

import Globals


class Data():
    data_directory = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppDataLocation
    )
    data = QSettings(Globals.org_name, Globals.app_name)

    def setValue(self, key, value):
        self.data.setValue(key, value)

    def value(self, key):
        return self.data.value(key)

data = Data()
