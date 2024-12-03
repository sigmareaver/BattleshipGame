"""
-------------------------------------------------------------------------------
Battleship Game - Ship Graphics and Interaction
-------------------------------------------------------------------------------

File Name: Ship.py

Description:
    This file provides classes for the graphical and interactive representation
    of ships within the Battleship game. It includes functionality for visualizing
    ships on a grid, enabling drag-and-drop interactions, and updating ship
    states in response to user input. The implementation uses PyQt6 to handle
    rendering and event management, allowing ships to be positioned and
    manipulated as part of the game's visual interface.

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

from PyQt6.QtWidgets import (
    QGraphicsItem, QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QLabel,
    QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsItemGroup, QApplication
)
from PyQt6.QtCore import Qt, QSize, QMimeData, QRect
from PyQt6.QtGui import QPixmap, QDrag, QPen

import Globals, Event
from Game import State

class ShipGraphicsItem(QGraphicsItemGroup):
    """
    Represents a graphical item that visualizes a ship in a grid-based scene
    for interactive manipulation such as dragging and rotating.

    The `ShipGraphicsItem` class is a custom graphics item that extends the
    QGraphicsItemGroup to allow ship components combining multiple visualizations,
    specifically a rectangle and a pixmap, to behave as a single interactive unit.
    The class supports features like drag-and-drop positioning within a scene grid
    and rotation of the ship, updating the visualization accordingly. It
    communicates changes in position or orientation by emitting events for
    integrating the graphical representation with game logic.

    :ivar idx: The index identifier for the ship within a fleet or on a board.
    :vartype idx: int
    :ivar cell_size: The size of a single cell on the grid used to scale the ship's
        visual representation.
    :vartype cell_size: int
    :ivar length: The number of grid cells the ship spans, dictating its visual
        appearance and physical space occupation.
    :vartype length: int
    :ivar image: The image representation of the ship, initially scaled according
        to cell size and ship length.
    :vartype image: QPixmap
    :ivar dragging: A flag indicating whether the ship is currently being dragged
        by the user.
    :vartype dragging: bool
    :ivar orientation: The current orientation angle (in degrees) of the ship used
        for rotation and positioning logic.
    :vartype orientation: int
    """
    def __init__(self, idx, cell_size, length, image):
        super().__init__()

        # Class fields
        self.idx = idx
        self.cell_size = cell_size
        self.length = length
        self.image = image.scaled(int(cell_size), int(cell_size * length))
        self.dragging = False
        self.orientation = 270

        # Group settings
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

        # Rect item
        self.rect_item = QGraphicsRectItem()
        self.rect_item.setPen(QPen(Qt.GlobalColor.green, 3))
        self.rect_item.setRect(-self.cell_size * length / 2, -self.cell_size / 2, self.cell_size * length, self.cell_size)
        #self.rect_item.setRect(0, 0, self.cell_size * length, self.cell_size)
        #self.rect_item.setPos(self.cell_size * length, self.cell_size)
        self.rect_item.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.rect_item.setTransformOriginPoint(self.rect_item.rect().center())
        self.rect_item.show()

        # Pixmap item
        self.pixmap_item = QGraphicsPixmapItem()
        self.pixmap_item.setPixmap(image)
        offset_x = self.pixmap_item.boundingRect().width() / 2
        offset_y = self.pixmap_item.boundingRect().height() / 2
        self.pixmap_item.setPos(-offset_x, -offset_y)
        self.pixmap_item.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.pixmap_item.setTransformOriginPoint(self.pixmap_item.boundingRect().center())
        self.pixmap_item.hide()

        # Add to group
        self.addToGroup(self.rect_item)
        self.addToGroup(self.pixmap_item)

        self.setTransformOriginPoint(self.rect_item.rect().center())
        self.rotate()

    def mousePressEvent(self, event):
        self.dragging = True
        Globals.selected_ship = self
        self.rect_item.setPen(QPen(Qt.GlobalColor.green, 3))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        Globals.selected_ship = None
        self.rect_item.setPen(QPen(Qt.GlobalColor.transparent, 0))
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.dragging:
            pos = self.scenePos()
            half_size = self.cell_size / 2

            # Ship orientation and length handling
            vertical = self.orientation % 180 == 0
            odd = (self.length + 1) % 2 == 0
            offset_x = half_size * (vertical or ((not vertical) and odd))
            offset_y = half_size * ((not vertical) or (odd and vertical))

            # Grid snap
            pos.setX(int((pos.x()) / self.cell_size) * self.cell_size + offset_x)
            pos.setY(int((pos.y()) / self.cell_size) * self.cell_size + offset_y)

            # Scene boundary snap
            rect = self.mapRectToScene(self.rect_item.boundingRect())
            scene_rect = self.scene().sceneRect()
            if rect.left() < scene_rect.x():
                pos.setX(rect.width() / 2)
            elif rect.right() > scene_rect.right() + offset_y: # Todo: Why does offset_y work with x here?
                pos.setX(scene_rect.width() - (rect.width() / 2) + offset_y)
            if rect.top() < scene_rect.y():
                pos.setY(rect.height() / 2)
            elif rect.bottom() > scene_rect.bottom() + offset_x: # Todo: Why does offset_x work with y here?
                pos.setY(scene_rect.height() - (rect.height() / 2) + offset_x)

            # Finalized grid snap and position set
            pos.setX(int((pos.x()) / self.cell_size) * self.cell_size + offset_x)
            pos.setY(int((pos.y()) / self.cell_size) * self.cell_size + offset_y)
            self.setPos(pos)

            # Convert QGraphics scene space to game coordinates (x1, y1, x2, y2) 0-10
            rect = self.rect_item.rect()
            normalized_rect = QRect()

            # This is ugly, but necessary until we find a way to get better rects from Qt.
            if vertical:
                normalized_rect.setX(int(round((rect.y() + pos.x()) / self.cell_size)))
                normalized_rect.setY(int(round((rect.x() + pos.y()) / self.cell_size)))
                normalized_rect.setWidth(int(round((rect.height() // self.cell_size) + normalized_rect.x())))
                normalized_rect.setHeight(int(round((rect.width() // self.cell_size) + normalized_rect.y())))
            else:
                normalized_rect.setX(int(round((rect.x() + pos.x()) / self.cell_size)))
                normalized_rect.setY(int(round((rect.y() + pos.y()) / self.cell_size)))
                normalized_rect.setWidth(int(round((rect.width() // self.cell_size) + normalized_rect.x())))
                normalized_rect.setHeight(int(round((rect.height() // self.cell_size) + normalized_rect.y())))
            Event.event_manager.ship_moved.emit(self.idx, normalized_rect, vertical)

    def rotate(self):
        if self.dragging:
            self.orientation = (self.orientation + 90) % 360
            self.setRotation(90 + self.orientation)
            pos = self.scenePos()
            half_size = self.cell_size / 2
            vertical = self.orientation % 180 == 0
            odd = (self.length + 1) % 2 == 0
            offset_x = half_size * (vertical or ((not vertical) and odd))
            offset_y = half_size * ((not vertical) or (odd and vertical))
            pos.setX(int((pos.x()) / self.cell_size) * self.cell_size + offset_x)
            pos.setY(int((pos.y()) / self.cell_size) * self.cell_size + offset_y)
            self.setPos(pos)
            rect = self.mapRectToScene(self.rect_item.boundingRect())
            scene_rect = self.scene().sceneRect()
            if rect.left() < scene_rect.x():
                pos.setX(rect.width() / 2)
            elif rect.right() > scene_rect.right() + offset_y:
                pos.setX(scene_rect.width() - (rect.width() / 2) + offset_y)
            if rect.top() < scene_rect.y():
                pos.setY(rect.height() / 2)
            elif rect.bottom() > scene_rect.bottom() + offset_x:
                pos.setY(scene_rect.height() - (rect.height() / 2) + offset_x)
            pos.setX(int((pos.x()) / self.cell_size) * self.cell_size + offset_x)
            pos.setY(int((pos.y()) / self.cell_size) * self.cell_size + offset_y)
            self.setPos(pos)
            rect = self.rect_item.rect()
            normalized_rect = QRect()
            if vertical:
                normalized_rect.setX(int(round((rect.y() + pos.x()) / self.cell_size)))
                normalized_rect.setY(int(round((rect.x() + pos.y()) / self.cell_size)))
                normalized_rect.setWidth(int(round((rect.height() // self.cell_size) + normalized_rect.x())))
                normalized_rect.setHeight(int(round((rect.width() // self.cell_size) + normalized_rect.y())))
            else:
                normalized_rect.setX(int(round((rect.x() + pos.x()) / self.cell_size)))
                normalized_rect.setY(int(round((rect.y() + pos.y()) / self.cell_size)))
                normalized_rect.setWidth(int(round((rect.width() // self.cell_size) + normalized_rect.x())))
                normalized_rect.setHeight(int(round((rect.height() // self.cell_size) + normalized_rect.y())))
            Event.event_manager.ship_moved.emit(self.idx, QRect(normalized_rect), vertical)


class ShipWidget(QWidget):
    """
    Represents a graphical user interface element displaying a ship. This class
    is responsible for rendering an image representation of a ship, along with
    handling its associated metadata like its index, size and length. The widget
    uses a vertical box layout to arrange its components.

    :ivar idx: The index of the ship, used to identify it within a collection.
    :type idx: int
    :ivar cell_size: The size of each cell occupied by the ship in the layout.
    :type cell_size: int
    :ivar length: The length of the ship, possibly indicating the number
                  of cells it occupies.
    :type length: int
    """
    def __init__(self, idx, image, cell_size, length):
        super().__init__()

        self.idx = idx
        self.cell_size = cell_size
        self.length = length

        layout = QVBoxLayout()
        self.setLayout(layout)

        image_label = QLabel()
        image_label.setPixmap(image)
        image_label.setFixedSize(int(image.width()), int(image.height()))
        layout.addWidget(image_label)

        # Add some space below the image
        # layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))


class ShipListWidget(QListWidget):
    """
    A widget that represents a list of ship items for a game, allowing users to drag and
    place ships during a placement phase. This widget is primarily designed for use within
    a larger game's graphical user interface.

    This class provides a graphical list of ship items, each with an image representing
    a different type of ship. It handles the drag-and-drop functionality to allow users
    to position ships within a game. The class interacts with an event management system
    to update its state based on game phases. This widget is initially disabled and can be
    enabled during the ship placement phase.

    :ivar cell_size: The size of each cell in the grid used for ship placement.
    :vartype cell_size: int
    :ivar lengths: A list describing the lengths of different ships available in the game.
    :vartype lengths: list of int
    :ivar image_paths: Paths to the image files used to represent each ship type.
    :vartype image_paths: list of str
    :ivar images: Cached QPixmap objects created from the image paths, scaled to appropriate sizes.
    :vartype images: list of QPixmap
    :ivar dragged_item: Temporary storage for the currently dragged QListWidgetItem.
    :vartype dragged_item: QListWidgetItem or None
    :ivar dragged_item_widget: The widget for the ship currently being dragged.
    :vartype dragged_item_widget: ShipWidget or None
    """
    dragged_item_widget = ShipWidget or None

    def __init__(self):
        super().__init__()
        # Ship settings
        self.cell_size = 33
        self.lengths = [2, 3, 3, 4, 5]
        self.image_paths = [
            "gunboat.png",
            "destroyer.png",
            "submarine.png",
            "battleship.png",
            "carrier.png"
        ]
        self.images = [
            QPixmap("res/" + path).scaled(length * self.cell_size, self.cell_size, Qt.AspectRatioMode.KeepAspectRatio)
            for length, path in zip(self.lengths, self.image_paths)
        ]

        # Qt widget setup
        self.setDragEnabled(True)
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setIconSize(QSize(50, 50))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFixedHeight(len(self.lengths) * (self.cell_size + 15))
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)
        self.dragged_item_widget = None
        self.dragged_item = None

        self.setEnabled(False)

        Event.event_manager.state_changed.connect(self.state_changed)

    def start_placement_phase(self):
        self.setEnabled(True)
        self.clear()
        self.init_items()

    def end_placement_phase(self):
        self.setEnabled(False)
        self.clear()

    def state_changed(self, state):
        if state == State.PLACEMENT:
            self.start_placement_phase()
        elif self.isEnabled():
            self.end_placement_phase()

    def init_items(self):
        for idx in range(len(self.lengths)):
            # Create a custom widget with an image of a ship
            item_widget = ShipWidget(idx, self.images[idx], self.cell_size, self.lengths[idx])

            # Add item to list
            item = QListWidgetItem(self)
            item.setSizeHint(item_widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, item_widget)

    def startDrag(self, event):
        self.dragged_item_index = self.currentRow()
        self.dragged_item = self.currentItem()
        self.dragged_ship = self.itemWidget(self.dragged_item)
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText("ship")
        mime_data.setProperty("index", self.dragged_ship.idx)
        mime_data.setProperty("cell_size", self.dragged_ship.cell_size)
        mime_data.setProperty("length", self.dragged_ship.length)
        mime_data.setProperty("image", self.images[self.dragged_ship.idx])
        drag.setMimeData(mime_data)

        drag.setPixmap(self.images[self.dragged_ship.idx])

        self.takeItem(self.row(self.dragged_item))
        if drag.exec(Qt.DropAction.MoveAction) != Qt.DropAction.MoveAction:
            # If the drop action isn't accepted, put the item back
            idx = drag.mimeData().property("index")
            restored_ship = ShipWidget(idx, self.images[idx],
                                       self.cell_size, self.lengths[idx])
            restored_item = QListWidgetItem()
            restored_item.setSizeHint(restored_ship.sizeHint())
            #self.addItem(restored_item)
            self.insertItem(self.dragged_item_index, restored_item)
            self.setItemWidget(restored_item, restored_ship)
            self.setCurrentRow(self.dragged_item_index)

        self.dragged_item = None
        self.dragged_item_widget = None
