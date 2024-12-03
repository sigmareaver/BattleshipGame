"""
-------------------------------------------------------------------------------
Battleship Game - Game Logic and Management
-------------------------------------------------------------------------------

File Name: Game.py

Description:
    This file contains the core game logic and management for the Battleship
    game. It includes classes for defining the state of the game, managing
    game boards, controlling game flow, and interactions between players and
    the game environment. The `Game` class provides mechanisms to handle player
    and enemy actions, transition between game states, and determine the game
    outcome.

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


import random
import Event


class State:
    """
    Represents the various states in a game lifecycle.

    This class defines constants to represent different states that a game can be
    in, such as during player placement, the player's turn, the enemy's turn, or
    when the game has finished. It can be used to control the flow of the game
    logic by checking and updating the current state.

    :ivar PLACEMENT: Indicates that the game is currently in the placement phase,
        where players may be setting up their game pieces.
    :type PLACEMENT: str
    :ivar PLAYER_TURN: Indicates that it is currently the player's turn to take
        an action in the game.
    :type PLAYER_TURN: str
    :ivar ENEMY_TURN: Indicates that it is currently the enemy's turn to take
        an action in the game.
    :type ENEMY_TURN: str
    :ivar GAME_FINISHED: Indicates that the game has concluded and no further
        actions can be taken by either player or enemy.
    :type GAME_FINISHED: str
    """
    PLACEMENT = "placement"
    PLAYER_TURN = "player_turn"
    ENEMY_TURN = "enemy_turn"
    GAME_FINISHED = "game_finished"


class Board:
    """
    Represents a game board for placing and managing ships, typically used in
    games similar to Battleship. The board allows positioning ships either
    manually by specifying their coordinates or randomly within the board
    dimensions. It also manages hits and misses on the ships and provides
    functionality to validate ship positions to ensure they do not overlap.

    :ivar width: The width of the game board.
    :type width: int
    :ivar height: The height of the game board.
    :type height: int
    :ivar hits: A list containing all the coordinates of hits made on the ships.
    :type hits: list
    :ivar misses: A list containing all the coordinates of misses made on the board.
    :type misses: list
    :ivar ships: A nested list representing the positions of placed ships on the board.
                 Each ship is represented as a list of four integers, specifying its
                 bounding rectangle.
    :type ships: list
    """
    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height

        self.reset()

    def reset(self):
        self.hits = []
        self.misses = []
        self.ships = [[-1 for x in range(4)] for y in range(5)]

    def move_ship(self, idx, rect, vertical):
        if vertical:
            if rect.x() < rect.width():
                self.ships[idx] = [rect.x(), rect.y(), rect.width() - 1, rect.height() - 1]
            else:
                self.ships[idx] = [rect.width(), rect.height(), rect.x() - 1, rect.y() - 1]
        else:
            if rect.x() < rect.width():
                self.ships[idx] = [rect.x(), rect.y(), rect.width() - 1, rect.height() - 1]
            else:
                self.ships[idx] = [rect.width(), rect.height(), rect.x() - 1, rect.y() - 1]


    def is_hit(self, x, y):
        # Check if the given (x, y) hits any ship
        for ship in self.ships:
            x1, y1, x2, y2 = ship
            if x1 <= x <= x2 and y1 <= y <= y2:
                return True  # Hit
        return False  # Miss

    def total_ship_cells(self):
        total = 0
        for ship in self.ships:
            x1, y1, x2, y2 = ship
            total += (x2 - x1 + 1) * (y2 - y1 + 1)
        return total

    def validate_ship_positions(self):
        for idx in range(len(self.ships) - 1):
            # Check if ship hasn't been placed yet.
            if self.ships[idx][0] == -1:
                return False
            x1, y1, x2, y2 = self.ships[idx]
            for idx2 in range(idx + 1, len(self.ships)):
                # Check if other ship hasn't been placed yet.
                if self.ships[idx2][0] == -1:
                    return False
                sx1, sy1, sx2, sy2 = self.ships[idx2]
                # If the ships overlap, the placement isn't valid.
                if not (x2 < sx1 or sx2 < x1 or y2 < sy1 or sy2 < y1):
                    return False
        # If we made it here, then all ship placements are valid.
        return True

    def _position_ship(self, length):
        vertical = random.choice([True, False])
        if vertical:
            x1 = random.randint(0, self.width - 1)
            y1 = random.randint(0, self.height - length)
            x2 = x1
            y2 = y1 + length - 1
        else:
            x1 = random.randint(0, self.width - length)
            y1 = random.randint(0, self.height - 1)
            x2 = x1 + length - 1
            y2 = y1
        return [x1, y1, x2, y2]

    def _intersects_any(self, rect):
        x1, y1, x2, y2 = rect
        for ship in self.ships:
            sx1, sy1, sx2, sy2 = ship
            # Check overlap
            if not (x2 < sx1 or sx2 < x1 or y2 < sy1 or sy2 < y1):
                return True
        return False

    def randomly_position_ships(self, lengths):
        self.ships = []
        for length in lengths:
            while True:
                rect = self._position_ship(length)
                if not self._intersects_any(rect):
                    self.ships.append(rect)
                    break


class Game:
    """
    Manages the overall gameplay including the initialization of the game state,
    handling player and enemy interactions, and determining game outcomes such
    as victory or defeat. The class is responsible for managing game flow,
    state transitions, and communication with any event manager for signaling
    real-time updates.

    :ivar state: Current state of the game, determining which player's turn it is or if the game has finished.
    :type state: State
    :ivar player_board: Board representing the player's grid and ship positions.
    :type player_board: Board
    :ivar enemy_board: Board representing the enemy's grid and ship positions.
    :type enemy_board: Board
    """
    def __init__(self):
        self.state = State.GAME_FINISHED
        self.player_board = Board()
        self.enemy_board = Board()

        Event.event_manager.ship_moved.connect(self.player_board.move_ship)

    def change_state(self, state):
        self.state = state
        Event.event_manager.state_changed.emit(state)

    def new_game(self):
        self.player_board.reset()
        self.enemy_board.reset()
        self.change_state(State.PLACEMENT)

    def start_game(self):
        self._generate_cpu_ships()
        self.change_state(State.PLAYER_TURN)

    def player_move(self, x, y):
        if (self.state != State.PLAYER_TURN or
                not self._valid_move(x, y, self.enemy_board.hits, self.enemy_board.misses)):
            return False
        if self.enemy_board.is_hit(x, y):
            Event.event_manager.player_hit.emit(x, y)
            self.enemy_board.hits.append((x, y))
            if self._check_victory(self.enemy_board, self.enemy_board.hits):
                Event.event_manager.victory.emit()
                self.change_state(State.GAME_FINISHED)
                return True
            else:
                self.change_state(State.ENEMY_TURN)
        else:
            Event.event_manager.player_miss.emit(x, y)
            self.enemy_board.misses.append((x, y))
            self.change_state(State.ENEMY_TURN)
        return True

    def enemy_move(self, x, y):
        if self.state != State.ENEMY_TURN or not self._valid_move(x, y, self.player_board.hits, self.player_board.misses):
            return False
        if self.player_board.is_hit(x, y):
            Event.event_manager.enemy_hit.emit(x, y)
            self.player_board.hits.append((x, y))
            if self._check_victory(self.player_board, self.player_board.hits):
                Event.event_manager.defeat.emit()
                self.change_state(State.GAME_FINISHED)
                return True
            else:
                self.change_state(State.PLAYER_TURN)
        else:
            Event.event_manager.enemy_miss.emit(x, y)
            self.player_board.misses.append((x, y))
            self.change_state(State.PLAYER_TURN)
        return True

    def _valid_move(self, x, y, hits, misses):
        return (x, y) not in hits and (x, y) not in misses and 0 <= x < 10 and 0 <= y < 10

    def _check_victory(self, board, hits):
        return len(hits) == board.total_ship_cells()

    def validate_player_placement(self):
        return self.player_board.validate_ship_positions()

    def _generate_cpu_ships(self):
        lengths = [2, 3, 3, 4, 5]
        self.enemy_board.randomly_position_ships(lengths)
