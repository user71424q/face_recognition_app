import traceback

from gui import MainWindow
from PyQt6.QtWidgets import QApplication, QMessageBox
import sys


def my_excepthook(type, value, tback):
    """
            Внешний перехват всех необработанных исключений и вызов окна критической ошибки

    """
    fatal_error = QMessageBox()
    fatal_error.setIcon(QMessageBox.Icon.Critical)
    fatal_error.setWindowTitle('Критическая ошибка')
    fatal_error.setText('Произошла непредвиденная ошибка')
    fatal_error.setInformativeText(str(value) + '\nТребуется перезапуск приложения')
    fatal_error.exec()
    QApplication([]).exec()


sys.excepthook = my_excepthook

app = QApplication([])
window = MainWindow()
window.show()
app.exec()

