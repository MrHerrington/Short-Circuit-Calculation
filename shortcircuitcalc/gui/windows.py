# -*- coding: utf-8 -*-
"""
The module contains GUI windows templates, using PyQt5 and Matplotlib.
Classes are based on ui files, developed by QtDesigner and customized.

Inner functionality:
    - CustomGraphicView: The class initializes a window shows graphical objects.
    - CustomPlainTextEdit: The class initializes a custom text edit with a custom caret.
    - CustomTextEditLogger: The class initializes custom text edit object for logging interface in the GUI.
    - ConfirmWindow: The class initializes custom QDialog object.
    - WindowMixin: The class initializes the mixin for graphic window object.

Custom threads:
    - GraphicsDataThread: The class defines a thread for loading graphics data.
    - TableDataThread: The class defines a thread for loading table data.

App main windows:
    - MainWindow: The class defines the main window of the program.
    - DatabaseBrowser: The class creates database browser window and allows to manage database.

Other functionality:
    - empty.

"""


import sys
import os

from collections import namedtuple
from decimal import Decimal
import typing as ty
from dataclasses import asdict

import logging
import matplotlib
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigCanvas,
    NavigationToolbar2QT as NavToolbar,
)
from PyQt5 import QtWidgets, QtCore, QtGui, uic

# Need for correctly loading icons
import shortcircuitcalc.gui.resources  # noqa
from shortcircuitcalc.gui.figures import ResultsFigure, CatalogFigure
from shortcircuitcalc.database import (
    Transformer, Cable, CurrentBreaker, OtherContact,

    InsertTrans, UpdateTransOldSource, UpdateTransNewSource, UpdateTransRow, DeleteTrans,
    InsertCable, UpdateCableOldSource, UpdateCableNewSource, UpdateCableRow, DeleteCable,
    InsertContact, UpdateContactOldSource, UpdateContactNewSource, UpdateContactRow, DeleteContact,
    InsertResist, UpdateResistOldSource, UpdateResistNewSource, UpdateResistRow, DeleteResist,

    db_install, BT
)
from shortcircuitcalc.tools import config_manager, logging_error, ChainsSystem
from shortcircuitcalc.config import GUI_DIR


__all__ = ('MainWindow', 'DatabaseBrowser', 'CustomGraphicView', 'ConfirmWindow')


# Select the backend used for rendering and GUI integration.
matplotlib.use('Qt5Agg')


logger = logging.getLogger(__name__)
GraphicClass = ty.TypeVar('GraphicClass', bound=ty.Union[ResultsFigure, CatalogFigure])
GraphicWindow = ty.TypeVar('GraphicWindow', bound=ty.Union[QtWidgets.QMainWindow, QtWidgets.QWidget])


#######################
# Inner functionality #
#######################

