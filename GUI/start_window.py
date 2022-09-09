from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import sys
import os
from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_uploader as du
import dash_bootstrap_components as dbc
import threading
import Data.Signal
import pandas as pd
from collections import OrderedDict
import base64


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
    data_default_input = OrderedDict(
        [
            ("Величина",
             ["Время ввода", "Скорость", "Центральная длина волны источника", "Ширина полосы источника в нанометрах",
              "Разница эффективных показателей преломления волокна"]),
            ("Единица измерения", ["с", "мм/c", "нм", "нм", ""]),
            ("Значение", [30, 1, 1560, 45, 6.086e-04])
        ]
    )

    df_default_input = pd.DataFrame(data_default_input)

    data_default_range = OrderedDict(
        [
            ("Левая граница, м", [0]),
            ("Правая граница, м", [0.025])
        ]
    )

    df_default_range = pd.DataFrame(data_default_range)

    app: Dash = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.layout = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                dcc.Upload(
                                    id='upload-data',
                                    children=html.Div(
                                        [
                                            'Перетащите или ',
                                            html.A('выберете файл')
                                        ]
                                    ),
                                    style={
                                        'height': '60px',
                                        'lineHeight': '60px',
                                        'borderWidth': '1px',
                                        'borderStyle': 'dashed',
                                        'borderRadius': '5px',
                                        'textAlign': 'center',
                                        'margin': '10px',
                                    },
                                    multiple=True
                                ),
                            ),

                            html.Div(
                                dash_table.DataTable(
                                    id='table_range',
                                    data=df_default_range.to_dict('records'),
                                    columns=[
                                        {'name': 'Левая граница, м', 'id': 'Левая граница, м', 'type': 'numeric'},
                                        {'name': 'Правая граница, м', 'id': 'Правая граница, м', 'type': 'numeric'},
                                    ],
                                    editable=True
                                ),
                            ),

                            html.Div(
                                id='filenames',
                                children='Имя файла'
                            )
                        ],
                        md=4
                    ),

                    dbc.Col(
                        html.Div(
                            dash_table.DataTable(
                                id='table_input',
                                data=df_default_input.to_dict('records'),
                                columns=[
                                    {'name': 'Величина', 'id': 'Величина', 'editable': False},
                                    {'name': 'Единица измерения', 'id': 'Единица измерения', 'editable': False},
                                    {'name': 'Значение', 'id': 'Значение', 'type': 'numeric'},
                                ],
                                editable=True
                            ),
                        ),
                        md=4
                    ),
                ],
                align="center",
                justify="around",
            ),

            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(
                            id="chart",
                            config={"displaylogo": False},
                            figure=window.visibilityWidget.fig,
                            # style={'width': '89%', 'height': '70vh', 'display': 'inline-block'}
                        )
                    ),
                    dbc.Col(
                        html.Button(
                            'Вычислить',
                            id='button-calculate',
                            style={'width': '100%', 'marginBottom': '1.5em'}
                        ),
                        width=1
                    )
                ],
                justify="around",
            )
        ],
        fluid=True
    )

    @app.callback(
        Output('chart', 'figure'),
        Input('button-calculate', 'n_clicks'),
        State('table_input', 'data'),
        State('table_range', 'data')
    )
    def calculate(n_clicks, data_input, data_range):
        # [print(i['Значение']) for i in data_input]
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

    def parse_contents(contents, filename):
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        print(decoded)
        return decoded

    @app.callback(
        Output('filenames', 'children'),
        Input('upload-data', 'filename'),
        State('upload-data', 'contents')
    )
    def open_file(list_of_contents, list_of_names):
        if list_of_contents is not None:
            print(1)
            children = [
                parse_contents(c, n) for c, n in
                zip(list_of_contents, list_of_names)]
            return children

    app.run_server(debug=True, use_reloader=False)


def main():
    app = QApplication(sys.argv)
    window = Ui()
    threading.Thread(target=run_dash, args=(window,), daemon=True).start()
    app.exec_()


if __name__ == '__main__':
    main()
