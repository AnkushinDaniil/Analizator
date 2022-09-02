from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import sys
import os

import Data.Signal


class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('analizator_GUI.ui', self) # Load the .ui file
        self.show() # Show the GUI
        self.set_defaults()
        self.add_functions()

    def set_defaults(self):
        self.visibilityWidget.show_graph()
        # self.interferenceWidget.canvas.axes.set_ylabel('Сигнал на фотоприемнике, В')
        # self.interferenceWidget.canvas.axes.set_xlabel('Длина плеча интерферометра, м')
        # self.interferenceWidget.canvas.figure.tight_layout()
        # self.visibilityWidget.canvas.axes.set_ylabel('Видность,отн. ед.')
        # self.visibilityWidget.canvas.axes.set_xlabel('Длина плеча интерферометра, м')
        # self.visibilityWidget.canvas.figure.tight_layout()
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

    def open_file(self):
        self.__filenames, _ = QFileDialog.getOpenFileNames()
        self.label_filename.setText('/'.join(self.__filenames[0].split('/')[:-1])) if self.__filenames else self.label_filename.setText('Директория')
        float_parameters = self.str2float(self.total_time.text(), self.speed.text(), self.lambda_source.text(),
                                          self.source_bandwith.text(), self.delta_n.text())
        if isinstance(float_parameters, list) & (self.__filenames != []):
            if len(float_parameters) == 5:
                self.signal = [Data.Signal.Signal(np.fromfile(i), *float_parameters, name=i.split('/')[-1]) for i in self.__filenames]
                # self.draw_graph(self.interferenceWidget, 'linear', *[i.get_interference() for i in self.signal])
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

    def draw_graph(self, widget, scale='linear', *args):
        widget.fig = make_subplots(specs=[[{"secondary_y": True}]])
        for x, y, name in args:
            widget.fig.add_trace(go.Scatter(x=x, y=y,
                                            mode='lines',
                                            name=name,
                                            line=dict(width=0.5)
                                            ))
        widget.fig.update_yaxes(type=scale)
        widget.fig.update_xaxes(title_text="Длина плеча интерферометра, м")
        widget.fig.update_yaxes(title_text="h-parameter", secondary_y=False)
        widget.fig.update_yaxes(title_text="PER", secondary_y=True)
        widget.fig.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    visible=True
                )
            )
        )

        widget.show_graph()


    def calculate(self):
        self.__visibility = [i.get_visibility() for i in self.signal]
        self.draw_graph(self.visibilityWidget, 'log', *self.__visibility)

    @staticmethod
    def show_error():
        from PyQt5.QtWidgets import QMessageBox
        error = QMessageBox()
        error.setWindowTitle('Ошибка')
        error.setText('Неверно введены параметры')
        error.setIcon(QMessageBox.Warning)
        error.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)

        error.exec_()


def main():
    app = QApplication(sys.argv)
    window = Ui()
    app.exec_()
    if os.path.isfile('temp.html'):
        os.remove('temp.html')

if __name__ == '__main__':
    main()