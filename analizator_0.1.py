# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'analizator_0.1.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure



class MplCanvas(FigureCanvasQTAgg):

    def __init__(self):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.interference = self.Chart(MainWindow)
        self.verticalLayout.addWidget(self.interference.chart)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_filename = QtWidgets.QLabel(self.centralwidget)
        self.label_filename.setAlignment(QtCore.Qt.AlignCenter)
        self.label_filename.setObjectName("label_filename")
        self.horizontalLayout.addWidget(self.label_filename)
        self.openButton = QtWidgets.QPushButton(self.centralwidget)
        self.openButton.setObjectName("openButton")
        self.horizontalLayout.addWidget(self.openButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.total_time_title = QtWidgets.QLabel(self.centralwidget)
        self.total_time_title.setObjectName("total_time_title")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.total_time_title)
        self.total_time = QtWidgets.QLineEdit(self.centralwidget)
        self.total_time.setObjectName("total_time")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.total_time)
        self.speed_title = QtWidgets.QLabel(self.centralwidget)
        self.speed_title.setObjectName("speed_title")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.speed_title)
        self.speed = QtWidgets.QLineEdit(self.centralwidget)
        self.speed.setObjectName("speed")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.speed)
        self.lambda_source_title = QtWidgets.QLabel(self.centralwidget)
        self.lambda_source_title.setObjectName("lambda_source_title")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.lambda_source_title)
        self.lambda_source = QtWidgets.QLineEdit(self.centralwidget)
        self.lambda_source.setObjectName("lambda_source")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lambda_source)
        self.source_bandwith_title = QtWidgets.QLabel(self.centralwidget)
        self.source_bandwith_title.setObjectName("source_bandwith_title")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.source_bandwith_title)
        self.source_bandwith = QtWidgets.QLineEdit(self.centralwidget)
        self.source_bandwith.setObjectName("source_bandwith")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.source_bandwith)
        self.delta_n_title = QtWidgets.QLabel(self.centralwidget)
        self.delta_n_title.setObjectName("delta_n_title")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.delta_n_title)
        self.delta_n = QtWidgets.QLineEdit(self.centralwidget)
        self.delta_n.setObjectName("delta_n")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.delta_n)
        self.k_disp_title = QtWidgets.QLabel(self.centralwidget)
        self.k_disp_title.setObjectName("k_disp_title")
        self.formLayout_2.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.k_disp_title)
        self.k_disp = QtWidgets.QLCDNumber(self.centralwidget)
        self.k_disp.setObjectName("k_disp")
        self.formLayout_2.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.k_disp)
        self.k_ekst_title = QtWidgets.QLabel(self.centralwidget)
        self.k_ekst_title.setObjectName("k_ekst_title")
        self.formLayout_2.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.k_ekst_title)
        self.k_ekst = QtWidgets.QLCDNumber(self.centralwidget)
        self.k_ekst.setObjectName("k_ekst")
        self.formLayout_2.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.k_ekst)
        self.calculateButton = QtWidgets.QPushButton(self.centralwidget)
        self.calculateButton.setObjectName("calculateButton")
        self.formLayout_2.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.calculateButton)
        self.horizontalLayout_2.addLayout(self.formLayout_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout_3.addWidget(self.line_2)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_3.addWidget(self.label_3)
        self.visibility = self.Chart(MainWindow)
        self.verticalLayout_3.addWidget(self.visibility.chart)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_3.addWidget(self.line)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.set_defaults()

        self.add_functions()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", " Анализатор"))
        self.label_2.setText(_translate("MainWindow", "Интерференционная картина"))
        self.label_filename.setText(_translate("MainWindow", "Имя файла"))
        self.openButton.setText(_translate("MainWindow", "Открыть файл"))
        self.total_time_title.setText(_translate("MainWindow", "Время ввода [с]"))
        self.speed_title.setText(_translate("MainWindow", "Скорость [мм/сек]"))
        self.lambda_source_title.setText(_translate("MainWindow", "Центральная длина волны источника [нм]"))
        self.source_bandwith_title.setText(_translate("MainWindow", "Ширина полосы источника в нанометрах [нм]"))
        self.delta_n_title.setText(_translate("MainWindow", "Разница эффективных показателей преломления волокна"))
        self.k_disp_title.setText(_translate("MainWindow", "Коэффициент дисперсии"))
        self.k_ekst_title.setText(_translate("MainWindow", "Коэффициент экстринкции"))
        self.calculateButton.setText(_translate("MainWindow", "Вычислить"))
        self.label_3.setText(_translate("MainWindow", "Картина видности"))

    def set_defaults(self):
        self.total_time.setText('30')
        self.speed.setText('1')
        self.lambda_source.setText('1560')
        self.source_bandwith.setText('45')
        self.delta_n.setText('6.086e-04')

    def add_functions(self):

        self.openButton.clicked.connect(self.open_file)
        self.calculateButton.clicked.connect(self.calculate)

        self.total_time.mousePressEvent = lambda _: self.total_time.selectAll()
        self.speed.mousePressEvent = lambda _: self.speed.selectAll()
        self.lambda_source.mousePressEvent = lambda _: self.lambda_source.selectAll()
        self.source_bandwith.mousePressEvent = lambda _: self.source_bandwith.selectAll()
        self.delta_n.mousePressEvent = lambda _: self.delta_n.selectAll()

    class Chart:

        def __init__(self, MainWindow):
            self.sc = MplCanvas()
            self.sc.axes.plot()

            self.toolbar = NavigationToolbar(self.sc, MainWindow)

            self.layout = QtWidgets.QVBoxLayout()
            self.layout.addWidget(self.toolbar)
            self.layout.addWidget(self.sc)

            self.chart = QtWidgets.QWidget()
            self.chart.setLayout(self.layout)

    def open_file(self):
        self.__filemane, _ = QFileDialog.getOpenFileName()
        self.label_filename.setText(self.__filemane)
        float_parameters = self.str2float(self.total_time.text(), self.speed.text(), self.lambda_source.text(),
                                          self.source_bandwith.text(), self.delta_n.text())
        if isinstance(float_parameters, list) & (self.__filemane != ''):
            if len(float_parameters) == 5:
                self.signal = self.Signal(np.fromfile(self.__filemane), *float_parameters)
                self.draw_interference()
            else:
                self.show_error()

    def draw_interference(self):
        self.interference.sc.axes.cla()
        self.interference.sc.axes.plot(self.signal.get_signal()[0], self.signal.get_signal()[1], linewidth=0.5)
        self.interference.sc.axes.set_xlabel('Длина волокна, м')
        self.interference.sc.axes.set_ylabel('Сигнал на фотоприемнике, В')
        self.interference.sc.fig.tight_layout()
        self.interference.sc.draw()

    def drow_visibility(self, visibility_data):
        self.visibility.sc.axes.cla()
        self.visibility.sc.axes.plot(visibility_data[0], visibility_data[1], linewidth=0.5)
        self.visibility.sc.axes.set_yscale('log')
        self.visibility.sc.axes.set_xlabel('Длина волокна, м')
        self.visibility.sc.axes.set_ylabel('Видность, отн. ед.')
        self.visibility.sc.fig.tight_layout()
        self.visibility.sc.draw()

    def calculate(self):
        self.__visibility = self.signal.get_visibility()
        self.drow_visibility(self.__visibility)

    def str2float(self, *args):
        try:
            res = []
            for i in args:
                res.append(float(i))
            return res
        except ValueError:
            self.show_error()

    @staticmethod
    def show_error():
        error = QMessageBox()
        error.setWindowTitle('Ошибка')
        error.setText('Неверно введены параметры')
        error.setIcon(QMessageBox.Warning)
        error.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)

        error.exec_()

    class Signal:

        def __init__(self, signal, speed, total_time, lambda_source, source_bandwith, delta_n):
            self.set_signal(signal, speed, total_time, lambda_source, source_bandwith, delta_n)

        def set_signal(self, signal, speed, total_time, lambda_source, source_bandwith, delta_n):
            if self.__check_signal(signal, speed, total_time, lambda_source, source_bandwith, delta_n):
                n = np.size(signal)
                speed = speed / 1000
                self.n_to_length = total_time*speed/n
                coordinates = np.arange(0, n, 1, dtype=float) * self.n_to_length
                self.__signal = (coordinates, signal)
                self.__signal = self.__set_0(self.__signal)

        @staticmethod
        def __check_signal(signal, speed, total_time, lambda_source, source_bandwith, delta_n):
            return all((isinstance(signal, np.ndarray), isinstance(speed, float),
                        isinstance(total_time, float), isinstance(lambda_source, float),
                        isinstance(source_bandwith, float), isinstance(delta_n, float)))

        @staticmethod
        def __set_0(signal):
            from scipy.signal import find_peaks

            x = signal[0]
            y = signal[1]
            peaks, _ = find_peaks(y)
            i = np.where(y == np.sort(y[peaks])[~0])

            x = x - x[i]

            return x, y

        def get_signal(self):
            return self.__signal

        def get_visibility(self):
            self.__denoised_signal = self.__remove_noise(self.__signal)
            self.__periodicity_of_the_interference_pattern =\
                self.__calculate_interference_pattern_periodicity(self.__denoised_signal[1])
            self.__visibility = self.__calculate_visibility(self.__denoised_signal, self.__periodicity_of_the_interference_pattern)
            self.__visibility = self.__set_0(self.__visibility)
            return self.__visibility

        @staticmethod
        def __remove_noise(signal):
            from scipy.signal import find_peaks
            span = int(signal[1].shape[0] / len(find_peaks(signal[1])[0]))
            denoised_signal = np.convolve(signal[1], np.ones(span * 2 + 1) / (span * 2 + 1), mode="same")[span:~span]
            new_coordinates = signal[0][span:~span]
            return new_coordinates, denoised_signal

        @staticmethod
        def __calculate_interference_pattern_periodicity(denoised_signal):
            from scipy.signal import find_peaks
            top_values = denoised_signal[denoised_signal > np.quantile(denoised_signal, 0.9999)]
            peaks, _ = find_peaks(top_values)
            return int(top_values.shape[0] / peaks.shape[0] * 10)

        def __calculate_visibility(self, denoised_signal, span):
            splited_denoised_signal = np.array_split(denoised_signal[1], denoised_signal[1].shape[0] // span)
            maximum = (np.max(i) for i in splited_denoised_signal)
            minimum = (np.min(i) for i in splited_denoised_signal)
            visibility = np.fromiter(((ma - mi) / (ma + mi) for ma, mi in zip(maximum, minimum)), float)
            visibility_coordinate = np.linspace(np.min(denoised_signal[0]), np.max(denoised_signal[0]),
                                                num=visibility.shape[0])
            return visibility_coordinate, visibility



def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()