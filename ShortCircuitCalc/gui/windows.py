# -*- coding: utf-8 -*-
"""The module contains GUI windows templates, using PyQt5 and Matplotlib.
Classes are based on ui files, developed by QtDesigner and customized."""


import matplotlib
# Need for figure matplotlib annotation
# noinspection PyUnresolvedReferences
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigCanvas,
    NavigationToolbar2QT as NavToolbar,
)
from PyQt5 import QtWidgets, QtCore, QtGui, uic

# Need for correctly loading icons
# noinspection PyUnresolvedReferences
import ShortCircuitCalc.gui.resources
from ShortCircuitCalc.gui.info_catalog import *
from ShortCircuitCalc.config import GUI_DIR


__all__ = ('MainWindow', 'ConfirmWindow', 'CustomGraphicView')


# Select the backend used for rendering and GUI integration.
matplotlib.use('Qt5Agg')


class CustomGraphicView(QtWidgets.QGraphicsView):
    """Initializes a CustomGraphicView object.

    Args:
        parent (Optional[QtWdgets.QWidget], optional): The parent widget for the CustomGraphicView.
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
                 parent: QtWidgets = None,
                 figure: matplotlib.figure.Figure = None,
                 title: str = 'Viewer') -> None:
        super(CustomGraphicView, self).__init__(parent)

        self._title = title
        self._figure = figure
        self._scene = QtWidgets.QGraphicsScene()

        if parent is not None:
            self._canvas = None
        else:
            self._canvas = FigCanvas(self._figure)
            self._scene.addWidget(self._canvas)

        self.setScene(self._scene)
        self.setWindowTitle(self._title)
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

    def set_model(self, model):
        self._figure = model
        self._canvas = FigCanvas(self._figure)
        self._scene.addWidget(self._canvas)
        self.setScene(self._scene)

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

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        """Handle the context menu event.

        Args:
            event (QtGui.QContextMenuEvent): The context menu event.

        This function is called when a context menu event is triggered. It creates a context menu
        with actions to save model and save fragment. It then executes the menu at the global position
        specified by the event.

        """
        # Creating context menu
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.save_model_action)

        # Creating / adding separator
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

    """

    def __init__(self, title: str = 'Viewer Window') -> None:
        super(ViewerWidget, self).__init__()
        # self._figure definition before loadUi is necessarily!
        uic.loadUi(GUI_DIR / 'viewer.ui', self)
        self.setWindowTitle(title)

        # self.allButton.setToolTip('Save whole page')
        # self.allButton.clicked.connect(self.save_model)
        #
        # self.partButton.setToolTip('Save part of page')
        # self.partButton.clicked.connect(self.save_fragment)


class ConfirmWindow(QtWidgets.QDialog):
    """Initializes a ConfirmWindow object."""
    def __init__(self, parent=None):
        super(ConfirmWindow, self).__init__(parent)
        uic.loadUi(GUI_DIR / 'confirm.ui', self)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(GUI_DIR / 'main_window.ui', self)

        # Hiding tab bar for QTabWidget
        self.findChild(QtWidgets.QTabBar).hide()

        # Initial start interface
        self.switchButton.setChecked(True)
        self.logsButton.setChecked(True)

        # Buttons config
        self.inputButton.setToolTip('Set input console')
        self.inputButton.clicked.connect(lambda: self.tabWidget.setCurrentIndex(0))

        self.resultButton.setToolTip('Set results view')
        self.resultButton.clicked.connect(lambda: self.tabWidget.setCurrentIndex(1))

        self.catalogButton.setToolTip('Set catalog view')
        self.catalogButton.clicked.connect(lambda: self.tabWidget.setCurrentIndex(2))

        self.logsButton.setToolTip('Set logs terminal')

        self.infoButton.setToolTip('Set info view')
        self.infoButton.clicked.connect(lambda: self.tabWidget.setCurrentIndex(3))

        self.set_info_catalog()
        self.window_auto_center()

    def window_auto_center(self) -> None:
        """Centers the window on the screen."""
        desktop = QtWidgets.QDesktopWidget().screenGeometry()
        screen_width = desktop.width()
        screen_height = desktop.height()
        x = int((screen_width - self.width()) / 2)
        y = int((screen_height - self.height()) / 2)
        self.move(x, y)

    def set_info_catalog(self) -> None:
        self.catalogView.set_model(info_catalog_figure())

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Handle the close event of the window.

        Args:
            event (QtGui.QCloseEvent): The close event object.

        This function is called when the user tries to close the window. It creates a confirmation window
        and displays it to the user. If the user confirms the close action, the event is accepted and the
        window is closed. Otherwise, the event is ignored and the window remains open.

        """
        confirm_window = ConfirmWindow(self)
        confirm_window.exec_()
        if confirm_window.result() == QtWidgets.QDialog.Accepted:
            event.accept()
        else:
            event.ignore()
