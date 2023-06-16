from gui import MainWindow
from PyQt6.QtWidgets import QApplication, QMessageBox


# самый мейн мы оборачиваем в try где прога будет падать с окном о неизвестной ошибке пожалуйста свяжитесь с разработчиком для хотфикса и полный код питоновской ошибки
try:
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
except Exception as e:
    print(e)
    fatal_error = QMessageBox()
    fatal_error.setIcon(QMessageBox.Icon.Critical)
    fatal_error.setWindowTitle('Критическая ошибка')
    fatal_error.setText('Произошла непредвиденная ошибка')
    fatal_error.exec()
