"""
-------------------------------------------------------------------------------
Battleship Game - Main Entry Point
-------------------------------------------------------------------------------

File Name: main.py

Description:
    This file serves as the entry point for the Battleship game application.
    It initializes the Battleship application by creating an instance of the
    BattleshipApplication class and starts the event loop. The application
    handles command-line arguments and manages application execution flow.

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


import sys
from Application import BattleshipApplication


def main():
    """
    Entry point for the Battleship application. This function initializes
    the Battleship application with the provided command-line arguments
    and starts the application's event loop.

    It creates an instance of the BattleshipApplication class, passing
    the system arguments to it. Upon successful execution, the application
    terminates with the same exit status as returned by the `exec` method.

    :return: None
    """
    app = BattleshipApplication(sys.argv)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
