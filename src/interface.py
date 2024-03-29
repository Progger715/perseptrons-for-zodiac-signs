from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPen
from PyQt5.QtCore import Qt, QPoint
from PIL import Image
from pathlib import Path
import threading

from PyQt5.QtWidgets import QDesktopWidget

from src import perceptron


# Класс для создания загрузочного окна
class WorkerMessageBox(QtWidgets.QMessageBox):
    started = QtCore.pyqtSignal()  # Сигнал о начале выполнения задачи
    finished = QtCore.pyqtSignal()  # Сигнал о завершении выполнения задачи

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Learning ....")
        self.setText("Система обучается, пожалуйста подождите ...")
        self.setStandardButtons(QtWidgets.QMessageBox.NoButton)
        self.finished.connect(self.accept)  # Привязка сигнала к методу accept
        self.setStyleSheet(open("../styles/style.qss", "r").read())  # применение стилей
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../styles/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        # Получение размеров экрана
        screen_geometry = QDesktopWidget().screenGeometry()
        window_width = self.width()
        window_height = self.height()
        # Рассчет координат для центрирования окна
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2

        self.move(x, y)

    # Выполнение функции в отдельном потоке
    def execute(self, func):
        threading.Thread(target=self._execute, args=(func, ()), daemon=True).start()  # Создание и запуск потока
        return self.exec_()  # Отображение окна с сообщением и ожидание завершения

    def _execute(self, func, args):
        self.started.emit()  # Генерация сигнала о начале выполнения
        func(*args)  # Вызов переданной функции с аргументами
        self.finished.emit()  # Генерация сигнала о завершении выполнения


