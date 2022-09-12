import dash_bootstrap_components as dbc
from PyQt5.QtWidgets import QFileDialog
from dash import Dash, dcc, html, Input, Output, State, dash_table
from collections import OrderedDict
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

import Data


class DashApp:
    app: Dash = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

    def __init__(self):
        self._data_range = None
        self._data_input = None
        self.signal = []
        self.set_data_input(30, 1, 1560, 45, 6.086e-04)
        self.set_data_range(0, 0.025)
        self._filenames = []
        self.app.layout = dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Button(
                                    'Выбрать файл',
                                    id='file-selector',
                                    style={'width': '100%', 'marginBottom': '1.5em'}
                                ),

                                html.Div(
                                    dash_table.DataTable(
                                        id='table_range',
                                        data=self.get_data_range(),
                                        columns=[
                                            {'name': 'Левая граница, м', 'id': 'Левая граница, м', 'type': 'numeric'},
                                            {'name': 'Правая граница, м', 'id': 'Правая граница, м', 'type': 'numeric'},
                                        ],
                                        editable=True
                                    ),
                                ),

                                html.Div(
                                    id='dir',
                                    children='Директория'
                                )
                            ],
                            md=4
                        ),

                        dbc.Col(
                            html.Div(
                                dash_table.DataTable(
                                    id='table_input',
                                    data=self.get_data_input(),
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
                                figure=go.Figure(make_subplots(specs=[[{"secondary_y": True}]])),
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

        if self.app is not None and hasattr(self, "callbacks"):
            self.callbacks(self.app)

    def callbacks(self, app):
        @app.callback(
            Output('chart', 'figure'),
            Input('button-calculate', 'n_clicks'),
            State('table_input', 'data'),
            State('table_range', 'data')
        )
        def calculate(n_clicks, data_input, data_range=None):
            float_parameters = self.str2float(*[i['Значение'] for i in data_input])
            filenames = self.get_filenames()
            if isinstance(float_parameters, list):
                if len(float_parameters) == 5:
                    self.signal = [Data.Signal.Signal(np.fromfile(i), *float_parameters, name=i.split('/')[-1]) for i in
                                   filenames]
                else:
                    self.show_error()

            figure = go.Figure(make_subplots(specs=[[{"secondary_y": True}]]))
            visibility = [i.get_visibility() for i in self.signal]
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

        @app.callback(
            Output('dir', 'children'),
            Input('file-selector', 'n_clicks')
        )
        def open_file(n_clicks=None):
            filenames, _ = QFileDialog.getOpenFileNames()
            self.set_filenames(filenames)

    def set_data_input(self, *args):
        data_default_input = OrderedDict(
            [
                ("Величина",
                 ["Время ввода", "Скорость", "Центральная длина волны источника",
                  "Ширина полосы источника в нанометрах",
                  "Разница эффективных показателей преломления волокна"]),
                ("Единица измерения", ["с", "мм/c", "нм", "нм", ""]),
                ("Значение", args)
            ]
        )
        df_input = pd.DataFrame(data_default_input)
        self._data_input = df_input.to_dict('records')

    def get_data_input(self):
        return self._data_input

    def set_data_range(self, *args):
        left, right = args
        data_range = OrderedDict(
            [
                ("Левая граница, м", [left]),
                ("Правая граница, м", [right])
            ]
        )

        df_range = pd.DataFrame(data_range)
        self._data_range = df_range.to_dict('records')

    def get_data_range(self):
        return self._data_range

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

    def set_filenames(self, filenames):
        self._filenames = filenames
        if self._filenames:
            res = '/'.join(self._filenames[0].split('/')[:-1])
        else:
            res = 'Директория'
        return res

    def get_filenames(self):
        return self._filenames


if __name__ == '__main__':
    dash_app = DashApp()
    dash_app.app.run_server(debug=True, use_reloader=False)
