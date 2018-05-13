import logging
import sys
from multiprocessing.pool import ThreadPool
from typing import List

from PyQt5 import QtWebEngineWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QMainWindow,
    QAction,
    QSplitter,
    QHBoxLayout,
    QWidget,
    QSizePolicy
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from data_explorer.testlet import TestletResult


class InlineHTML:
    def __init__(self, html):
        self.html = html


class EvaluateOnUiThread:
    def __init__(self, func):
        self.func = func

    def evaluate(self):
        return self.func()


class ExpandingFigureCanvas(FigureCanvas):
    def __init__(self, figure: Figure):
        FigureCanvas.__init__(self, figure)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def savefig(self, filename):
        self.figure.savefig(filename)


class TestletResultItem(QTableWidgetItem):

    def __init__(self, testlet_result):
        QTableWidgetItem.__init__(self, testlet_result.view)
        self.testlet_result = testlet_result

    def __lt__(self, other):
        res = True
        # noinspection PyBroadException
        try:
            if other is None:
                res = True
            elif isinstance(other, TestletResultItem):
                res = self.testlet_result.model < other.testlet_result.model
            else:
                res = super(QTableWidgetItem, self).__lt__(other)
        except Exception:
            pass

        if bool(res) != res:
            print("comparing strange things")

        return bool(res)


