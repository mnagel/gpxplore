import logging
import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication

from data_explorer.gui import MainWindow


def execute(
        title: str,
        entry_list: list,
        testlet_list: list,
        icon: str,
        main_figures=None,
        verbose: bool = False
):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    app = QApplication([])
    font = QtGui.QFont("Courier", 10)
    app.setFont(font)
    win = MainWindow(entry_list, testlet_list, title, main_figures=main_figures, icon=icon)
    win.show()

    # Execute and exit with app result code
    sys.exit(app.exec_())
