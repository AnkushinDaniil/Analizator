# -----------------------------------------------------------
# Запуск и функции главного окна анализатора
#
# (C) 2022 Анкушин Даниил, Санкт-Петербург, Россия
# ООО "Анализ оптических систем"
# email ankushin.daniil42@gmail.com
# -----------------------------------------------------------
import csv
import os
import pickle

import numpy as np
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
import pyqtgraph as pg
from pyqtgraph import PlotWidget
import json
from Data import Signal

pg.setConfigOptions(antialias=True)


class Ui_MainWindow(object):
    """Графический интерфейс главного окна"""

    def __init__(self):
        self.signals = None
        self.filenames = None

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1050, 735)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.graph_widget = PlotWidget(self.centralwidget)
        self.graph_widget.setMinimumSize(QtCore.QSize(600, 300))
        self.graph_widget.setObjectName("graph_widget")
        self.verticalLayout_4.addWidget(self.graph_widget)
        self.graph_widget_zoom = PlotWidget(self.centralwidget)
        self.graph_widget_zoom.setMinimumSize(QtCore.QSize(600, 300))
        self.graph_widget_zoom.setObjectName("graph_widget_zoom")
        self.verticalLayout_4.addWidget(self.graph_widget_zoom)
        self.horizontalLayout.addLayout(self.verticalLayout_4)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.total_time = QtWidgets.QLineEdit(self.centralwidget)
        self.total_time.setObjectName("total_time")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.total_time)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.speed = QtWidgets.QLineEdit(self.centralwidget)
        self.speed.setObjectName("speed")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.speed)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.lambda_source = QtWidgets.QLineEdit(self.centralwidget)
        self.lambda_source.setObjectName("lambda_source")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lambda_source)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.source_bandwith = QtWidgets.QLineEdit(self.centralwidget)
        self.source_bandwith.setObjectName("source_bandwith")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.source_bandwith)
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.delta_n = QtWidgets.QLineEdit(self.centralwidget)
        self.delta_n.setObjectName("delta_n")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.delta_n)
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.ADC_frequency = QtWidgets.QLineEdit(self.centralwidget)
        self.ADC_frequency.setObjectName("ADC_frequency")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.ADC_frequency)
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.phase_modulation_frequency = QtWidgets.QLineEdit(self.centralwidget)
        self.phase_modulation_frequency.setObjectName("phase_modulation_frequency")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.phase_modulation_frequency)
        self.verticalLayout.addLayout(self.formLayout)
        self.graphType = QtWidgets.QComboBox(self.centralwidget)
        self.graphType.setObjectName("graphType")
        self.graphType.addItem("")
        self.graphType.addItem("")
        self.graphType.addItem("")
        self.graphType.addItem("")
        self.verticalLayout.addWidget(self.graphType)
        self.buildButton = QtWidgets.QPushButton(self.centralwidget)
        self.buildButton.setObjectName("buildButton")
        self.verticalLayout.addWidget(self.buildButton)
        self.horizontalLayout.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1050, 26))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.newButton = QtWidgets.QAction(MainWindow)
        self.newButton.setObjectName("newButton")
        self.openButton = QtWidgets.QAction(MainWindow)
        self.openButton.setObjectName("openButton")
        self.saveButton = QtWidgets.QAction(MainWindow)
        self.saveButton.setObjectName("saveButton")
        self.menu.addAction(self.newButton)
        self.menu.addAction(self.openButton)
        self.menu.addAction(self.saveButton)
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.add_functions()  # Добавление функционала к элементам интерфейса

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Analizator"))
        self.label.setText(_translate("MainWindow", "Время ввода, с"))
        self.total_time.setText(_translate("MainWindow", "30"))
        self.label_2.setText(_translate("MainWindow", "Скорость, мм/c"))
        self.speed.setText(_translate("MainWindow", "1"))
        self.label_3.setText(_translate("MainWindow", "Центральная длина волны источника, нм"))
        self.lambda_source.setText(_translate("MainWindow", "1560"))
        self.label_4.setText(_translate("MainWindow", "Ширина полосы источника, нм"))
        self.source_bandwith.setText(_translate("MainWindow", "45"))
        self.label_5.setText(_translate("MainWindow", "Разница эффективных показателей преломления волокна"))
        self.delta_n.setText(_translate("MainWindow", "0.0006086"))
        self.label_6.setText(_translate("MainWindow", "Частота АЦП, Гц"))
        self.ADC_frequency.setText(_translate("MainWindow", "500000"))
        self.label_7.setText(_translate("MainWindow", "Частота фазовой модуляции"))
        self.phase_modulation_frequency.setText(_translate("MainWindow", "0"))
        self.graphType.setItemText(0, _translate("MainWindow", "h-параметр"))
        self.graphType.setItemText(1, _translate("MainWindow", "Видность"))
        self.graphType.setItemText(2, _translate("MainWindow", "Интерференция"))
        self.graphType.setItemText(3, _translate("MainWindow", "Фильтрованная интерференция"))
        self.buildButton.setText(_translate("MainWindow", "Построить"))
        self.menu.setTitle(_translate("MainWindow", "Файл"))
        self.newButton.setText(_translate("MainWindow", "Новый"))
        self.openButton.setText(_translate("MainWindow", "Открыть"))
        self.saveButton.setText(_translate("MainWindow", "Сохранить"))

    def add_functions(self):
        """Добавление функционала к элементам интерфейса"""
        self.newButton.triggered.connect(self.new_file)
        self.buildButton.clicked.connect(self.draw_graph)
        self.saveButton.triggered.connect(self.save_file)
        # self.buildButton.clicked.connect()

    @staticmethod
    def show_error():
        """Вызов окна ошибки"""
        from PyQt5.QtWidgets import QMessageBox
        error = QMessageBox()
        error.setWindowTitle('Ошибка')
        error.setText('Неверно введены параметры')
        error.setIcon(QMessageBox.Warning)
        error.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        error.exec_()

    def str2float(self, string):
        """Перевод из строки в число"""
        try:
            return float(string)
        except ValueError:
            self.show_error()

    def set_signals(self, filenames, total_time, speed, lambda_source, source_bandwith, delta_n, ADC_frequency,
                    phase_modulation_frequency, pens):
        """Создание объектов класса "сигнал" внутри объекта класса главного окна"""
        # Считывание параметров из элементов графического интерфейса и преобразование их в числа
        float_parameters = [self.str2float(i) for i in [total_time, speed, lambda_source, source_bandwith, delta_n,
                                                        ADC_frequency, phase_modulation_frequency]]
        if all([not (parameter is None) for parameter in float_parameters]):  # Если все параметры введены правильно
            # Создание объектов класса "сигнал"
            self.signals = [Signal.Signal(np.fromfile(i), *float_parameters, name=i.split('/')[-1].split('.')[0],
                                          pen=pen) for i, pen in zip(filenames, pens)]

    def new_file(self):
        """Открытие файлов и дальнейшая их обработка"""
        print('Открытие файлов:')
        self.filenames, _ = QFileDialog.getOpenFileNames()  # Открытие файлов
        [print(filename) for filename in self.filenames]
        print()
        if self.filenames:  # Если список файлов не пустой
            n = len(self.filenames)
            colors = pg.colormap.get('CET-C1').color
            l = len(colors)
            k = l // n
            print('Подбор набора цветов для будущих графиков')
            # Подбор набора цветов для будущих графиков
            pens = [[round(255 * r), round(255 * g), round(256 * b)] for r, g, b, a in colors[::k]]
            # Создание объектов класса "сигнал"
            print('Создание объектов класса "сигнал"')
            self.set_signals(
                filenames=self.filenames,
                total_time=self.total_time.text(),
                speed=self.speed.text(),
                lambda_source=self.lambda_source.text(),
                source_bandwith=self.source_bandwith.text(),
                delta_n=self.delta_n.text(),
                ADC_frequency=self.ADC_frequency.text(),
                phase_modulation_frequency=self.phase_modulation_frequency.text(),
                pens=pens
            )

        if self.signals:
            # Если сигналы существуют
            self.draw_graph()  # Построить график

    def draw_graph(self):
        """Построение графиков"""
        print('Построение графиков')
        key = self.graphType.currentText()  # Создание ключа - название графика, который необходимо построить
        print(f'Выбранный график - {key}')
        # В зависимости от ключа будет создан словарь, который будет задавать дальнейшие ключи для построения графиков
        chart_dict = {
            'Видность': {
                'x_axis_name': 'Длина плеча интерферометра',
                'x_axis_unit': 'м',
                'y_axis_name': 'Видность',
                'y_axis_unit': ''
            },
            'h-параметр': {
                'x_axis_name': 'Длина волокна',
                'x_axis_unit': 'м',
                'y_axis_name': 'h-параметр',
                'y_axis_unit': 'дБ'
            },
            'Интерференция': {
                'x_axis_name': 'Длина плеча интерферометра',
                'x_axis_unit': 'м',
                'y_axis_name': 'Мощность, относительные единицы',
                'y_axis_unit': 'дБ'
            },
            'Фильтрованная интерференция': {
                'x_axis_name': 'Длина плеча интерферометра',
                'x_axis_unit': 'м',
                'y_axis_name': 'Мощность, относительные единицы',
                'y_axis_unit': 'дБ'
            }
        }[key]

        for plt in [self.graph_widget, self.graph_widget_zoom]:  # Строим графики в обоих виджетах
            plt.clear()  # Очищаем виджеты от предыдущих графиков
            plt.addLegend()
            # В зависимости от типа графика задается линейная или логарифмическая шкала
            plt.setLogMode(False, (False, True)[key == 'Видность'])
            # Задаем названия осей и единицы измерения
            plt.setLabel('bottom', chart_dict['x_axis_name'], chart_dict['x_axis_unit'])
            plt.setLabel('left', chart_dict['y_axis_name'], chart_dict['y_axis_unit'])
            plt.plotItem.getViewBox().setMouseMode(pg.ViewBox.RectMode)  # Настройка режима работы мыши
        for signal in self.signals:  # Для каждого сигнала в списке сигналов
            x, y = {
                'Видность': (signal.visibility_coordinates, signal.visibility),
                'h-параметр': (signal.h_parameter_coordinates, signal.h_parameter),
                'Интерференция': (signal.interference_coordinates, signal.interference),
                'Фильтрованная интерференция': (signal.denoised_interference_coordinates, signal.denoised_interference)
            }[key]  # Задаем значения по обеим координатам
            name, pen = signal.name, signal.pen  # Задаем имя и цвет графика
            print(f'Построение графика "{key}": {name}')
            for plt in [self.graph_widget, self.graph_widget_zoom]:  # Для каждого виджета
                # Строим графики
                plt.plot(x, y, name=name, pen=pen)
        for plt in [self.graph_widget, self.graph_widget_zoom]:
            plt.enableAutoRange('y', True)  # Автоматический зум 1:1
            plt.enableAutoRange('x', True)
        # Привязка зума между графиками
        lr = pg.LinearRegionItem()
        lr.setRegion((0, self.signals[0].beat_length))
        self.graph_widget.addItem(lr)

        def updatePlot():
            """Настройка обновления графика при зуме"""
            self.graph_widget_zoom.setXRange(*lr.getRegion(), padding=0)

        def updateRegion():
            """Настройка обновления региона при зуме"""
            lr.setRegion(self.graph_widget_zoom.getViewBox().viewRange()[0])

        lr.sigRegionChanged.connect(updatePlot)
        self.graph_widget_zoom.sigXRangeChanged.connect(updateRegion)
        updatePlot()

    def save_file(self):
        directory = '_'.join([signal.name for signal in self.signals])
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, extension = QFileDialog.getSaveFileName(
            parent=None, caption="Сохранить", directory=directory,
            filter=".json;;txt;;.pkl;;.mat;;.csv;;.png", options=options
        )

        def sig2dict(sig_list: list):
            for sig in sig_list:
                sig_dict = {
                    sig.name: sig.__dict__
                }
            return sig_dict

        if not ((filename is None) | (extension is None)):
            signal_dict = sig2dict(self.signals)
            if extension == '.csv':
                if not os.path.exists(directory):
                    os.mkdir(directory)
                for name, signal in signal_dict.items():
                    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in signal.items()]))
                    path = os.path.join(directory, name)
                    df.to_csv(f"{path}{extension}", index=False)
            else:
                with open(f"{directory}{extension}", "w") as file:
                    if extension == '.json':
                        signal_json = json.dumps(signal_dict)
                        file.write(signal_json)
                    elif extension == '.txt':
                        file.write(str(signal_dict))
                    elif extension == '.pkl':
                        pickle.dump(signal_dict, file)




if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    # Настройка стиля для всех ОС:
    app.setStyle("Fusion")

    # Переключение на темные цвета:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    # Код функции сгенерирован с помощью pyuic5
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.showFullScreen()
    sys.exit(app.exec_())