class MainWindow(QMainWindow):
    testlet_evaluated = pyqtSignal(int, list, name='testlet evaluated')
    table_widget: QTableWidget = None
    embedded_browsers = []

    def __init__(self, entry_list, testlet_list, title, main_figures=None, icon=None):
        # noinspection PyArgumentList
        super(MainWindow, self).__init__()

        self.setWindowIcon(QIcon(icon))

        # self.path = path
        self.entry_list = entry_list
        self.testlet_list = testlet_list

        self.setGeometry(50, 50, 1600, 900)
        self.setWindowTitle(title)

        # Add menu
        main_menu = self.menuBar()

        file_menu = main_menu.addMenu('&File')

        quit_action = QAction('&Quit', self)
        quit_action.setShortcut('Ctrl+Q')
        quit_action.setStatusTip('Leave App')
        # noinspection PyUnresolvedReferences
        quit_action.triggered.connect(self.close_application)
        file_menu.addAction(quit_action)

        action_menu = main_menu.addMenu('&Action')

        save_png_action = QAction('Save Figures as PNG', self)
        save_png_action.setStatusTip('Save Figures to PNG Files')
        # noinspection PyUnresolvedReferences
        save_png_action.triggered.connect(self.save_figures_png)
        action_menu.addAction(save_png_action)
        save_svg_action = QAction('Save Figures as SVG', self)
        save_svg_action.setStatusTip('Save Figures to SVG Files')
        # noinspection PyUnresolvedReferences
        save_svg_action.triggered.connect(self.save_figures_svg)
        action_menu.addAction(save_svg_action)

        big_image_action = QAction('Use Big Images', self)

        # big_image_action.setStatusTip('Save Figures to SVG Files')
        # noinspection PyUnresolvedReferences
        def foo():
            self.set_image_size(10000)

        big_image_action.triggered.connect(foo)
        action_menu.addAction(big_image_action)

        # Show status bar
        self.statusBar()

        # Setup main layout
        horizontal_splitter = QSplitter(Qt.Vertical)
        self.main_figures = []

        def add_main_figure(fig):
            if isinstance(fig, FigureCanvas):
                self.main_figures.append(fig)
                horizontal_splitter.addWidget(fig)
            elif isinstance(fig, Figure):
                canvas = ExpandingFigureCanvas(fig)
                self.main_figures.append(canvas)
                horizontal_splitter.addWidget(canvas)
            else:
                raise Exception('Invalid main figure type')

        if isinstance(main_figures, list):
            for main_figure in main_figures:
                add_main_figure(main_figure)
        else:
            if main_figures is not None:
                add_main_figure(main_figures)

        vertical_splitter = QSplitter(Qt.Horizontal)

        self.create_table(testlet_list, entry_list)
        vertical_splitter.addWidget(self.table_widget)
        vertical_splitter.addWidget(horizontal_splitter)

        main_layout = QHBoxLayout()
        # noinspection PyArgumentList
        main_layout.addWidget(vertical_splitter)

        # noinspection PyArgumentList
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    @staticmethod
    def close_application():
        logging.warning('Closing application from UI')
        sys.exit()

    def save_figures_png(self):
        logging.info('Saving figures')
        for fig in self.main_figures:
            fig.savefig(f'{self.path}/{fig}.png')

    def save_figures_svg(self):
        logging.info('Saving figures')
        for fig in self.main_figures:
            fig.savefig(f'{self.path}/{fig}.svg')

    @staticmethod
    def set_cell(table_widget: QTableWidget, row: int, col: int, testlet_result: TestletResult):
        if isinstance(testlet_result.view, str):
            item = TestletResultItem(testlet_result)
            item.setTextAlignment(Qt.AlignRight)
            if testlet_result.color is not None:
                item.setBackground(QColor(*[int(255 * max(0.0, min(c, 1.0))) for c in testlet_result.color[:3]]))
            table_widget.setItem(row, col, item)

        elif isinstance(testlet_result.view, Figure):
            web = ExpandingFigureCanvas(testlet_result.view)
            web.setMaximumWidth(200)
            web.setMaximumHeight(200)
            MainWindow.embedded_browsers.append(web)
            table_widget.setCellWidget(row, col, web)

        elif isinstance(testlet_result.view, InlineHTML):
            web = QtWebEngineWidgets.QWebEngineView()
            # web.setUrl(QtCore.QUrl(testlet_result.view.html))
            web.setHtml(testlet_result.view.html)
            web.setMaximumWidth(200)
            web.setMaximumHeight(200)
            MainWindow.embedded_browsers.append(web)
            table_widget.setCellWidget(row, col, web)

        elif isinstance(testlet_result.view, EvaluateOnUiThread):
            # noinspection PyUnresolvedReferences
            testlet_result.view = testlet_result.view.evaluate()
            table_widget.setCellWidget(row, col, testlet_result.view)

        else:
            table_widget.setCellWidget(row, col, testlet_result.view)

    def create_table(self, testlet_list, entry_list):
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(len(testlet_list))
        self.table_widget.setRowCount(len(entry_list))
        self.table_widget.setSortingEnabled(True)

        for row, entry in enumerate(entry_list):
            for col, testlet in enumerate(testlet_list):
                item = QTableWidgetItem('loading...')
                item.setBackground(QColor(0xA0, 0xA0, 0xA0))
                self.table_widget.setItem(row, col, item)

        testlet_names = [str(x) for x in testlet_list]
        self.table_widget.setHorizontalHeaderLabels(testlet_names)
        self.table_widget.resizeRowsToContents()
        self.table_widget.resizeColumnsToContents()

        self.evaluate_testlets_in_background()

    def evaluate_row(self, row: int):
        testlet_results = [testlet.wrapped_evaluate(self.entry_list[row]) for testlet in self.testlet_list]
        self.testlet_evaluated.emit(row, testlet_results)

    def update_row(self, row: int, testlet_results: List[TestletResult]):
        for col, testlet_result in enumerate(testlet_results):
            MainWindow.set_cell(self.table_widget, row, col, testlet_result)

        self.table_widget.resizeRowToContents(row)
        self.table_widget.resizeColumnsToContents()

    @staticmethod
    def set_image_size(size):
        for web in MainWindow.embedded_browsers:
            web.setMaximumWidth(size)
            web.setMaximumHeight(size)
        print("Image Size %d" % size)

    def evaluate_testlets_in_background(self):
        self.testlet_evaluated.connect(self.update_row)
        pool = ThreadPool(processes=4)
        pool.map_async(self.evaluate_row, range(len(self.entry_list)))
