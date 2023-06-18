from PyQt6.QtWidgets import QWidget, QMainWindow, QPushButton, \
    QFileDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QGridLayout, QCheckBox, QMessageBox
from PyQt6.QtGui import QIcon, QPixmap, QImage
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import numpy as np

from recognition import getImage


class PixmapContainer(QLabel):
    """
            Класс, наследующий QLabel с модификацией для масштабирования изображения
    """
    def __init__(self, pixmap, parent=None):
        super(PixmapContainer, self).__init__(parent)
        self._pixmap = QPixmap(pixmap)
        self.setMinimumSize(256, 256)  # needed to be able to scale down the image

    def resizeEvent(self, event):
        w = self.width()
        h = self.height()
        self.setPixmap(self._pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Распознавание лиц")
        self.setWindowIcon(QIcon('./visual/icon.png'))

        self.imgpath = None
        self.pathTextLine = QLineEdit("", )
        self.pathTextLine.setEnabled(False)
        self.showUnknown = False
        self.model = 'small'

        # анонимное изображение, запуск программы на анонимном изображении запрещен
        self.image = PixmapContainer('./visual/anon_img.png')
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        checkbox_altModel = QCheckBox("Более точное и долгое распознавание")
        checkbox_altModel.stateChanged.connect(self.modelSwitch)
        l = QVBoxLayout()
        l.addWidget(checkbox_unknown)
        l.addWidget(checkbox_altModel)
        l.addWidget(button_recgn)
        l.addStretch()
        return l

    def drawFaces(self, img_data):
        """
            Конвертация cv2 изображения в PixmapContainer и обновление изображения в gui

            :param img_data: стандартное cv2 изображение (RGB)
        """

        if img_data.shape == ():
            # уведомление о некорректном типе файла
            error = QMessageBox(self)
            error.setWindowTitle('Ошибка')
            error.setText('Произошло перемещение/удаление одного из обрабатываемых файлов')
            error.setInformativeText("Повторите попытку")
            error.setIcon(QMessageBox.Icon.Warning)
            error.setStandardButtons(QMessageBox.StandardButton.Ok)
            self.imgpath = None
            self.updateImage(PixmapContainer('./visual/anon_img.png'))
            error.exec()
        else:
            h, w, _ = img_data.shape
            image = PixmapContainer(QImage(img_data.data, w, h, w * 3, QImage.Format.Format_RGB888))
            self.updateImage(image)

        for button in self.centralWidget().findChildren(QPushButton):
            button.setDisabled(False)


    def start_recogn_thread(self):
        if self.pathTextLine.text() == '':
            error = QMessageBox(self)
            error.setWindowTitle('Ошибка')
            error.setText('Необходимо выбрать папку с известными изображениями')
            error.setInformativeText('Для корректной работы на каждой фотографии должно быть не более 1 человек\nПустая папка допускается, как и папка с посторонними файлами')
            error.setIcon(QMessageBox.Icon.Warning)
            error.setStandardButtons(QMessageBox.StandardButton.Ok)
            error.exec()
        elif self.imgpath is None:
            error = QMessageBox(self)
            error.setWindowTitle('Ошибка')
            error.setText('Необходимо выбрать изображение для распознавания')
            error.setIcon(QMessageBox.Icon.Warning)
            error.setStandardButtons(QMessageBox.StandardButton.Ok)
            error.exec()
        else:
            #self.centralWidget().setDisabled(True)
            #self.centralWidget().findChild(QPushButton, 'btnrecg').setDisabled(True)
            for button in self.centralWidget().findChildren(QPushButton):
                button.setDisabled(True)

            # сообщение об обработке
            lay = QVBoxLayout(self.image)
            loadlabel = QLabel("Обработка...")
            loadlabel.setStyleSheet("background-color: gainsboro; padding: 4px 10px;")
            lay.addWidget(loadlabel, alignment=Qt.AlignmentFlag.AlignCenter)

            self.worker = Worker(self.imgpath, self.pathTextLine.text(), self.showUnknown, self.model)
            self.worker.beep.connect(self.drawFaces)
            self.worker.start()

    def check(self, state):
        if self.sender().isChecked():
            self.showUnknown = True
        else:
            self.showUnknown = False

    def modelSwitch(self, state):
        if self.sender().isChecked():
            self.model = 'large'
        else:
            self.model = 'small'

    def getDirectory(self):
        dirlist = QFileDialog.getExistingDirectory(self, "Выбрать папку", ".")
        self.pathTextLine.setText(dirlist)

    def updateImage(self, new_image):
        """
            Обновление изображения в gui

            :param new_image: экземпляр QImage или производного от него класса
        """
        new_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.centralWidget().layout().replaceWidget(self.image, new_image)
        self.image.deleteLater()
        self.image = new_image

    def openfile(self):
        fname = QFileDialog.getOpenFileName(
            self,
            'Выберите фото для распознавания',
            '.',
            "Supported files (*.png;*.jpeg;*.jpg;*.bmp);;PNG Files (*.png);;JPG Files (*.jpg;*.jpeg);;BMP File (*.bmp)"
        )[0]
        if not fname:
            return
        elif not fname.endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            # уведомление о некорректном типе файла
            error = QMessageBox(self)
            error.setWindowTitle('Ошибка')
            error.setText('Выбранный Вами тип файла не поддерживается')
            error.setInformativeText("Поддерживаемые файлы: (*.png;*.jpeg;*.jpg;*.bmp)")
            error.setIcon(QMessageBox.Icon.Warning)
            error.setStandardButtons(QMessageBox.StandardButton.Ok)
            error.exec()
            return
        # сохраняем путь к фотографии в специальное поле (для глобальной логики)
        self.imgpath = fname
        image = PixmapContainer(fname)
        self.updateImage(image)


class Worker(QThread):
    """
            Класс, представляющий отдельный поток для запуска распознавания

            Вызывает метод getImage из модуля recognition при запуске
            Возвращает изображение по окончанию расчета с помощью сигнала beep
    """
    beep = pyqtSignal(np.ndarray)

    def __init__(self, imgpath, dirpath, shwunkn, model, parent=None):
        super(self.__class__, self).__init__(parent)
        self.imgpath = imgpath
        self.dirpath = dirpath
        self.shwunkn = shwunkn
        self.model = model

    def run(self):
        try:
            self.beep.emit(getImage(self.imgpath, self.dirpath, self.shwunkn, self.model))
        except:
            self.beep.emit(np.ndarray([]))


