from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import sys
import pyqtgraph as pg

import Data.Signal


class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('analizator_GUI.ui', self) # Load the .ui file
        self.show() # Show the GUI
        self.set_defaults()
        self.add_functions()

    def set_defaults(self):
        self.interferenceWidget.canvas.axes.set_ylabel('Сигнал на фотоприемнике, В')
        self.interferenceWidget.canvas.axes.set_xlabel('Длина плеча интерферометра, м')
        self.interferenceWidget.canvas.figure.tight_layout()
        self.visibilityWidget.canvas.axes.set_ylabel('Видность,отн. ед.')
        self.visibilityWidget.canvas.axes.set_xlabel('Длина плеча интерферометра, м')
        self.visibilityWidget.canvas.figure.tight_layout()
        self.total_time.setText('30')
        self.speed.setText('1')
        self.lambda_source.setText('1560')
        self.source_bandwith.setText('45')
        self.delta_n.setText('6.086e-04')



    def add_functions(self):
        self.openButton.clicked.connect(self.open_file)
        # self.calculateButton.clicked.connect(self.calculate)

        self.total_time.mousePressEvent = lambda _: self.total_time.selectAll()
        self.speed.mousePressEvent = lambda _: self.speed.selectAll()
        self.lambda_source.mousePressEvent = lambda _: self.lambda_source.selectAll()
        self.source_bandwith.mousePressEvent = lambda _: self.source_bandwith.selectAll()
        self.delta_n.mousePressEvent = lambda _: self.delta_n.selectAll()

    def open_file(self):
        self.__filemane, _ = QFileDialog.getOpenFileName()
        self.label_filename.setText(self.__filemane)
        float_parameters = self.str2float(self.total_time.text(), self.speed.text(), self.lambda_source.text(),
                                          self.source_bandwith.text(), self.delta_n.text())
        if isinstance(float_parameters, list) & (self.__filemane != ''):
            if len(float_parameters) == 5:

                self.signal = Data.Signal.Signal(np.fromfile(self.__filemane), *float_parameters)
                self.draw_interference(*self.signal.get_interference())
            else:
                self.show_error()

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
        from PyQt5.QtWidgets import QMessageBox
        error = QMessageBox()
        error.setWindowTitle('Ошибка')
        error.setText('Неверно введены параметры')
        error.setIcon(QMessageBox.Warning)
        error.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)

    def draw_interference(self, x, y):
        # self.interferenceWidget.canvas.axes.cla()
        self.interferenceWidget.canvas.axes.plot(x, y, linewidth=0.5)
        # self.interferenceWidget.canvas.axes.set_yscale('log')
        self.interferenceWidget.canvas.figure.tight_layout()
        self.interferenceWidget.canvas.draw()


def main():
    app = QApplication(sys.argv)
    window = Ui()
    app.exec_()

if __name__ == '__main__':
    main()