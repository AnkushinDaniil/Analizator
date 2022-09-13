import json
import dash_bootstrap_components as dbc
from PyQt5.QtWidgets import QFileDialog
from dash import Dash, dcc, html, Input, Output, State, dash_table, ctx
from collections import OrderedDict
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

from Data import Signal


class DashApp:
    app: Dash = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

    def __init__(self):
        self._data_range = None
        self._data_input = None
        self.signal = []
        self.set_data_input(30, 1, 1560, 45, 6.086e-04)
        self.set_data_range(0, 0.025)
        self._filenames = np.array([])
        self.set_figure()
        self.traces = set()
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
                                figure=self.figure,
                                # style={'width': '89%', 'height': '70vh', 'display': 'inline-block'}
                            )
                        ),
                        dbc.Col(
                            html.Button(
                                'Построить',
                                id='button-build',
                                style={'width': '100%', 'marginBottom': '1.5em'}
                            ),
                            width=1
                        )
                    ],
                    justify="around",
                ),
                dbc.Row(
                    html.Div(
                        id='selected-data',
                        children=''
                    )
                )
            ],
            fluid=True
        )

        if self.app is not None and hasattr(self, "callbacks"):
            self.callbacks(self.app)

    def callbacks(self, app):
        @app.callback(
            Output('chart', 'figure'),
            Input('button-build', 'n_clicks'),
            # Input('chart', 'clickData'),
            State('table_input', 'data'),
            State('table_range', 'data'),
            prevent_initial_call=True
        )
        def calculate(n_clicks, clickData, data_input, data_range=None):
            triggered_id = ctx.triggered_id
            if triggered_id == 'button-build':   
                float_parameters = self.str2float(*[i['Значение'] for i in data_input])
                filenames = self.get_filenames()
                if isinstance(float_parameters, list):
                    if len(float_parameters) == 5:
                        self.signal = [Signal.Signal(np.fromfile(i), *float_parameters, name=i.split('/')[-1]) for i in
                                       filenames]
                    else:
                        self.show_error()

                visibility = [i.get_visibility() for i in self.signal]
                for x, y, name in visibility:
                    if not (name in self.traces):
                        self.traces.add(name)
                        self.figure.add_trace(
                            go.Scatter(
                                x=x, y=y,
                                mode='lines',
                                name=name,
                                line=dict(width=1)
                            )
                        )
                        # self.figure.add_trace(
                        #     go.Scatter(
                        #         x=[], y=[],
                        #         mode='markers',
                        #         name='Выбранное в ' + name,
                        #         marker=dict(size=5),
                        #         text=[]
                        #     )
                        # )
            # elif triggered_id == 'chart':
            #     i = clickData['points'][0]
            #     j = i['curveNumber'] + 1
            #     x = i['x']
            #     y = i['y']
            #     text = f'{x}, {y}'
            #     x_list = list(self.figure.data[j]['x'])
            #     y_list = list(self.figure.data[j]['y'])
            #     text_list = list(self.figure.data[j]['text'])
            #     if x in self.figure.data[j]['x']:
            #         x_list.remove(x)
            #         y_list.remove(y)
            #         text_list.remove(f'{x}, {y}')
            #     else:
            #         x_list.append(x)
            #         y_list.append(y)
            #         text_list.append(f'{x}, {y}')
            #     self.figure.data[j]['x'] = tuple(x_list)
            #     self.figure.data[j]['y'] = tuple(y_list)
            #     self.figure.data[j]['text'] = tuple(text_list)
            return self.figure

        @app.callback(
            Output('dir', 'children'),
            [Input('file-selector', 'n_clicks')],
            prevent_initial_call=True
        )
        def open_file(n_clicks=None):
            filenames, _ = QFileDialog.getOpenFileNames()
            self.set_filenames(filenames)

    def set_figure(self):
        self.figure = go.Figure(make_subplots(specs=[[{"secondary_y": True}]]))
        self.figure.update_yaxes(type='log')
        self.figure.update_xaxes(title_text="Длина плеча интерферометра, м")
        self.figure.update_yaxes(title_text="h-parameter", secondary_y=False)
        self.figure.update_yaxes(title_text="PER", secondary_y=True)
        self.figure.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    visible=True
                )
            )
        )
        self.figure.update_layout(uirevision="Don't change")
        # self.figure.update_layout(clickmode='event+select')
        self.figure.update_traces(textposition="top")

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
