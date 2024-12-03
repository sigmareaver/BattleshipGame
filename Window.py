"""
-------------------------------------------------------------------------------
Battleship Game - Main Window Interface
-------------------------------------------------------------------------------

File Name: Window.py

Description:
    This file contains the implementation of the main window for a Battleship
    game using PyQt6. It manages the graphical user interface components, game
    setup, and user interactions. It handles game logic, including starting new
    games, managing player and enemy grids, and updating the UI based on
    game states.

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

import random
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QGroupBox, QFormLayout, QLabel
)

import Event, Data, Globals
from NativeEventHandler import CustomKeyEvent
from Board import BattleshipView, BattleshipScene
from Ship import ShipListWidget
from Game import Game, State


class BattleshipWindow(QMainWindow):
    """
    The BattleshipWindow class represents the main window interface for a battleship
    game. It manages the graphical user interface components, game setup, and user
    interactions. This class integrates various Qt widgets and layouts to organize
    the game view and controls. It supports managing the player's and enemy's game
    grids, sidebar controls, and statistics display. The class handles GUI events
    and connects them with game logic to facilitate gameplay, such as starting a new
    game, responding to player actions, and updating the display based on game state
    changes.

    :ivar grids_layout: Holds the layout for both the enemy and player views.
    :type grids_layout: QVBoxLayout
    :ivar enemy_view: The visual component representing the enemy's game board.
    :type enemy_view: BattleshipView
    :ivar enemy_scene: The scene representing the enemy game grid.
    :type enemy_scene: BattleshipScene
    :ivar player_view: The visual component representing the player's game board.
    :type player_view: BattleshipView
    :ivar player_scene: The scene representing the player game grid.
    :type player_scene: BattleshipScene
    :ivar game: Represents the game logic and state management.
    :type game: Game
    """
    def __init__(self):
        super().__init__()

        # Qt UI elements
        self.grids_layout = None
        self.enemy_view = None
        self.enemy_scene = None
        self.player_view = None
        self.player_scene = None

        # Game elements
        self.game = None

        # Build the GUI
        self.setupUi()

        # Setup the game
        self.setupGame()

        # Connect signals
        self.connectSignals()

    def setupUi(self):
        self.setWindowTitle("Battleship Game")

        # Set the size of the window
        self.setFixedSize(600, 800)

        # Main container widget
        main_widget = QWidget()
        main_widget.setContentsMargins(1, 1, 1, 1)
        self.setCentralWidget(main_widget)

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(1)
        main_widget.setLayout(main_layout)
        main_widget.setAcceptDrops(True)
        main_widget.dragEnterEvent = self.dragEnterEvent
        main_widget.dropEvent = self.dropEvent

        # Left-side container widget for both grids
        grids_widget = QWidget()
        grids_widget.setContentsMargins(1, 1, 1, 1)
        self.grids_layout = QVBoxLayout()  # Use QVBoxLayout to stack grids vertically
        self.grids_layout.setContentsMargins(1, 1, 1, 1)
        self.grids_layout.setSpacing(5)
        grids_widget.setLayout(self.grids_layout)
        grids_widget.setAcceptDrops(True)
        grids_widget.dragEnterEvent = self.dragEnterEvent
        grids_widget.dropEvent = self.dropEvent

        # Enemy board
        self.enemy_scene = BattleshipScene(background_image_path ="res/ocean_tile.png")
        self.enemy_view = BattleshipView(self.enemy_scene)
        self.enemy_view.setStyleSheet("border: 2px solid")
        self.grids_layout.addWidget(self.enemy_view)

        # Player board
        self.player_scene = BattleshipScene(background_image_path ="res/ocean_tile.png")
        self.player_view = BattleshipView(self.player_scene, accept_drops=True)
        self.player_view.setStyleSheet("border: 2px solid")
        self.grids_layout.addWidget(self.player_view)

        main_layout.addWidget(grids_widget)

        # Sidebar container widget
        sidebar_widget = QWidget()
        #sidebar_widget.setStyleSheet("border: 1px solid")
        # def get_grid_item_stylesheet(self) -> str:
        #     return """
        #     QFrame {
        #         background-color: rgba(255, 255, 255, 150);  /* Translucent white */
        #         border: 1px solid rgba(0, 0, 0, 50); /* Semi-translucent dark border */
        #     }
        #     """
        sidebar_layout = QVBoxLayout()
        sidebar_widget.setLayout(sidebar_layout)
        sidebar_widget.setFixedWidth(200)
        sidebar_widget.setAcceptDrops(True)
        sidebar_widget.dragEnterEvent = self.dragEnterEvent
        sidebar_widget.dropEvent = self.dropEvent

        # Sidebar - Game Controls
        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_container.setLayout(button_layout)
        self.new_game = QPushButton("New Game")
        button_layout.addWidget(self.new_game)
        self.start_game = QPushButton("Begin!")
        self.start_game.setEnabled(False)
        button_layout.addWidget(self.start_game)
        sidebar_layout.addWidget(button_container)

        # Sidebar - Game Stats
        stats_container = QGroupBox("Game Info")
        form_layout = QFormLayout()
        self.wins = QLabel(str(int(Data.data.value("Wins") or 0)))
        form_layout.addRow("Wins:", self.wins)
        self.losses = QLabel(str(int(Data.data.value("Losses") or 0)))
        form_layout.addRow("Losses:", self.losses)
        stats_container.setLayout(form_layout)
        sidebar_layout.addWidget(stats_container)

        # Add sidebar widget to the main layout
        main_layout.addWidget(sidebar_widget)

        # Create draggable ship items
        ships_widget = ShipListWidget()
        sidebar_layout.addWidget(ships_widget)

    def setupGame(self):
        self.game = Game()

    def connectSignals(self):
        # Connect widget signals
        self.new_game.clicked.connect(self.game.new_game)
        self.start_game.clicked.connect(self.game.start_game)
        self.enemy_view.board_clicked.connect(self.enemy_board_clicked)

        # Connect board signals
        Event.event_manager.player_hit.connect(self.enemy_scene.add_hit)
        Event.event_manager.player_miss.connect(self.enemy_scene.add_miss)
        Event.event_manager.enemy_hit.connect(self.player_scene.add_hit)
        Event.event_manager.enemy_miss.connect(self.player_scene.add_miss)

        # Connect window (self) signals
        Event.event_manager.state_changed.connect(self.state_changed)
        Event.event_manager.ship_moved.connect(self.ship_moved)
        Event.event_manager.victory.connect(self.victory)
        Event.event_manager.defeat.connect(self.defeat)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        # Resize grids to fit available space while maintaining a 1:1 aspect ratio
        area = self.grids_layout.contentsRect()

        new_size = min(area.width(), area.height() // 2)

        self.player_view.setFixedSize(new_size, new_size)
        self.player_scene.resize_grid(new_size)

        self.enemy_view.setFixedSize(new_size, new_size)
        self.enemy_scene.resize_grid(new_size)

    def customEvent(self, event):
        if event.type() == CustomKeyEvent.CustomEventType:
            key = event.key()
            if key == 'r':
                if Globals.selected_ship is not None:
                    Globals.selected_ship.rotate()

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        if Globals.selected_ship is not None:
            Globals.selected_ship = None

    def state_changed(self, state):
        if state == State.PLACEMENT:
            self.new_game.setEnabled(False)
            self.start_game.setEnabled(False)
        else:
            self.new_game.setEnabled(True)
            self.start_game.setEnabled(False)

        if state == State.ENEMY_TURN:
            while not self.game.enemy_move(random.randrange(0, 10), random.randrange(0, 10)):
                continue

    def ship_moved(self, idx, rect, vertical):
        if self.game.state == State.PLACEMENT and self.game.validate_player_placement():
            self.start_game.setEnabled(True)
        else:
            self.start_game.setEnabled(False)

    def enemy_board_clicked(self, x, y):
        if self.game.state == State.PLAYER_TURN and self.game.player_move(x, y):
            self.enemy_view.add_attack(x, y)

    def victory(self):
        QMessageBox.information(self, "Victory", "Congratulations! You have won the game!")
        Data.data.setValue("Wins", int(Data.data.value("Wins") or 0) + 1)
        self.wins.setText(str(int(Data.data.value("Wins") or 0)))

    def defeat(self):
        QMessageBox.information(self, "Defeat", "Oh no! You have lost the game. Better luck next time!")
        Data.data.setValue("Losses", int(Data.data.value("Losses") or 0) + 1)
        self.losses.setText(str(int(Data.data.value("Losses") or 0)))