class CustomGraphicView(QtWidgets.QGraphicsView):
    # noinspection PyUnresolvedReferences
    """
    The class initializes a window shows graphical objects.

    Attributes:
        parent (QtWdgets.QWidget, optional): The parent widget.
        figure (matplotlib.figure.Figure, optional): The Matplotlib figure.
        title (str, optional): The title of the graphic window.

    Interface:
        - supports scrolling, zooming and panning working scene by handling events.
        - set_figure: The method sets the figure to the view scene.
        - save_model: The method saves the current figure as an any graphical file.
        - save_fragment: The method saves the current visible area widget as an image.

    Handling events:
        - mousePressEvent: The method handles mouse press event.
        - mouseMoveEvent: The method handles mouse move event.
        - mouseReleaseEvent: The method handles mouse release event.
        - wheelEvent: The method handles mouse wheel event.
        - contextMenuEvent: The method handles context menu event.

    """

    def __init__(self,
                 parent: QtWidgets = None,
                 figure: matplotlib.figure.Figure = None,
                 title: str = 'Viewer') -> None:
        super(CustomGraphicView, self).__init__(parent)
        self._title = title

        self._figure = figure
        self._canvas = FigCanvas(self._figure)
        self._scene = QtWidgets.QGraphicsScene()

        self._zoom = 0
        self._mousePressed = False
        self._drag_pos = None

        self.save_model_action = QtWidgets.QAction(QtGui.QIcon(':/icons/resources/icons/file_save.svg'),
                                                   'Save model as ...', self)
        self.save_fragment_action = QtWidgets.QAction(QtGui.QIcon(':/icons/resources/icons/save_part.svg'),
                                                      'Save fragment as ...', self)

        self.init_gui()

    def init_gui(self) -> None:
        """
        The method initializes window GUI.

        Definite:
            - Window title
            - Scene settings
            - Anchor settings
            - Context menu actions settings

        """
        # Set title
        self.setWindowTitle(self._title)

        # Scene settings
        self._scene.addWidget(self._canvas)
        self.setScene(self._scene)

        # Anchor settings
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

        # Context menu actions settings
        self.save_model_action.setIconVisibleInMenu(True)
        self.save_model_action.triggered.connect(self.save_model)  # noqa

        self.save_fragment_action.setIconVisibleInMenu(True)
        self.save_fragment_action.triggered.connect(self.save_fragment)  # noqa

    def set_figure(self,
                   figure: matplotlib.figure.Figure,
                   custom_zoom: bool = False
                   ) -> None:
        """
        The method sets the figure to the view scene.

        Args:
            figure (matplotlib.figure.Figure): The Matplotlib figure.
            custom_zoom (bool, optional): The flag for custom zoom, need if fig dpi > default.

        Note:
            Sets start viewing position in top left corner scene.

        """
        self._figure = figure
        self._canvas = FigCanvas(self._figure)
        self._scene = QtWidgets.QGraphicsScene()
        self._scene.addWidget(self._canvas)
        self.setScene(self._scene)

        # Start viewing position
        self.horizontalScrollBar().setSliderPosition(1)
        self.verticalScrollBar().setSliderPosition(1)

        if self.objectName() not in (
                'resultsView',
        ):
            self.setStyleSheet('QGraphicsView {background-color: transparent;}')

        if custom_zoom:
            self.zoom_initialize()

    def zoom_initialize(self) -> None:
        """
        The method sets custom zoom initialization for scene and figure.

        """
        fig_size_x_inches, fig_size_y_inches = self._figure.get_size_inches()
        start_scale = int(min((self.width() / fig_size_x_inches, self.height() / fig_size_y_inches))) * 0.9
        self.scale(1 / start_scale, 1 / start_scale)

    def save_model(self) -> None:
        """
        The method saves the current figure as an any graphical file.

        """
        try:
            if self.parent() is None:
                NavToolbar.save_figure(self._figure)
            else:
                viewers = self.parent().findChildren(QtWidgets.QGraphicsView)
                for viewer in viewers:
                    if viewer == self:
                        NavToolbar.save_figure(viewer._figure)  # noqa

        except (AttributeError,):
            logger.error('Cannot save empty model.')

    def save_fragment(self) -> None:
        """
        The method saves the current visible area widget as an image.

        Note:
            Saves the current visible area as an image without the scrollbars.

        """
        rect_region = QtCore.QRect(0, 0,
                                   self.width() - self.verticalScrollBar().width(),
                                   self.height() - self.horizontalScrollBar().height())
        pixmap = self.grab(rect_region)
        fname = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Save fragment as ...', 'image.png',
            'Portable Network Graphics (*.png);;'
            'Joint Photographic Experts Group (*.jpeg *.jpg)'
        )[0]

        if fname:
            pixmap.save(fname)

    def mousePressEvent(self, event: QtCore.Qt.MouseButton.LeftButton) -> None:
        """
        The method handles the mouse press event.

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
        """
        The method handles the mouse move event.

        Args:
            event (QtCore.Qt.MouseButton.LeftButton): The mouse move event.

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
        """
        The method handles the mouse release event.

        Args:
            event (QtCore.Qt.MouseButton.LeftButton): The mouse release event.

        """
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._mousePressed = False
            self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))

        else:
            super(CustomGraphicView, self).mouseReleaseEvent(event)

    def wheelEvent(self, event: QtCore.Qt.KeyboardModifier.ControlModifier) -> None:
        """
        The method handles the wheel event.

        Args:
            event (QtCore.Qt.KeyboardModifier.ControlModifier): The wheel event.

        """
        modifiers = QtWidgets.QApplication.keyboardModifiers()

        if modifiers == QtCore.Qt.KeyboardModifier.ControlModifier:

            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1

            if self._zoom > -1:
                self.scale(factor, factor)
            else:
                self._zoom = 0
                # self.resetTransform()

            # Alternative variant
            # angle = event.angleDelta().y()
            # factor = 1 + (angle / 1000)
            # self.scale(factor, factor)

        else:
            super(CustomGraphicView, self).wheelEvent(event)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        """
        The method handles the context menu event.

        Args:
            event (QtGui.QContextMenuEvent): The context menu event.

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


class CustomPlainTextEdit(QtWidgets.QPlainTextEdit):
    # noinspection PyUnresolvedReferences
    """
    The class initializes a custom text edit with a custom caret.

    Attributes:
        parent (Optional[QtWdgets.QWidget], optional): The parent widget.

    Handling events:
        paintEvent(self, event: QtGui.QPaintEvent)

    """
    def __init__(self, parent=None) -> None:
        super(CustomPlainTextEdit, self).__init__(parent)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        """
        The method handles the paint event.

        Args:
            event (QtGui.QPaintEvent): The context menu event.

        """
        # Use paintEvent() of base class to do the main work
        QtWidgets.QPlainTextEdit.paintEvent(self, event)
        # Draw cursor (if widget has focus)
        if self.hasFocus():
            rect = self.cursorRect(self.textCursor())
            rect.setWidth(rect.width() * 5)
            painter = QtGui.QPainter(self.viewport())
            painter.fillRect(rect, QtGui.QColor('red'))

        else:
            super(CustomPlainTextEdit, self).paintEvent(event)


class CustomTextEditLogger(QtWidgets.QPlainTextEdit, logging.Handler):
    # noinspection PyUnresolvedReferences
    """
    The class initializes custom text edit object for logging interface in the GUI.

    Attributes:
        parent (Optional[QtWdgets.QWidget], optional): The parent widget.

    Handling events:
        emit(self, record: logging.LogRecord)

    """
    append_plain_text = QtCore.pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super(CustomTextEditLogger, self).__init__(parent)
        self.setReadOnly(True)

    def emit(self, record: logging.LogRecord) -> None:
        """
        Do whatever it takes to actually log the specified logging record.

        This version is intended to be implemented by subclasses and so raises a NotImplementedError.

        Args:
            record (logging.LogRecord): The record to be logged.

        Signals:
            - append_plain_text(str): The text to be appended to the logs terminal.

        """
        msg = self.format(record)

        color_info = '#000000'
        color_warning = '#ffffff'
        color_error = '#ff0000'

        if 'DEBUG' in msg or 'INFO' in msg:
            msg = f"<span style='color:{color_info};'>{msg}</span>"
        elif 'WARNING' in msg:
            msg = f"<span style='color:{color_warning};'>{msg}</span>"
        elif 'ERROR' in msg or 'CRITICAL' in msg:
            msg = f"<span style='color:{color_error};'>{msg}</span>"

        self.append_plain_text.emit(self.appendHtml(msg))


class ConfirmWindow(QtWidgets.QDialog):
    # noinspection PyUnresolvedReferences
    """
    The class initializes custom QDialog object.

    Attributes:
        parent (Optional[QtWdgets.QWidget], optional): The parent widget.
        msg (str): The message to be displayed. If None, show 'Are you sure?'.

    """

    def __init__(self, parent=None, msg: str = None) -> None:
        super(ConfirmWindow, self).__init__(parent)
        uic.loadUi(GUI_DIR / 'confirm.ui', self)

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)  # noqa

        if msg:
            self.textLabel.setText(msg)


class WindowMixin:
    """
    The class initializes the mixin for graphic window object.

    Mixins methods:
        - window_center_position: The method centers the window on the screen.

    """
    def window_center_position(self: GraphicWindow,
                               shift_x: int = 0,
                               shift_y: int = 0,
                               relative: ty.Tuple[int, int] = None) -> None:
        """
        The method centers the window on the screen.

        Args:
            shift_x (int, optional): The shift on the X axis in percentage. Defaults to 0.
            shift_y (int, optional): The shift on the Y axis in percentage. Defaults to 0.
            relative (ty.Tuple[int], optional): Relative position of one window relative to another.

        """
        desktop = QtWidgets.QDesktopWidget().screenGeometry()
        screen_width = desktop.width()
        screen_height = desktop.height()
        x = int((screen_width - self.width()) / 2)
        y = int((screen_height - self.height()) / 2)

        if not relative:
            self.move(
                int(x + self.width() * shift_x / 100),
                int(y - self.height() * shift_y / 100)
            )

        else:
            self.move(
                int(relative[0] + self.width() * shift_x / 100),
                int(relative[1] - self.height() * shift_y / 100)
            )


##################
# Custom threads #
##################

class GraphicsDataThread(QtCore.QThread):
    # noinspection PyUnresolvedReferences
    """
    The class defines a thread for loading graphics data.

    Attributes:
        parent (QtWdgets.QWidget, optional): The parent widget.
        outer_fn (Callable, optional): The outer function object.
        inner_fn (Callable, optional): The inner function object.

    Signals:
        - save_data(object): The data to be saved.
        - read_data(object): The data to be read.
        - load_complete(str): The message to be displayed on the success of loading.
        - load_failure(str): The message to be displayed on the failure of loading.

    """
    save_data = QtCore.pyqtSignal(object)
    read_data = QtCore.pyqtSignal(object)
    load_complete = QtCore.pyqtSignal(str)
    load_failure = QtCore.pyqtSignal(str)

    def __init__(self, parent=None,
                 outer_fn: ty.Union[GraphicClass, ty.Callable] = None,
                 inner_fn: ty.Union[GraphicClass, ty.Callable] = None,
                 *args) -> None:
        super(GraphicsDataThread, self).__init__(parent)
        self.outer_fn = outer_fn
        self.inner_fn = inner_fn
        self.args = (*args,)

    def run(self) -> ty.Any:
        """
        The method runs separated thread.

        """
        try:
            if self.inner_fn:
                data = self.outer_fn(self.inner_fn(*self.args))
            else:
                data = self.outer_fn(*self.args)

            only_fig = data.fig

            self.save_data.emit(data)
            self.read_data.emit(only_fig)
            self.load_complete.emit(
                f"Graphics '{self.outer_fn.LOGS_NAME}' successfully loaded."
            )

        except (Exception,):
            self.load_failure.emit(
                f"Problems with graphics initialization. '{self.outer_fn.LOGS_NAME}' not loaded."
            )


class TableDataThread(QtCore.QThread):
    # noinspection PyUnresolvedReferences
    """
    The class defines a thread for loading table data.

    Attributes:
        parent (QtWdgets.QWidget, optional): The parent widget.
        table (Table): The table object.

    Signals:
        - load_data(object): The data to be loaded.
        - load_complete(str): The message to be displayed on the success of loading.
        - load_failure(str): The message to be displayed on the failure of loading.

    """
    load_data = QtCore.pyqtSignal(object)
    load_complete = QtCore.pyqtSignal(str)
    load_failure = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, table: BT = None):
        super(TableDataThread, self).__init__(parent)
        self.table = table

    def run(self):
        """
        The method runs separated thread.

        """
        try:
            if 'JoinedMixin' in map(lambda x: x.__name__, self.table.__mro__):
                data = self.table.show_table(self.table.read_joined_table())
            else:
                data = self.table.show_table(self.table.read_table())

            self.load_data.emit(data)
            self.load_complete.emit(
                f"Table '{self.table.__tablename__}' successfully loaded."
            )

        except (Exception,):
            self.load_failure.emit(
                f"Problems with table '{self.table.__tablename__}'. Try to reinstall database."
            )


####################
# App main windows #
####################

class MainWindow(QtWidgets.QMainWindow, WindowMixin):
    # noinspection PyUnresolvedReferences
    """
    The class defines the main window of the program.

    Attributes:
        parent (QtWdgets.QWidget, optional): The parent widget.

    Interface:
        - Contains informative logs terminal.
        - Contains input terminal allowing to input data.
        - Shows dynamic interactive results and allows save them in any format.
        - Contain dynamic catalog of current database unique values.
        - Contains settings panel for the program and allows to change them at any time (partial).
        - Allow to open custom database browser for manage database.

    Handling events:
        - eventFilter: The method handles eventFilter.
        - closeEvent: The method handles the close event of the window.

    """
    def __init__(self, parent=None) -> None:
        super(MainWindow, self).__init__(parent)
        uic.loadUi(GUI_DIR / 'main_window.ui', self)

        # Saved instances
        self.results_figure = None
        self.db_browser = None

        self.init_gui()

    def init_gui(self) -> None:
        """
        The method initializes the main window GUI.

        Interface initialization includes:
            - Logger frame settings.
            - Initial start interface.
            - Main bar buttons config.
            - Side panel buttons config.
            - Input tab settings.
            - Results tab settings.
            - Catalog tab settings.
            - Settings tab config.

        """
        #########################
        # Logger frame settings #
        #########################
        self.logsOutput.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s'))
        logging.getLogger().addHandler(self.logsOutput)
        logging.getLogger().setLevel(logging.INFO)

        ###########################
        # Initial start interface #
        ###########################
        self.switchButton.setChecked(True)
        self.logsButton.setChecked(False)

        # Hiding tab bar for QTabWidget
        self.findChild(QtWidgets.QTabBar).hide()

        # Set window position in the center of the screen
        self.window_center_position()

        ###########################
        # Main bar buttons config #
        ###########################
        self.switchButton.setToolTip('Switch side panel view')

        self.dbmanagerButton.setToolTip('Open database manage client in separate window')
        self.dbmanagerButton.clicked.connect(self.open_db_browser)

        #############################
        # Side panel buttons config #
        #############################
        self.inputButton.setToolTip('Show input console')
        self.inputButton.clicked.connect(lambda: self.tabWidget.setCurrentIndex(0))

        self.resultButton.setToolTip('Show calculation results')
        self.resultButton.clicked.connect(lambda: self.tabWidget.setCurrentIndex(1))

        self.catalogButton.setToolTip('Show electrical catalog')
        self.catalogButton.clicked.connect(lambda: self.tabWidget.setCurrentIndex(2))

        self.logsButton.setToolTip('Show logs terminal')

        self.settingsButton.setToolTip('Show settings')
        self.settingsButton.clicked.connect(lambda: self.tabWidget.setCurrentIndex(3))

        self.infoButton.setToolTip('Show info')
        self.infoButton.clicked.connect(lambda: self.tabWidget.setCurrentIndex(4))

        ######################
        # Input tab settings #
        ######################
        self.consoleInput.installEventFilter(self)

        # Set placeholder text color
        palette = self.consoleInput.palette()
        text_color = QtGui.QColor("white")
        palette.setColor(QtGui.QPalette.PlaceholderText, text_color)
        self.consoleInput.setPalette(palette)

        self.consoleInput.setPlaceholderText(
            'Enter your statement here and press [CTRL + ENTER] to calculate system.\n'
            'For each element in one chain use the same style (using project names or not).\n'
            "Use next service special symbols:\n"
            "   ' ' - for separate attributes of element in chain;\n"
            "   ':' - for separate project name and value of element in chain (if project name exists);\n"
            "   ',' - for separate elements in chain;\n"
            "   ';' - for separate chains.\n"
            'Query chains sample:\n\n'
            "T(160, 'У/Ун-0'), QS(160), QF(160), Line(), QF(25), W('ВВГ', 3, 4, 20), Line(), Arc();\n\n"
            "TCH: T(160, 'У/Ун-0'), QF3: QF(100), R1: Line(), QF2: QF(25), W1: W('ВВГ', 3, 4, 20)"
        )

        ########################
        # Results tab settings #
        ########################
        pass

        ########################
        # Catalog tab settings #
        ########################
        self.set_catalog()

        ###########################
        #   Settings tab config   #
        ###########################
        BoxParams = namedtuple('BoxParams', ('editable', 'values', 'default', 'update'))

        box_config = {

            # Database settings
            self.settingsBox: BoxParams(
                True, [config_manager('SQLITE_DB_NAME')], config_manager('SQLITE_DB_NAME'),
                lambda: self.admit_changes('SQLITE_DB_NAME', self.settingsBox)
            ),

            self.settingsBox2: BoxParams(
                False, ['MySQL', 'SQLite'], config_manager('DB_EXISTING_CONNECTION'),
                lambda: self.admit_changes('DB_EXISTING_CONNECTION', self.settingsBox2)
            ),

            self.settingsBox3: BoxParams(
                False, [True, False], config_manager('DB_TABLES_CLEAR_INSTALL'),
                lambda x: config_manager('DB_TABLES_CLEAR_INSTALL', x)
            ),

            self.settingsBox4: BoxParams(
                False, [True, False], config_manager('ENGINE_ECHO'),
                lambda: self.admit_changes('ENGINE_ECHO', self.settingsBox4)
            ),

            # Calculations settings
            self.settingsBox5: BoxParams(
                False, [3, 1], config_manager('SYSTEM_PHASES'),
                lambda x: config_manager('SYSTEM_PHASES', x)
            ),

            self.settingsBox6: BoxParams(
                False, [Decimal('0.4')], config_manager('SYSTEM_VOLTAGE_IN_KILOVOLTS'),
                lambda x: config_manager('SYSTEM_VOLTAGE_IN_KILOVOLTS', x)
            ),

            self.settingsBox7: BoxParams(
                True, [config_manager('CALCULATIONS_ACCURACY')], config_manager('CALCULATIONS_ACCURACY'),
                lambda x: config_manager('CALCULATIONS_ACCURACY', x)
            )
        }

        for box in box_config:
            # Creating combo box options list
            default = box_config[box].default
            others = box_config[box].values
            others.remove(default)
            default = [default]
            default.extend(others)
            for i in range(len(default)):
                default[i] = str(default[i])

            # Creating GUI for combo box options list
            box.addItems(default)
            box.setEditable(True)
            line_edit = box.lineEdit()
            line_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            line_edit.setReadOnly(not box_config[box].editable)
            if box_config[box].editable:
                box.setStyleSheet('font: italic bold 11pt')
            else:
                box.setStyleSheet('font: italic bold 11pt; background-color: lightgray')

            box.previous_index = box.currentText()

        # Actions if combo boxes changed
        self.settingsBox.currentIndexChanged.connect(box_config[self.settingsBox].update)
        self.settingsBox2.currentIndexChanged.connect(box_config[self.settingsBox2].update)
        self.settingsBox3.currentIndexChanged.connect(
            lambda: box_config[self.settingsBox3].update(self.settingsBox3.currentText())
        )
        self.settingsBox4.currentIndexChanged.connect(box_config[self.settingsBox4].update)
        self.settingsBox5.currentIndexChanged.connect(
            lambda: box_config[self.settingsBox5].update(self.settingsBox5.currentText())
        )
        self.settingsBox6.currentIndexChanged.connect(
            lambda: box_config[self.settingsBox6].update(self.settingsBox6.currentText())
        )
        self.settingsBox7.currentIndexChanged.connect(
            lambda: box_config[self.settingsBox7].update(self.settingsBox7.currentText())
        )

    def admit_changes(self, critical_param: str, owner: QtWidgets.QComboBox) -> None:
        """
        The method admit critical changes and reload app if changes were made.

        The method admit critical changes and reload app if changes were made.
        If changes were not made, the method returns to previous state.

        Args:
            critical_param (str): The name of critical param.
            owner (QtWidgets.QComboBox): The owner of param field.

        """
        if not owner.previous_index == owner.currentText():
            confirm_window = ConfirmWindow(self, 'ADMIT CHANGES AND RELOAD APP?')
            confirm_window.exec_()

            if confirm_window.result() == QtWidgets.QDialog.Accepted:
                config_manager(critical_param, owner.currentText())
                owner.previous_index = owner.currentText()
                self.restart_app()

            else:
                index = owner.findText(owner.previous_index)
                owner.setCurrentIndex(index)

    def set_catalog(self) -> None:
        """
        The method set catalog figure in the catalog view.

        Loading catalog figure processing in a separate thread
        and when it is done, the catalog view is updated.

        """
        catalog_thread = GraphicsDataThread(self, CatalogFigure)

        catalog_thread.read_data.connect(self.catalogView.set_figure)
        catalog_thread.load_complete.connect(logger.info)
        catalog_thread.load_failure.connect(logger.error)

        catalog_thread.start()

    def open_db_browser(self) -> None:
        """
        The method create and open database browser window.

        If database browser is already were opened in session, the method just opens it.

        """
        if self.db_browser is None:
            self.db_browser = DatabaseBrowser()
            self.db_browser.window_center_position(
                shift_x=5, shift_y=-5, relative=(self.x(), self.y())
            )
        self.db_browser.show()

    def save_interactive_stmt(self, figure_obj: matplotlib.figure.Figure) -> None:
        """
        The method save interactive figure in the app state.

        Args:
            figure_obj (matplotlib.figure.Figure): The matplotlib figure object.

        """
        self.results_figure = figure_obj

    def eventFilter(self, obj: QtWidgets.QWidget, event: QtCore.QEvent) -> bool:
        """
        The method handles eventFilter.

        When console input is focused and pressed 'CTRL + ENTER', the method start new thread
        for loading interactive results figure. When it is done, the results view is updated.

        Args:
            obj (QtWidgets.QWidget): The widget object.
            event (QtCore.QEvent): The event object.

        """
        if event.type() == QtCore.QEvent.KeyPress and obj is self.consoleInput:  # noqa
            if event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Return:  # noqa
                text = self.consoleInput.toPlainText()
                results_thread = GraphicsDataThread(
                    self, ResultsFigure, ChainsSystem, text
                )

                results_thread.save_data.connect(self.save_interactive_stmt)
                results_thread.read_data.connect(self.resultsView.set_figure)
                results_thread.load_complete.connect(logger.info)
                results_thread.load_failure.connect(logger.error)

                results_thread.start()

        return super().eventFilter(obj, event)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """
        The method handles the close event of the window.

        This function is called when the user tries to close the window. It creates a confirmation window
        and displays it to the user. If the user confirms the close action, the event is accepted and the
        window is closed. Otherwise, the event is ignored and the window remains open.

        Args:
            event (QtGui.QCloseEvent): The close event object.

        """
        app = QtWidgets.QApplication.instance()
        confirm_window = ConfirmWindow(self)
        confirm_window.exec_()
        if confirm_window.result() == QtWidgets.QDialog.Accepted:
            event.accept()
            for window in app.topLevelWidgets():  # noqa
                window.close()
        else:
            event.ignore()

    @staticmethod
    def restart_app() -> None:
        """
        The method restarts the app.

        """
        os.execl(sys.executable, sys.executable, *sys.argv)


class DatabaseBrowser(QtWidgets.QWidget, WindowMixin):
    # noinspection PyUnresolvedReferences
    """
    The class creates database browser window and allows to manage database.

    Attributes:
        parent (QtWdgets.QWidget, optional): The parent widget.

    Interface:
        - Shows different categories of database in separate views.
        - Allows to install or reinstall database.
        - Allows to manage database.
        - Supports CRUD operations on database as insert, update and delete.
        - Supports update keys and non keys values.
        - Supports delete values from joined tables and source tables (from catalog).

    Handling events:
        - crud_event: The method get tools and ready for CRUD operations to execution, await command.

    """
    def __init__(self, parent=None) -> None:
        super(DatabaseBrowser, self).__init__(parent)
        uic.loadUi(GUI_DIR / 'db_browser.ui', self)

        self.init_gui()
        self.main_menu = next(widget for widget in QtWidgets.QApplication.topLevelWidgets()
                              if isinstance(widget, MainWindow))
        self.show_database()
        self.crud_operations()

    def init_gui(self) -> None:
        """
        The method initializes the database browser GUI.

        Interface initialization includes:
            - Initial start interface.
            - Main keys actions binding.

        """
        ###########################
        # Initial start interface #
        ###########################
        self.viewerWidget.setCurrentIndex(0)
        self.optionsWidget.setCurrentIndex(0)
        self.manageButton.setChecked(True)

        # Set DB name and logo
        db_key = config_manager('DB_EXISTING_CONNECTION')

        names = {
            'MySQL': 'MySQL Browser',
            'SQLite': 'SQLite Browser',
            False: 'Database Browser'
        }

        logos = {
            'MySQL': QtGui.QPixmap(':/logos/resources/logos/db_mysql_rectangle.svg'),
            'SQLite': QtGui.QPixmap(':/logos/resources/logos/db_sqlite_rectangle.svg'),
            False: QtGui.QPixmap(':/logos/resources/logos/db_no_connections.svg')
        }

        self.setWindowTitle(names[db_key])
        self.iconLabel.setPixmap(logos[db_key])
        self.iconLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        #############################
        # Main keys actions binding #
        #############################
        self.installButton.clicked.connect(self.reinstall_database)

    def show_database(self) -> None:
        """
        The method loads data from database in separate threads and shows it in the views.

        """
        tables = Transformer, Cable, CurrentBreaker, OtherContact
        views = self.transformersView, self.cablesView, self.contactsView, self.resistancesView

        threads = []

        for table, view in zip(tables, views):
            table_data_thread = TableDataThread(self, table)

            table_data_thread.load_data.connect(view.set_figure)
            table_data_thread.load_complete.connect(logger.info)
            table_data_thread.load_failure.connect(logger.error)

            threads.append(table_data_thread)
            table_data_thread.start()

    def reinstall_database(self) -> None:
        """
        The method allows to install or reinstall the database.

        Clear or partially install depending on the installation settings configuration.
        After operation, the catalog view is updated.

        """
        confirm_window = ConfirmWindow(self, 'RE/INSTALL DATABASE?')
        confirm_window.exec_()

        if confirm_window.result() == QtWidgets.QDialog.Accepted:
            db_install(clear=config_manager('DB_TABLES_CLEAR_INSTALL'))
            self.show_database()
            self.main_menu.set_catalog()

    def crud_operations(self) -> None:
        """
        The method executes the CRUD operations when crud_event is called.

        Update method supports update keys and non keys values.
        Delete method supports delete values from joined tables (pivot table)
        and source tables (from catalog).

        """
        ##############################
        # Insert operations settings #
        ##############################
        self.insertButton.clicked.connect(lambda: self.crud_event(self.get_insert_tools))

        ##############################
        # Update operations settings #
        ##############################
        self.updateButton.clicked.connect(lambda: self.crud_event(self.get_update_tools))

        ##############################
        # Delete operations settings #
        ##############################
        self.rowButton.clicked.connect(lambda: self.crud_event(self.get_delete_tools, False))
        self.sourceButton.clicked.connect(lambda: self.crud_event(self.get_delete_tools, True))

    @logging_error
    def crud_event(self, get_tools: namedtuple, *args, **kwargs) -> None:
        """
        The method get tools and ready for CRUD operations to execution, await command.

        Args:
            get_tools(namedtuple): tools for CRUD operations.

        """
        tools = get_tools()
        tools.operation(*args, **kwargs)

        if 'JoinedMixin' in map(lambda x: x.__name__, tools.table.__mro__):
            tools.view.set_figure(
                tools.table.show_table(tools.table.read_joined_table())
            )
        else:
            tools.view.set_figure(
                tools.table.show_table(tools.table.read_table())
            )

        self.main_menu.set_catalog()

    def get_insert_tools(self) -> namedtuple:
        """
        The method returns tools for insert operations.

        Returns:
            namedtuple: tools for insert operations.

        """
        InsertTuple = namedtuple('InsertTuple', ('table', 'view', 'operation'))

        insert_operations = {
            'insertTransPage': InsertTuple(
                Transformer, self.transformersView, lambda: Transformer.insert_joined_table(
                    data=[
                        asdict(
                            InsertTrans(
                                self.insertTransEdit.text(),
                                self.insertTransEdit2.text(),
                                self.insertTransEdit3.text(),
                                self.insertTransEdit4.text(),
                                self.insertTransEdit5.text(),
                                self.insertTransEdit6.text(),
                                self.insertTransEdit7.text(),
                                self.insertTransEdit8.text(),
                                self.insertTransEdit9.text()
                            )
                        )
                    ]
                )
            ),

            'insertCablePage': InsertTuple(
                Cable, self.cablesView, lambda: Cable.insert_joined_table(
                    data=[
                        asdict(
                            InsertCable(
                                self.insertCableEdit.text(),
                                self.insertCableEdit2.text(),
                                self.insertCableEdit3.text(),
                                self.insertCableEdit4.text(),
                                self.insertCableEdit5.text(),
                                self.insertCableEdit6.text(),
                                self.insertCableEdit7.text(),
                                self.insertCableEdit8.text()
                            )
                        )
                    ]
                )
            ),

            'insertContactPage': InsertTuple(
                CurrentBreaker, self.contactsView, lambda: CurrentBreaker.insert_joined_table(
                    data=[
                        asdict(
                            InsertContact(
                                self.insertContactEdit.text(),
                                self.insertContactEdit2.text(),
                                self.insertContactEdit3.text(),
                                self.insertContactEdit4.text(),
                                self.insertContactEdit5.text(),
                                self.insertContactEdit6.text()
                            )
                        )
                    ]
                )
            ),

            'insertResistPage': InsertTuple(
                OtherContact, self.resistancesView, lambda: OtherContact.insert_table(
                    data=[
                        asdict(
                            InsertResist(
                                self.insertResistEdit.text(),
                                self.insertResistEdit2.text(),
                                self.insertResistEdit3.text(),
                                self.insertResistEdit4.text(),
                                self.insertResistEdit5.text()
                            )
                        )
                    ]
                )
            )
        }

        return insert_operations[self.insertWidget.currentWidget().objectName()]

    def get_update_tools(self) -> namedtuple:
        """
        The method returns tools for update operations.

        Returns:
            namedtuple: tools for update operations.

        """
        UpdateTuple = namedtuple('UpdateTuple', ('table', 'view', 'operation'))

        update_operations = {
            'updateTransPage': UpdateTuple(
                Transformer, self.transformersView, lambda: Transformer.update_joined_table(
                    old_source_data=asdict(
                        dict_factory=self.__dict_factory,
                        obj=UpdateTransOldSource(
                            self.updateTransEdit.text(),
                            self.updateTransEdit2.text(),
                            self.updateTransEdit3.text()
                        )
                    ),
                    new_source_data=asdict(
                        dict_factory=self.__dict_factory,
                        obj=UpdateTransNewSource(
                            self.updateTransEdit4.text(),
                            self.updateTransEdit5.text(),
                            self.updateTransEdit6.text()
                        )
                    ),
                    target_row_data=asdict(
                        dict_factory=self.__dict_factory,
                        obj=UpdateTransRow(
                            self.updateTransEdit7.text(),
                            self.updateTransEdit8.text(),
                            self.updateTransEdit9.text(),
                            self.updateTransEdit10.text(),
                            self.updateTransEdit11.text(),
                            self.updateTransEdit12.text()
                        )
                    )
                )
            ),

            'updateCablePage': UpdateTuple(
                Cable, self.cablesView, lambda: Cable.update_joined_table(
                    old_source_data=asdict(
                        dict_factory=self.__dict_factory,
                        obj=UpdateCableOldSource(
                            self.updateCableEdit.text(),
                            self.updateCableEdit2.text(),
                            self.updateCableEdit3.text()
                        )
                    ),
                    new_source_data=asdict(
                        dict_factory=self.__dict_factory,
                        obj=UpdateCableNewSource(
                            self.updateCableEdit4.text(),
                            self.updateCableEdit5.text(),
                            self.updateCableEdit6.text()
                        )
                    ),
                    target_row_data=asdict(
                        dict_factory=self.__dict_factory,
                        obj=UpdateCableRow(
                            self.updateCableEdit7.text(),
                            self.updateCableEdit8.text(),
                            self.updateCableEdit9.text(),
                            self.updateCableEdit10.text(),
                            self.updateCableEdit11.text()
                        )
                    )
                )
            ),

            'updateContactPage': UpdateTuple(
                CurrentBreaker, self.contactsView, lambda: CurrentBreaker.update_joined_table(
                    old_source_data=asdict(
                        dict_factory=self.__dict_factory,
                        obj=UpdateContactOldSource(
                            self.updateContactEdit.text(),
                            self.updateContactEdit2.text()
                        )
                    ),
                    new_source_data=asdict(
                        dict_factory=self.__dict_factory,
                        obj=UpdateContactNewSource(
                            self.updateContactEdit3.text(),
                            self.updateContactEdit4.text()
                        )
                    ),
                    target_row_data=asdict(
                        dict_factory=self.__dict_factory,
                        obj=UpdateContactRow(
                            self.updateContactEdit5.text(),
                            self.updateContactEdit6.text(),
                            self.updateContactEdit7.text(),
                            self.updateContactEdit8.text()
                        )
                    )
                )
            ),

            'updateResistPage': UpdateTuple(
                OtherContact, self.resistancesView, lambda: OtherContact.update_table(
                    {
                        **asdict(
                            dict_factory=self.__dict_factory,
                            obj=UpdateResistNewSource(
                                self.updateResistEdit2.text()
                            )
                        ),
                        **asdict(
                            dict_factory=self.__dict_factory,
                            obj=UpdateResistRow(
                                self.updateResistEdit3.text(),
                                self.updateResistEdit4.text(),
                                self.updateResistEdit5.text(),
                                self.updateResistEdit6.text()
                            )
                        )
                    },
                    options='where_condition',
                    attr='contact_type',
                    criteria=(
                        asdict(
                            dict_factory=self.__dict_factory,
                            obj=UpdateResistOldSource(
                                self.updateResistEdit.text()
                            )
                        )['contact_type'],
                    )
                )
            )
        }

        return update_operations[self.updateWidget.currentWidget().objectName()]

    def get_delete_tools(self) -> namedtuple:
        """
        The method returns tools for delete operations.

        Returns:
            namedtuple: tools for delete operations.

        """
        DeleteTuple = namedtuple('DeleteTuple', ('table', 'view', 'operation'))

        delete_operations = {
            'deleteTransPage': DeleteTuple(
                Transformer, self.transformersView, lambda x: Transformer.delete_joined_table(
                    from_source=x,
                    source_data=asdict(
                        dict_factory=self.__dict_factory,
                        obj=DeleteTrans(
                            self.deleteTransEdit.text(),
                            self.deleteTransEdit2.text(),
                            self.deleteTransEdit3.text()
                        )
                    )
                )
            ),

            'deleteCablePage': DeleteTuple(
                Cable, self.cablesView, lambda x: Cable.delete_joined_table(
                    from_source=x,
                    source_data=asdict(
                        dict_factory=self.__dict_factory,
                        obj=DeleteCable(
                            self.deleteCableEdit.text(),
                            self.deleteCableEdit2.text(),
                            self.deleteCableEdit3.text()
                        )
                    )
                )
            ),

            'deleteContactPage': DeleteTuple(
                CurrentBreaker, self.contactsView, lambda x: CurrentBreaker.delete_joined_table(
                    from_source=x,
                    source_data=asdict(
                        dict_factory=self.__dict_factory,
                        obj=DeleteContact(
                            self.deleteContactEdit.text(),
                            self.deleteContactEdit2.text()
                        )
                    )
                )
            ),
            'deleteResistPage': DeleteTuple(
                OtherContact, self.resistancesView, lambda x: OtherContact.delete_table(
                    filtrate=next(
                        map(
                            lambda pair: f"{pair[0]} = '{pair[1]}'",
                            tuple(
                                asdict(
                                    dict_factory=self.__dict_factory,
                                    obj=DeleteResist(
                                        self.deleteResistEdit.text()
                                    )
                                ).items()
                            )
                        )
                    )
                )
            )
        }

        return delete_operations[self.deleteWidget.currentWidget().objectName()]

    @property
    def __dict_factory(self) -> ty.Callable:
        """
        The method returns a dictionary factory template lambda function.

        Returns:
            ty.Callable: dictionary factory template lambda function.

        """
        return lambda x: {k: v for (k, v) in x if v is not None}


########################
# Others functionality #
########################

pass
