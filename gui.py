from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QLabel, QLineEdit, QGridLayout
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Распознавание лиц")
        self.setWindowIcon(QIcon('.\\visual\\icon.png'))
        self.setMaximumSize(1920, 1080)


        self.pathTextLine = QLineEdit("", )
        self.pathTextLine.setEnabled(False)
        self.image = QLabel()
        dir_layout = self.initDirLayout()

        button = QPushButton("Фото")
        button.clicked.connect(self.openfile)
        l = QVBoxLayout()
        l.addLayout(dir_layout)
        l.addWidget(button)
        l.addWidget(self.image)
        wid = QWidget()
        wid.setLayout(l)


        self.setCentralWidget(wid)


    def initDirLayout(self):

        button = QPushButton("Обзор")
        button.clicked.connect(self.getDirectory)

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(QLabel("Выберите папку с датасетом: "), 0, 0)
        grid.setColumnMinimumWidth(1, 5)
        grid.addWidget(self.pathTextLine, 0, 2)
        grid.setColumnMinimumWidth(3, 5)
        grid.addWidget(button, 0, 4)
        # минимальная длина строки пути (она же 2 колонка сетки)
        grid.setColumnMinimumWidth(2, 270)
        # растягивается только 2 колонка сетки (с множителем 1)
        grid.setColumnStretch(2, 1)

        return grid


    def getDirectory(self):
        dirlist = QFileDialog.getExistingDirectory(self, "Выбрать папку", ".")
        self.pathTextLine.setText(dirlist)

    def openfile(self):
        fname = QFileDialog.getOpenFileName(
            self,
            'Выберите картинку',
            '.',
            "PNG Files(*.png);;JPG Files(*.jpg);;BMP File(*.BMP)"
        )[0]
        if not fname:
            return
        self.pixmap = QPixmap(fname)
        self.image.setPixmap(self.pixmap)

        size = self.pixmap.size()
        pos = self.pos()
        self.setGeometry(pos.x() + 10, pos.y() + 30, size.width(), size.height())
        self.layout.activate()
        #self.adjustSize()


app = QApplication([])
window = MainWindow()
window.show()
app.exec()