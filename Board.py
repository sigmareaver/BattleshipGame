"""
-------------------------------------------------------------------------------
Battleship Game - Board Graphics and Interaction
-------------------------------------------------------------------------------

File Name: Board.py

Description:
    This file provides the graphical components and user interaction mechanisms
    for the Battleship game's board. It includes the implementation of a scene
    representing the game grid and a view to facilitate user interactions with
    the board. The classes within manage rendering of the grid, handling user
    inputs such as clicks and drags for ship placement, and reflecting game
    events such as hits and misses on the board.

Author: sigmareaver
Date Created: 11/26/2024

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

from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsLineItem, QGraphicsPixmapItem
from PyQt6.QtGui import QBrush, QPixmap, QPen
from PyQt6.QtCore import Qt, QRect, pyqtSignal

from Ship import ShipGraphicsItem
import Globals, Event
from Game import State

class BattleshipScene(QGraphicsScene):
    """
    Represents a graphical scene for a Battleship game, managing the display of
    a grid and the placement of hit and miss markers within the grid.

    The BattleshipScene is designed to be used as part of a graphical user
    interface for a Battleship game. It draws a grid representing the game
    board, allows resizing of the grid, and manages the rendering of visual
    indicators for hits and misses on the game board. The background can be
    customized with an image, and the grid is initially drawn with a specified
    number of cells.

    :ivar cell_count: The number of cells in the grid along one dimension.
    :type cell_count: int
    :ivar cell_size: The size of each cell in pixels.
    :type cell_size: int
    :ivar pen: The pen used to draw grid lines.
    :type pen: QPen
    :ivar hit_pixmap: The pixmap used to represent a hit on the grid.
    :type hit_pixmap: QPixmap
    :ivar miss_pixmap: The pixmap used to represent a miss on the grid.
    :type miss_pixmap: QPixmap
    """
    def __init__(self, background_image_path, cell_count=10, parent=None):
        super().__init__(parent)

        self.cell_count = cell_count
        self.cell_size = 50
        self.pen = QPen(Qt.GlobalColor.gray, 1)
        self.hit_pixmap = QPixmap("res/hit.png")
        self.miss_pixmap = QPixmap("res/miss.png")

        # Set the background image
        if background_image_path:
            pixmap = QPixmap(background_image_path)
            self.setBackgroundBrush(QBrush(pixmap))

        self.draw_grid()

    def draw_grid(self):
        self.clear()
        for count in range(self.cell_count):
            v_line = QGraphicsLineItem(count * self.cell_size, 0,
                                      count * self.cell_size, self.cell_count * self.cell_size)
            h_line = QGraphicsLineItem(0, count * self.cell_size,
                                      self.cell_count * self.cell_size, count * self.cell_size)
            v_line.setPen(self.pen)
            h_line.setPen(self.pen)
            self.addItem(v_line)
            self.addItem(h_line)

    def resize_grid(self, new_size):
        self.setSceneRect(0, 0, new_size, new_size)
        self.cell_size = new_size / self.cell_count
        self.clear()
        self.draw_grid()
        self.update()

    def add_hit(self, x, y):
        hit = QGraphicsPixmapItem(self.hit_pixmap.scaled(int(self.cell_size), int(self.cell_size), Qt.AspectRatioMode.KeepAspectRatio))
        self.addItem(hit)
        hit.setPos(x * self.cell_size, y * self.cell_size)

    def add_miss(self, x, y):
        miss = QGraphicsPixmapItem(self.miss_pixmap.scaled(int(self.cell_size), int(self.cell_size), Qt.AspectRatioMode.KeepAspectRatio))
        self.addItem(miss)
        miss.setPos(x * self.cell_size, y * self.cell_size)


class BattleshipView(QGraphicsView):
    """

    """
    board_clicked = pyqtSignal(int, int)

    def __init__(self, scene, accept_drops=False, parent=None):
        super().__init__(scene, parent)
        self.battleship_scene = scene
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setAcceptDrops(accept_drops)
        #self.setFixedSize(self.scene.cell_count * self.scene.cell_size, self.scene.cell_count * self.scene.cell_size)

        self.dragging_item = None

        Event.event_manager.state_changed.connect(self.state_changed)

    def resizeEvent(self, event):
        # Force the widget to maintain a 1:1 aspect ratio
        area = self.parent().contentsRect()
        size = min(area.width(), area.height() // 2)
        self.setFixedSize(size, size)

        # Calculate the size of each grid item based on the widget's size
        self.battleship_scene.resize_grid(size)
        self.update()

    def mousePressEvent(self, event):
        pos = self.mapToScene(event.pos())
        x, y = int(pos.x() // self.battleship_scene.cell_size), int(pos.y() // self.battleship_scene.cell_size)
        self.board_clicked.emit(x, y)
        super().mousePressEvent(event)

    def dragEnterEvent(self, event):
        if self.acceptDrops() and event.mimeData().hasText():
            event.acceptProposedAction()
            idx = event.mimeData().property("index")
            length = event.mimeData().property("length")
            image = event.mimeData().property("image")
            self.dragging_item = ShipGraphicsItem(idx, self.battleship_scene.cell_size, length, image)
            Globals.selected_ship = self.dragging_item
            self.dragging_item.dragging = True
            self.dragging_item.pixmap_item.hide()
            self.dragging_item.rect_item.setPen(QPen(Qt.GlobalColor.green, 3))
            self.scene().addItem(self.dragging_item)

    def dragMoveEvent(self, event):
        if self.dragging_item:
            cell_size = self.battleship_scene.cell_size
            half_size = cell_size / 2
            vertical = self.dragging_item.orientation % 180 == 0
            odd = (self.dragging_item.length + 1) % 2 == 0
            offset_x = half_size * (vertical or ((not vertical) and odd))
            offset_y = half_size * ((not vertical) or (odd and vertical))
            pos = self.mapToScene(event.position().toPoint())
            pos.setX(int((pos.x()) / cell_size) * cell_size + offset_x)
            pos.setY(int((pos.y()) / cell_size) * cell_size + offset_y)
            self.dragging_item.setPos(pos)
            rect = self.dragging_item.mapRectToScene(self.dragging_item.rect_item.boundingRect())
            scene_rect = self.scene().sceneRect()
            if rect.left() < scene_rect.x():
                pos.setX(rect.width() / 2)
            elif rect.right() > scene_rect.right() + offset_y:
                pos.setX(scene_rect.width() - (rect.width() / 2) + offset_y)
            if rect.top() < scene_rect.y():
                pos.setY(rect.height() / 2)
            elif rect.bottom() > scene_rect.bottom() + offset_x:
                pos.setY(scene_rect.height() - (rect.height() / 2) + offset_x)
            pos.setX(int((pos.x()) / cell_size) * cell_size + offset_x)
            pos.setY(int((pos.y()) / cell_size) * cell_size + offset_y)
            self.dragging_item.setPos(pos)
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        if self.dragging_item:
            self.scene().removeItem(self.dragging_item)
            self.dragging_item = None
            globals.selected_ship = None
            event.accept()

    def dropEvent(self, event):
        if self.dragging_item:
            cell_size = self.battleship_scene.cell_size
            half_size = cell_size / 2
            vertical = self.dragging_item.orientation % 180 == 0
            odd = (self.dragging_item.length + 1) % 2 == 0
            offset_x = half_size * (vertical or ((not vertical) and odd))
            offset_y = half_size * ((not vertical) or (odd and vertical))
            pos = self.mapToScene(event.position().toPoint())
            pos.setX(int(pos.x() / cell_size) * cell_size + offset_x)
            pos.setY(int(pos.y() / cell_size) * cell_size + offset_y)
            self.dragging_item.setPos(pos)
            rect = self.dragging_item.mapRectToScene(self.dragging_item.rect_item.boundingRect())
            scene_rect = self.scene().sceneRect()
            if rect.left() < scene_rect.x():
                pos.setX(rect.width() / 2)
            elif rect.right() > scene_rect.right() + offset_y:
                pos.setX(scene_rect.width() - (rect.width() / 2) + offset_y)
            if rect.top() < scene_rect.y():
                pos.setY(rect.height() / 2)
            elif rect.bottom() > scene_rect.bottom() + offset_x:
                pos.setY(scene_rect.height() - (rect.height() / 2) + offset_x)
            pos.setX(int((pos.x()) / cell_size) * cell_size + offset_x)
            pos.setY(int((pos.y()) / cell_size) * cell_size + offset_y)
            self.dragging_item.setPos(pos)
            rect = self.dragging_item.rect_item.rect()
            normalized_rect = QRect()
            if vertical:
                normalized_rect.setX(int(round((rect.y() + pos.x()) / cell_size)))
                normalized_rect.setY(int(round((rect.x() + pos.y()) / cell_size)))
                normalized_rect.setWidth(int(round((rect.height() // cell_size) + normalized_rect.x())))
                normalized_rect.setHeight(int(round((rect.width() // cell_size) + normalized_rect.y())))
            else:
                normalized_rect.setX(int(round((rect.x() + pos.x()) / cell_size)))
                normalized_rect.setY(int(round((rect.y() + pos.y()) / cell_size)))
                normalized_rect.setWidth(int(round((rect.width() // cell_size) + normalized_rect.x())))
                normalized_rect.setHeight(int(round((rect.height() // cell_size) + normalized_rect.y())))
            Event.event_manager.ship_moved.emit(self.dragging_item.idx, normalized_rect, vertical)
            self.dragging_item.dragging = False
            self.dragging_item.pixmap_item.show()
            self.dragging_item.rect_item.setPen(QPen(Qt.GlobalColor.transparent, 0))
            self.dragging_item = None
            Globals.selected_ship = None
            event.acceptProposedAction()
        else:
            event.ignore()

    def add_attack(self, x, y):
        pass

    def state_changed(self, state):
        if state == State.PLACEMENT:
            self.battleship_scene.clear()
            self.battleship_scene.draw_grid()