class Interface(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # настройка главного окна
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)  # Запретить изменение размера
        self.setStyleSheet(open("../styles/style.qss", "r").read())  # применение стилей
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../styles/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        self.zodiac_signs_rus = {"Aries": "Овен", "Taurus": "Телец", "Gemini": "Близнецы",
                                 "Cancer": "Рак", "Leo": "Лев", "Virgo": "Дева",
                                 "Libra": "Весы", "Scorpio": "Скорпион", "Sagittarius": "Стрелец",
                                 "Capricorn": "Козерог", "Aquarius": "Водолей", "Pisces": "Рыбы"}

        # все компоненты
        self.centralwidget = QtWidgets.QWidget(self)
        self.verticalLayout_central_widget = QtWidgets.QVBoxLayout(self.centralwidget)
        self.frame_labels = QtWidgets.QFrame(self.centralwidget)
        self.verticalLayout_for_frame_labels = QtWidgets.QVBoxLayout(self.frame_labels)
        self.label_output = QtWidgets.QLabel(self.frame_labels)

        self.frame_buttons_detect = QtWidgets.QFrame(self.centralwidget)
        self.pushButton_train = QtWidgets.QPushButton(self.frame_buttons_detect)
        self.pushButton_detect = QtWidgets.QPushButton(self.frame_buttons_detect)
        self.combo_box_response_options = QtWidgets.QComboBox()
        self.horizontalLayout_frame_buttons_detect = QtWidgets.QHBoxLayout(self.frame_buttons_detect)

        self.frame_canvas = QtWidgets.QFrame(self.centralwidget)
        self.label_for_canvas = QtWidgets.QLabel()
        self.verticallLayout_canvas_frame = QtWidgets.QHBoxLayout(self.frame_canvas)

        self.frame_buttons_canvas = QtWidgets.QFrame(self.centralwidget)
        self.pushButton_clear_all = QtWidgets.QPushButton(self.frame_buttons_canvas)
        self.pushButton_clear_mode = QtWidgets.QPushButton(self.frame_buttons_canvas)
        self.pushButton_pen_mode = QtWidgets.QPushButton(self.frame_buttons_canvas)
        self.horizontalLayout_frame_buttons_canvas = QtWidgets.QHBoxLayout(self.frame_buttons_canvas)

        # настройка всех компонентов
        self.setup_ui()

        # настройки рисования
        self.brush_color = Qt.black
        self.brush_size = 9
        self.last_point = QPoint()

        self.show()

    def setup_ui(self):
        self.setObjectName("MainWindow")
        self.resize(339, 432)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)

        self.frame_buttons_canvas.setMaximumSize(QtCore.QSize(16777215, 45))
        self.frame_buttons_canvas.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_buttons_canvas.setFrameShadow(QtWidgets.QFrame.Raised)
        self.horizontalLayout_frame_buttons_canvas.setContentsMargins(-1, 0, -1, 0)

        # pushButton_pen_mode
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../styles/icons/карандаш.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_pen_mode.setIcon(icon)
        self.pushButton_pen_mode.clicked.connect(self.click_pen_mode)
        self.horizontalLayout_frame_buttons_canvas.addWidget(self.pushButton_pen_mode)

        # pushButton_clear_mode
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../styles/icons/ластик.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_clear_mode.setIcon(icon1)
        self.pushButton_clear_mode.clicked.connect(self.click_clear_mode)
        self.horizontalLayout_frame_buttons_canvas.addWidget(self.pushButton_clear_mode)

        # pushButton_clear_all
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("../styles/icons/очистить2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_clear_all.setIcon(icon2)
        self.pushButton_clear_all.clicked.connect(self.click_clear_all)
        self.horizontalLayout_frame_buttons_canvas.addWidget(self.pushButton_clear_all)
        self.verticalLayout_central_widget.addWidget(self.frame_buttons_canvas)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_canvas.sizePolicy().hasHeightForWidth())
        self.frame_canvas.setSizePolicy(sizePolicy)
        self.frame_canvas.setMaximumSize(QtCore.QSize(1000, 1000))
        self.frame_canvas.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.frame_canvas.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_canvas.setFrameShadow(QtWidgets.QFrame.Raised)

        canvas = QtGui.QPixmap(256, 256)
        canvas.fill(Qt.white)
        self.label_for_canvas.setPixmap(canvas)
        self.verticallLayout_canvas_frame.addItem(
            QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        self.verticallLayout_canvas_frame.addWidget(self.label_for_canvas)
        self.verticallLayout_canvas_frame.addItem(
            QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        self.verticalLayout_central_widget.addWidget(self.frame_canvas)

        self.frame_buttons_detect.setMaximumSize(QtCore.QSize(16777215, 60))
        self.frame_buttons_detect.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_buttons_detect.setFrameShadow(QtWidgets.QFrame.Raised)

        # pushButton_detect
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("../styles/icons/распознать.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_detect.setIcon(icon3)
        self.pushButton_detect.clicked.connect(self.click_detect)
        self.horizontalLayout_frame_buttons_detect.addWidget(self.pushButton_detect)

        # pushButton_train
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("../styles/icons/обучить.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_train.setIcon(icon4)
        self.pushButton_train.clicked.connect(self.click_train)
        self.horizontalLayout_frame_buttons_detect.addWidget(self.pushButton_train)
        self.verticalLayout_central_widget.addWidget(self.frame_buttons_detect)

        # Добавление вариантов в комбо-бокс
        for sign in self.zodiac_signs_rus.values():
            self.combo_box_response_options.addItem(sign)
        self.combo_box_response_options.currentIndexChanged.connect(self.handle_combobox_selection)

        self.frame_labels.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_labels.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_labels.setObjectName("frame_labels")

        self.label_output.setOpenExternalLinks(False)
        self.label_output.setObjectName("label_output")
        self.verticalLayout_for_frame_labels.addWidget(self.label_output)
        self.verticalLayout_central_widget.addWidget(self.frame_labels)
        self.setCentralWidget(self.centralwidget)

        self.retranslate_ui()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslate_ui(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "Perceptron"))
        self.pushButton_pen_mode.setText(_translate("MainWindow", "карандаш"))
        self.pushButton_pen_mode.setShortcut(_translate("MainWindow", "Ctrl+P"))
        self.pushButton_clear_mode.setText(_translate("MainWindow", "ластик"))
        self.pushButton_clear_mode.setShortcut(_translate("MainWindow", "Ctrl+E"))
        self.pushButton_clear_all.setText(_translate("MainWindow", "очистить"))
        self.pushButton_clear_all.setShortcut(_translate("MainWindow", "Ctrl+C"))
        self.pushButton_detect.setText(_translate("MainWindow", "распознать"))
        self.pushButton_detect.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.pushButton_train.setText(_translate("MainWindow", "обучить"))
        self.pushButton_train.setShortcut(_translate("MainWindow", "Ctrl+L"))
        self.label_output.setText(_translate("MainWindow", "Здесь будет отображен ответ системы"))

    # метод для рисования на холсте
    def mouseMoveEvent(self, e):
        local_pos = self.label_for_canvas.mapFromGlobal(e.globalPos())
        if self.last_point.isNull():
            self.last_point = local_pos
        painter = QtGui.QPainter(self.label_for_canvas.pixmap())
        painter.setPen(QPen(self.brush_color, self.brush_size, Qt.PenStyle.SolidLine))
        painter.drawLine(self.last_point, local_pos)
        self.last_point = local_pos
        # painter.end()
        self.update()

    # обнулить значение последней точки при отпускании кнопки мыши
    def mouseReleaseEvent(self, event):
        self.last_point = QPoint()

    def click_clear_mode(self):
        self.brush_color = Qt.white

    def click_pen_mode(self):
        self.brush_color = Qt.black

    def click_clear_all(self):
        clear_canvas = QtGui.QPixmap(256, 256)
        clear_canvas.fill(Qt.white)
        self.label_for_canvas.setPixmap(clear_canvas)

    def click_detect(self):
        file_path = Path(Path.cwd().parent, "picture reads", "Image1.png")
        self._save_image(file_path)
        path_to_compressed_image = self._compress_image(file_path)
        answer = perceptron.identify_image(path_to_compressed_image)  # раскомментировать при работе
        print(answer)
        self.label_output.setText(f"Вы нарисовали: {answer} - {self.zodiac_signs_rus[answer]}")

    # Показать раскрывающийся список (комбо-бокс)
    def click_train(self):
        # Получение глобальных координат кнопки
        button_global_pos = self.pushButton_train.mapToGlobal(self.pushButton_train.rect().bottomLeft())
        # Показать раскрывающийся список по указанным координатам
        self.combo_box_response_options.move(button_global_pos)
        self.combo_box_response_options.showPopup()

    # Обработка выбора варианта в комбо-боксе
    def handle_combobox_selection(self, index):
        selected_option = self.combo_box_response_options.itemText(index)
        print(f"Выбран вариант: {selected_option}")

        image_for_identy = Path(Path.cwd().parent, "picture reads", "compressed_image.png")
        perceptron.init_weights()
        answer = perceptron.train_with_teacher(index, image_for_identy)
        print()
        self.label_output.setText(f"Система обучилась и определила: {answer}")

    # сохранить нарисованное изображение
    def _save_image(self, file_path):
        if file_path:
            self.label_for_canvas.pixmap().save(file_path.__str__())

    # сжать изображение
    @staticmethod
    def _compress_image(file_path: Path):
        image = Image.open(file_path)
        path_to_compressed_image = file_path.parent.joinpath("compressed_image.png")
        new_size = (32, 32)
        small_image = image.resize(new_size)
        small_image.save(path_to_compressed_image)
        return path_to_compressed_image


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    # Создание и отображение загрузочного окна
    msgBox = WorkerMessageBox()
    msgBox.execute(perceptron.start_perceptron)  # Выполнение обучения в отдельном потоке

    ui = Interface()
    sys.exit(app.exec_())
