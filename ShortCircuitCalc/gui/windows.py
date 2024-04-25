# -*- coding: utf-8 -*-
"""The module contains at the moment the ScrollableWindow class, which is
used to display figures in a scrollable window using PyQt5 and Matplotlib.
The class provides methods for initializing the GUI, setting basic window
information, and displaying the window."""


import sys
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


__all__ = ('ViewerWindow', 'PhotoViewer')


# Select the backend used for rendering and GUI integration.
matplotlib.use('Qt5Agg')


class PhotoViewer(QtWidgets.QGraphicsView):
    def __init__(self, figure):
        super(PhotoViewer, self).__init__()
        self.figure = figure
        self._zoom = 0
        self._scene = QtWidgets.QGraphicsScene()
        self._scene.addWidget(FigCanvas(self.figure))
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self._mousePressed = False

    def mousePressEvent(self,  event):
        if event.button() == QtCore.Qt.LeftButton:
            self._mousePressed = True
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))
            self._dragPos = event.pos()
            event.accept()
        else:
            super(PhotoViewer, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._mousePressed:
            newPos = event.pos()
            diff = newPos - self._dragPos
            self._dragPos = newPos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - diff.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - diff.y())
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))
        else:
            super(PhotoViewer, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._mousePressed = False
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        super(PhotoViewer, self).mouseReleaseEvent(event)

    def wheelEvent(self, event):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
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
            super(PhotoViewer, self).wheelEvent(event)


class ViewerWindow(QtWidgets.QWidget):
    def __init__(self, title='Viewer', figure: matplotlib.figure.Figure = None):
        super(ViewerWindow, self).__init__()
        uic.loadUi(GUI_DIR / 'viewer.ui', self)
        self.setWindowTitle(title)
        self.figure = figure
        new_exemplar = PhotoViewer(self.figure)
        old = self.findChildren(QtWidgets.QGraphicsView)[0]
        old.setParent(None)
        self.layout().addWidget(new_exemplar)
