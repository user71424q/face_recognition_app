from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton,\
    QFileDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QGridLayout, QCheckBox
from PyQt6.QtGui import QIcon, QPixmap, QImage
from PyQt6.QtCore import Qt
import threading

from recognition import getImage

class PixmapContainer(QLabel):
    def __init__(self, pixmap, parent=None):
        super(PixmapContainer, self).__init__(parent)
        self._pixmap = QPixmap(pixmap)
        self.setMinimumSize(256, 256)  # needed to be able to scale down the image

    def resizeEvent(self, event):
        w = min(self.width(), self._pixmap.width())
        h = min(self.height(), self._pixmap.height())
        self.setPixmap(self._pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Распознавание лиц")
        self.setWindowIcon(QIcon('.\\visual\\icon.png'))

        self.imgpath = None
        self.pathTextLine = QLineEdit("", )
        self.pathTextLine.setEnabled(False)
        self.showUnknown = False

        # возможно некое анонимное изображение до выбора конкретного
        # вероятно запуск программы на анонимном изображении запрещен
        self.image = QLabel()

        dir_layout = self.initDirLayout()
        tool_layout = self.initToolbar()

        hl = QHBoxLayout()
        hl.addWidget(self.image, stretch=1)
        hl.addLayout(tool_layout, stretch=0)

        layout = QVBoxLayout()
        layout.addLayout(dir_layout)
        layout.addLayout(hl)

        wid = QWidget()
        wid.setLayout(layout)

        self.setCentralWidget(wid)

    def initDirLayout(self):

        button_dir = QPushButton("Обзор")
        button_dir.clicked.connect(self.getDirectory)
        button_img = QPushButton("Фото")
        button_img.clicked.connect(self.openfile)
        #button_img.setMaximumWidth(int(self.pathTextLine.size().width() * 0.6))

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(QLabel("Выберите папку с датасетом: "), 0, 0)
        grid.setColumnMinimumWidth(1, 5)
        grid.addWidget(self.pathTextLine, 0, 2)
        grid.setColumnMinimumWidth(3, 5)
        grid.addWidget(button_dir, 0, 4)
        grid.addWidget(button_img, 1, 0, 1, 5, alignment=Qt.AlignmentFlag.AlignHCenter)
        # минимальная длина строки пути (она же 2 колонка сетки)
        grid.setColumnMinimumWidth(2, 270)
        # растягивается только 2 колонка сетки (с множителем 1)
        grid.setColumnStretch(2, 1)

        return grid

    def initToolbar(self):
        button_recgn = QPushButton("Начать распознавание")
        button_recgn.clicked.connect(self.start_recogn_thread)
        checkbox_unknown = QCheckBox("Выделять неизвестных")
        checkbox_unknown.stateChanged.connect(self.check)

        l = QVBoxLayout()
        l.addWidget(checkbox_unknown)
        l.addWidget(button_recgn)
        l.addStretch()
        return l

    def recognize(self):
        self.centralWidget().setDisabled(True)

        img_data = getImage(self.imgpath, self.pathTextLine.text(), self.showUnknown)

        h, w, c = img_data.shape

        image = PixmapContainer(QImage(img_data.data, w, h, w * 3, QImage.Format.Format_RGB888))
        self.centralWidget().layout().replaceWidget(self.image, image)
        self.image.deleteLater()
        self.image = image

        self.centralWidget().setDisabled(False)

    def start_recogn_thread(self):
        th = threading.Thread(target=self.recognize)
        th.start()

    def check(self, state):
        if self.sender().isChecked():
            self.showUnknown = True
        else:
            self.showUnknown = False

    def getDirectory(self):
        dirlist = QFileDialog.getExistingDirectory(self, "Выбрать папку", ".")
        self.pathTextLine.setText(dirlist)

    def openfile(self):
        fname = QFileDialog.getOpenFileName(
            self,
            'Выберите фото для распознавания',
            '.',
            "Supported files (*.png;*.jpg;*.bmp);;PNG Files (*.png);;JPG Files (*.jpg);;BMP File (*.bmp)"
        )[0]
        if not fname.endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            #прописать уведомление о некорректном типе файла/недоступном
            return
        # сохраняем путь к фотографии в специальное поле (для глобальной логики)
        self.imgpath = fname

        image = PixmapContainer(fname)
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.centralWidget().layout().replaceWidget(self.image, image)
        self.image.deleteLater()
        self.image = image




app = QApplication([])
window = MainWindow()
window.show()
app.exec()
