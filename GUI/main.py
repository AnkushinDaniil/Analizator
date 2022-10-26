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
from scipy.io import savemat, loadmat

from Data.Signal import Signal
from mainwindow import Ui_MainWindow

pg.setConfigOptions(antialias=True)


class MainWindow(Ui_MainWindow):
    """Графический интерфейс главного окна"""

    def __init__(self):
        super().__init__()
        self.key = None
        self.signals = []
        self.filenames = None

    def add_functions(self):
        """Добавление функционала к элементам интерфейса"""
        self.newButton.triggered.connect(self.new_file)
        self.buildButton.clicked.connect(self.draw_graph)
        self.saveButton.triggered.connect(self.save_file)
        self.openButton.triggered.connect(self.open_file)
        self.clear_graphButton.clicked.connect(self.clear_graph)
        self.color_resetButton.clicked.connect(self.color_reset)
        self.clear_dataButton.clicked.connect(self.clear_data)

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
            for i, pen in zip(filenames, pens):
                signal = Signal()
                signal.set_signal(
                    interference=np.fromfile(i),
                    speed=speed,
                    total_time=total_time,
                    lambda_source=lambda_source,
                    source_bandwith=source_bandwith,
                    delta_n=delta_n,
                    ADC_frequency=ADC_frequency,
                    phase_modulation_frequency=phase_modulation_frequency,
                    name=i.split('/')[-1].split('.')[0],
                    pen=pen
                )
                self.signals.append(signal)
        self.saveButton.setEnabled(True)

    def new_file(self):
        """Открытие файлов и дальнейшая их обработка"""
        print('Открытие файлов:')
        self.filenames, _ = QFileDialog.getOpenFileNames()  # Открытие файлов
        [print(filename) for filename in self.filenames]
        print()
        if self.filenames:  # Если список файлов не пустой
            pens = self.generate_pens(len(self.filenames))
            # Создание объектов класса "сигнал"
            print('Создание объектов класса "сигнал"')
            self.set_signals(
                filenames=self.filenames,
                total_time=self.str2float(self.total_time.text()),
                speed=self.str2float(self.speed.text()),
                lambda_source=self.str2float(self.lambda_source.text()),
                source_bandwith=self.str2float(self.source_bandwith.text()),
                delta_n=self.str2float(self.delta_n.text()),
                ADC_frequency=self.str2float(self.ADC_frequency.text()),
                phase_modulation_frequency=self.str2float(self.phase_modulation_frequency.text()),
                pens=pens
            )
            self.newButton.setEnabled(True)

        if self.signals:
            # Если сигналы существуют
            self.draw_graph()  # Построить график

    def draw_graph(self):
        """Построение графиков"""
        if self.signals:
            print('Построение графиков')
            self.clear_graph()
            self.key = self.graphType.currentText()  # Создание ключа - название графика, который необходимо построить
            print(f'Выбранный график - {self.key}')
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
                    'y_axis_name': 'Мощность',
                    'y_axis_unit': 'Относительные единицы'
                },
                'Фильтрованная интерференция': {
                    'x_axis_name': 'Длина плеча интерферометра',
                    'x_axis_unit': 'м',
                    'y_axis_name': 'Мощность',
                    'y_axis_unit': 'Относительные единицы'
                },
                'Фильтр Чебышёва': {
                    'x_axis_name': 'Частота',
                    'x_axis_unit': 'Гц',
                    'y_axis_name': 'Амплитуда',
                    'y_axis_unit': 'Относительные единицы'
                }
            }[self.key]

            for plt in [self.graph_widget, self.graph_widget_zoom]:  # Строим графики в обоих виджетах
                plt.addLegend()
                # В зависимости от типа графика задается линейная или логарифмическая шкала
                plt.setLogMode(False, (False, True)[self.key == 'Видность'])
                # Задаем названия осей и единицы измерения
                plt.setLabel('bottom', chart_dict['x_axis_name'], chart_dict['x_axis_unit'])
                plt.setLabel('left', chart_dict['y_axis_name'], chart_dict['y_axis_unit'])
                plt.plotItem.getViewBox().setMouseMode(pg.ViewBox.RectMode)  # Настройка режима работы мыши
            for signal in self.signals:  # Для каждого сигнала в списке сигналов
                x, y = {
                    'Видность': (signal.visibility_coordinates, signal.visibility),
                    'h-параметр': (signal.h_parameter_coordinates, signal.h_parameter),
                    'Интерференция': (signal.interference_coordinates, signal.interference),
                    'Фильтрованная интерференция': (
                    signal.denoised_interference_coordinates, signal.denoised_interference),
                    'Фильтр Чебышёва': (signal.cheb2_x, signal.cheb2_y)
                }[self.key]  # Задаем значения по обеим координатам
                name, pen = signal.name, signal.pen  # Задаем имя и цвет графика
                print(f'Построение графика "{self.key}": {name}')
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

    def clear_graph(self):
        for plt in [self.graph_widget, self.graph_widget_zoom]:
            plt.clear()

    def color_reset(self):
        if self.signals:
            pens = self.generate_pens(len(self.signals))
            for signal, pen in zip(self.signals, pens):
                signal.pen = pen
            self.clear_graph()
            self.draw_graph()

    @staticmethod
    def generate_pens(n: int):
        colors = pg.colormap.get('CET-C1').color
        l = len(colors)
        k = l // n
        print('Подбор набора цветов для графиков')
        # Подбор набора цветов для графиков
        pens = [[round(255 * r), round(255 * g), round(256 * b)] for r, g, b, a in colors[::k]]
        return pens

    def clear_data(self):
        self.signals = []
        self.clear_graph()



    def save_file(self):
        """Экспорт файлов"""
        if self.signals:
            directory = '_'.join([signal.name for signal in self.signals])
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            filename, extension = QFileDialog.getSaveFileName(
                parent=None, caption="Сохранить", directory=directory,
                filter="*.json;;*.txt;;*.pkl;;*.mat;;*.csv;;*.png", options=options
            )

        def sig2dict(sig_list: list):
            sig_dict = dict()
            for sig in sig_list:
                sig_name = sig.name
                sig_dict[sig_name] = dict()
                for key, value in sig.__dict__.items():
                    if isinstance(value, np.ndarray):
                        sig_dict[sig_name][key] = value.tolist()
                    else:
                        sig_dict[sig_name][key] = value
            return sig_dict

        if filename:
            signal_dict = sig2dict(self.signals)
            extension = extension.split('*')[-1]
            if extension == '.csv':
                if not os.path.exists(directory):
                    os.mkdir(directory)
                for name, signal in signal_dict.items():
                    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in signal.items()]))
                    path = os.path.join(directory, name)
                    df.to_csv(f"{path}{extension}", index=False)
            elif extension == '.mat':
                short_keys_signal_dict = dict()
                for name, sig_dict in signal_dict.items():
                    short_name = name[:31]
                    short_keys_signal_dict[short_name] = dict()
                    for key, value in sig_dict.items():
                        short_key = key[:31]
                        if value:
                            short_keys_signal_dict[short_name][short_key] = value
                savemat(f"{directory}{extension}", short_keys_signal_dict)
            elif extension == '.pkl':
                with open(f"{directory}{extension}", "wb") as file:
                    pickle.dump(signal_dict, file)
            else:
                with open(f"{directory}{extension}", "w") as file:
                    if extension == '.json':
                        signal_json = json.dumps(signal_dict)
                        file.write(signal_json)
                    elif extension == '.txt':
                        file.write(str(signal_dict))

    def open_file(self):
        print('Открытие файлов:')
        self.filenames, extension = QFileDialog.getOpenFileNames(
            filter="*.json;;*.txt;;*.pkl;;*.mat;;*.csv")  # Открытие файлов
        [print(filename) for filename in self.filenames]
        extension = extension.split('*')[-1]

        if self.filenames:  # Если список файлов не пустой
            for filename in self.filenames:
                if extension == '.json':
                    with open(filename) as file:
                        signal_dict: dict = json.load(file)
                        for item in signal_dict.values():
                            signal = Signal()
                            signal.read_signal(signal_dict=item)
                            self.signals.append(signal)
        self.saveButton.setEnabled(True)
        self.draw_graph()


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
    main_window = QtWidgets.QMainWindow()
    ui = MainWindow()
    ui.setupUi(main_window)
    ui.add_functions()  # Добавление функционала к элементам интерфейса
    main_window.showMaximized()
    sys.exit(app.exec_())
