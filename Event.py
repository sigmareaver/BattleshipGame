"""
-------------------------------------------------------------------------------
Battleship Game - Event Management
-------------------------------------------------------------------------------

File Name: Event.py

Description:
    This file defines the EventManager class, which is responsible for managing
    and emitting signals related to various game events within the Battleship
    game. The EventManager class leverages PyQt6 to aggregate game events and
    expose signals indicating changes in game state, ship movements, player
    actions, and game outcomes such as victory or defeat.

Author: sigmareaver
Date Created: 11/27/2024

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

from PyQt6.QtCore import pyqtSignal, QObject, QRect


class EventManager(QObject):
    """
    Manages and emits signals related to game events.

    This class is responsible for aggregating various game events and
    emitting corresponding PyQt signals. The signals indicate changes
    in the game state, ship movements, player actions, and the outcome
    of the game such as victory or defeat.

    :ivar state_changed: Signal emitted when the state changes, carrying a string
                         that describes the new state.
    :type state_changed: pyqtSignal

    :ivar ship_moved: Signal emitted when a ship moves, carrying an integer for
                      index, a QRect for the bounding rectangle, and a boolean
                      indicating orientation.
    :type ship_moved: pyqtSignal

    :ivar player_hit: Signal emitted when a player lands a hit, carrying two
                      integers that specify the hit coordinates.
    :type player_hit: pyqtSignal

    :ivar player_miss: Signal emitted when a player misses, carrying two integers
                       that specify the miss coordinates.
    :type player_miss: pyqtSignal

    :ivar enemy_hit: Signal emitted when an enemy lands a hit, carrying two
                     integers that specify the hit coordinates.
    :type enemy_hit: pyqtSignal

    :ivar enemy_miss: Signal emitted when an enemy misses, carrying two integers
                      that specify the miss coordinates.
    :type enemy_miss: pyqtSignal

    :ivar victory: Signal emitted when the player wins the game.
    :type victory: pyqtSignal

    :ivar defeat: Signal emitted when the player loses the game.
    :type defeat: pyqtSignal
    """
    state_changed = pyqtSignal(str)
    ship_moved = pyqtSignal(int, QRect, bool)
    player_hit = pyqtSignal(int, int)
    player_miss = pyqtSignal(int, int)
    enemy_hit = pyqtSignal(int, int)
    enemy_miss = pyqtSignal(int, int)
    victory = pyqtSignal()
    defeat = pyqtSignal()


event_manager = EventManager()
