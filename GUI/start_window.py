from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import sys
import os
import dash
from dash import Dash, dcc, html, Input, Output
import threading
import Data.Signal


class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('analizator_GUI.ui', self)  # Load the .ui file
        self.show()  # Show the GUI
        self.set_defaults()
        self.add_functions()
        self.signal = []

    def set_defaults(self):
        self.visibilityWidget.show_graph()
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
        self.label_filename.setText(
            '/'.join(self.__filenames[0].split('/')[:-1])) if self.__filenames else self.label_filename.setText(
            'Директория')
        float_parameters = self.str2float(self.total_time.text(), self.speed.text(), self.lambda_source.text(),
                                          self.source_bandwith.text(), self.delta_n.text())
        if isinstance(float_parameters, list) & (self.__filenames != []):
            if len(float_parameters) == 5:
                self.signal = [Data.Signal.Signal(np.fromfile(i), *float_parameters, name=i.split('/')[-1]) for i in
                               self.__filenames]
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
        error.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    def draw_graph(self, widget, scale='linear', *args):
        widget.fig = make_subplots(specs=[[{"secondary_y": True}]])
        for x, y, name in args:
            widget.fig.add_trace(go.Scatter(x=x, y=y,
                                            mode='lines',
                                            name=name,
                                            line=dict(width=0.5)
                                            ))

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
        error.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        error.exec_()


def run_dash(window):
    app = Dash()
    style_input = {'width': '100%'}
    style_div_input = {'marginBottom': '1.5em'}

    app.layout = html.Div([
        dcc.Graph(
            id="chart",
            config={"displaylogo": False},
            figure=window.visibilityWidget.fig,
            style={'width': '89%', 'height': '90vh', 'display': 'inline-block'}
        ),

        html.Div([
            html.Div(
                [
                    html.Div(
                        children='Время ввода [с]',
                        style=style_input
                    ),
                    dcc.Input(
                        id='total_time',
                        placeholder='Enter a value...',
                        type='number',
                        value='1',
                        style=style_input
                    )
                ],
                style=style_div_input
            ),

            html.Div(
                [
                    html.Div(
                        children='Скорость [мм/c]',
                        style=style_input
                    ),
                    dcc.Input(
                        id='speed',
                        placeholder='Enter a value...',
                        type='number',
                        value='30',
                        style=style_input
                    )
                ],
                style=style_div_input
            ),

            html.Div(
                [
                    html.Div(
                        children='Центральная длина волны источника [нм]',
                        style=style_input
                    ),
                    dcc.Input(
                        id='lambda_source',
                        placeholder='Enter a value...',
                        type='number',
                        value='1560',
                        style=style_input
                    )
                ],
                style=style_div_input
            ),

            html.Div(
                [
                    html.Div(
                        children='Ширина полосы источника в нанометрах [нм]',
                        style=style_input
                    ),
                    dcc.Input(
                        id='source_bandwith',
                        placeholder='Enter a value...',
                        type='number',
                        value='45',
                        style=style_input
                    )
                ],
                style=style_div_input
            ),

            html.Div(
                [
                    html.Div(
                        children='Разница эффективных показателей преломления волокна',
                        style=style_input
                    ),
                    dcc.Input(
                        id='delta_n',
                        placeholder='Enter a value...',
                        type='number',
                        value='6.086e-04',
                        style=style_input
                    )
                ],
                style=style_div_input
            ),

            html.Button(
                'Вычислить',
                id='button-calculate',
                style={'width': '100%', 'horizontal-align': 'middle', 'marginBottom': '1.5em'}
            ),
        ],
            style={'width': '9%', 'display': 'inline-block', 'vertical-align': 'top'})
    ])

    @app.callback(
        Output('chart', 'figure'),
        Input('button-calculate', 'n_clicks')
    )
    def calculate(n_clicks):
        figure = go.Figure(make_subplots(specs=[[{"secondary_y": True}]]))
        visibility = [i.get_visibility() for i in window.signal]
        for x, y, name in visibility:
            figure.add_trace(
                go.Scatter(
                    x=x, y=y,
                    mode='lines',
                    name=name,
                    line=dict(width=1)
                )
            )
        figure.update_yaxes(type='log')
        figure.update_xaxes(title_text="Длина плеча интерферометра, м")
        figure.update_yaxes(title_text="h-parameter", secondary_y=False)
        figure.update_yaxes(title_text="PER", secondary_y=True)
        figure.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    visible=True
                )
            )
        )
        return figure

    app.run_server(debug=True, use_reloader=False)


def main():
    app = QApplication(sys.argv)
    window = Ui()
    threading.Thread(target=run_dash, args=(window,), daemon=True).start()
    app.exec_()


if __name__ == '__main__':
    main()
