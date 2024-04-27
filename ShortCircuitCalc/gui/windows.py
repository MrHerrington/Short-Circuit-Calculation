# -*- coding: utf-8 -*-
"""The module contains GUI windows templates, using PyQt5 and Matplotlib.
Classes are based on ui files, developed by QtDesigner and customized."""


import typing as ty
import matplotlib
# Need for figure matplotlib annotation
# noinspection PyUnresolvedReferences
import matplotlib.pyplot as plt
# Need for correctly loading icons
# noinspection PyUnresolvedReferences
import ShortCircuitCalc.gui.resources
from ..config import GUI_DIR

from PyQt5 import QtWidgets, QtCore, QtGui, uic

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigCanvas,
    NavigationToolbar2QT as NavToolbar,
)


__all__ = ('CustomGraphicView', 'ViewerWidget')


# Select the backend used for rendering and GUI integration.
matplotlib.use('Qt5Agg')


class CustomGraphicView(QtWidgets.QGraphicsView):
    """Initializes a CustomGraphicView object.

    Args:
        parent (Optional[QtWidgets.QWidget], optional): The parent widget for the CustomGraphicView.
        Defaults to None.

    Initializes the following instance variables:
        - _scene (QtWidgets.QGraphicsScene): The graphics scene for the CustomGraphicView.
        - _canvas (FigCanvas): The Matplotlib figure canvas for the CustomGraphicView.
        - _zoom (int): The current zoom level of the CustomGraphicView.
        - _mousePressed (bool): Flag indicating whether the mouse is currently pressed.
        - _drag_pos (Optional[QtCore.QPoint]): The position of the mouse during a drag operation.

    Sets the graphics scene, canvas, transformation anchor, and resize anchor for the CustomGraphicView.

    """

    def __init__(self,
                 parent: ty.Optional[QtWidgets.QWidget] = None,
                 figure: matplotlib.figure.Figure = None,
                 title: str = 'Viewer') -> None:
        super(CustomGraphicView, self).__init__(parent)

        self._title = title
        self._figure = figure
        self._scene = QtWidgets.QGraphicsScene()

        if parent is not None:
            self._figure = self.parent()._figure

        self._canvas = FigCanvas(self._figure)
        self._scene.addWidget(self._canvas)

        self.setWindowTitle(self._title)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        # Start viewing position
        self.horizontalScrollBar().setSliderPosition(1)
        self.verticalScrollBar().setSliderPosition(1)

        self._zoom = 0
        self._mousePressed = False
        self._drag_pos = None

        self.save_model_action = QtWidgets.QAction(QtGui.QIcon(':/icons/resources/icons/file_save.svg'),
                                                   'Save model as ...', self)
        self.save_model_action.setIconVisibleInMenu(True)
        self.save_model_action.triggered.connect(self.save_model)

        self.save_fragment_action = QtWidgets.QAction(QtGui.QIcon(':/icons/resources/icons/save_part.svg'),
                                                      'Save fragment as ...', self)
        self.save_fragment_action.setIconVisibleInMenu(True)
        self.save_fragment_action.triggered.connect(self.save_fragment)

    def mousePressEvent(self, event: QtCore.Qt.MouseButton.LeftButton) -> None:
        """Handle the mouse press event.

        Args:
            event (QtCore.Qt.MouseButton.LeftButton): The mouse press event.

        """
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._mousePressed = True
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))
            self._drag_pos = event.pos()
            event.accept()

        else:
            super(CustomGraphicView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event: QtCore.Qt.MouseButton.LeftButton) -> None:
        """Handle the mouse move event.

        Args:
            event (QtCore.Qt.MouseButton.LeftButton): The mouse move event.


        This function is called when the mouse is moved while the left button is pressed.
        It calculates the difference between the current mouse position and the previous
        mouse position and updates the scrollbars accordingly.

        """
        if self._mousePressed:
            new_pos = event.pos()
            diff = new_pos - self._drag_pos
            self._drag_pos = new_pos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - diff.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - diff.y())
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))

        else:
            super(CustomGraphicView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtCore.Qt.MouseButton.LeftButton) -> None:
        """Handle the mouse release event.

        Args:
            event (QtCore.Qt.MouseButton.LeftButton): The mouse release event.

        This function is called when the mouse button is released. It checks if the released
        button is the left button. If it is, it sets the '_mousePressed' flag to 'False' and
        changes the cursor to an arrow cursor. Finally, it calls the 'mouseReleaseEvent' method
        of the parent class with the given event.

        """
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._mousePressed = False
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))

        super(CustomGraphicView, self).mouseReleaseEvent(event)

    def wheelEvent(self, event: QtCore.Qt.KeyboardModifier.ControlModifier) -> None:
        """Handle the wheel event.

        Args:
            event (QtCore.Qt.KeyboardModifier.ControlModifier): The wheel event.

        This function is called when the user scrolls the mouse wheel. It checks if the Control
        modifier key is pressed and adjusts the zoom level accordingly. If the zoom level is
        greater than 0, it scales the view by a factor of 1.25 or 0.8 depending on the scroll
        direction. If the zoom level is 0, it resets the view transformation. If the Control
        modifier key is not pressed, it calls the parent class's wheelEvent method with the
        given event.

        """
        modifiers = QtWidgets.QApplication.keyboardModifiers()

        if modifiers == QtCore.Qt.KeyboardModifier.ControlModifier:

            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1

            if self._zoom > 0:
                self.scale(factor, factor)
            else:
                self._zoom = 0
                self.resetTransform()

        else:
            super(CustomGraphicView, self).wheelEvent(event)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.save_model_action)
        separator = QtWidgets.QAction(self)
        separator.setSeparator(True)
        menu.addAction(separator)
        menu.addAction(self.save_fragment_action)
        menu.exec(event.globalPos())

    def save_model(self):
        """Saves the current figure as an any graphical file."""
        NavToolbar.save_figure(self._figure)

    def save_fragment(self):
        """Saves the current visible area widget as an image.

        Note:
            Saves the current visible area as an image without the scrollbars.

        """
        rect_region = QtCore.QRect(0, 0,
                                   self.width() - self.verticalScrollBar().width(),
                                   self.height() - self.horizontalScrollBar().height())
        pixmap = self.grab(rect_region)
        fname = QtWidgets.QFileDialog.getSaveFileName(self, 'Save fragment as ...', 'image.png',
                                                      'Portable Network Graphics (*.png);;'
                                                      'Joint Photographic Experts Group (*.jpeg *.jpg)')[0]
        if fname:
            pixmap.save(fname)


class ViewerWidget(QtWidgets.QWidget):
    """Initializes a ViewerWidget object.

    ViewerWidget is a QWidget that displays a matplotlib figure in a QGraphicsView widget.
    Also allows saving the figure as any graphical format or saving part of the figure as an image.

    Args:
        title (str): The title of the viewer widget.
        figure (Optional[matplotlib.figure.Figure]): The matplotlib figure to display.

    """

    def __init__(self,
                 figure: ty.Optional[matplotlib.figure.Figure],
                 title: str = 'Viewer Window') -> None:
        super(ViewerWidget, self).__init__()
        # self._figure definition before loadUi is necessarily!
        self._figure = figure
        uic.loadUi(GUI_DIR / 'viewer.ui', self)
        self.setWindowTitle(title)

        # self.allButton.setToolTip('Save whole page')
        # self.allButton.clicked.connect(self.save_model)
        #
        # self.partButton.setToolTip('Save part of page')
        # self.partButton.clicked.connect(self.save_fragment)
