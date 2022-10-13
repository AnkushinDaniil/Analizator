import os
import sys
from collections import OrderedDict
from tkinter import Tk

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

pio.kaleido.scope.default_format = "png"
import numpy as np
from scipy.io import savemat
from dash import Dash, dcc, html, Input, Output, State, dash_table, ctx
import dash_bootstrap_components as dbc
from tkinter.filedialog import askopenfilenames, asksaveasfilename
import io
import PIL.Image as Image

from Data import Signal


def resource_path(relative_path):
    # get absolute path to resource
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class DashApp:
    app = Dash(__name__, assets_folder=resource_path("assets"), external_stylesheets=[dbc.themes.BOOTSTRAP])

    def __init__(self):
        self.figure = None
        self.dir = ''
        self._data_range = None
        self._data_input = None
        self.signal = []
        self.set_data_input(30, 1, 1560, 45, 6.086e-04, 500_000, 250_000)
        self.set_data_range(0, 0.025)
        self._filenames = np.array([])
        self.set_figure()
        self.app.layout = dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dcc.Graph(
                                    id="visibility",
                                    config={"displaylogo": False},
                                    figure=self.figure['visibility'],
                                ),
                                dcc.Graph(
                                    id="h-parameter",
                                    config={"displaylogo": False},
                                    figure=self.figure['h-parameter'],
                                )
                            ],
                            width=10,
                            align="center"
                        ),
                        dbc.Col(
                            [
                                dbc.Row(
                                    dash_table.DataTable(
                                        id='table_input',
                                        data=self.get_data_input(),
                                        columns=[
                                            {'name': 'Величина', 'id': 'Величина', 'editable': False},
                                            {'name': 'Значение', 'id': 'Значение', 'type': 'numeric'},
                                        ],
                                        style_data={
                                            'whiteSpace': 'normal',
                                            'height': 'auto',
                                        },
                                        editable=True
                                    ),
                                    align="center",
                                    className="mb-4"
                                ),

                                dbc.Row(
                                    dbc.ButtonGroup(
                                        [
                                            dbc.Button(
                                                'Выбрать файл и построить',
                                                id='button-build',
                                                className="me-1"
                                            ),
                                        ],
                                        vertical=True,
                                    ),
                                    align="center",
                                    className="mb-4"
                                ),

                                html.Div(
                                    dash_table.DataTable(
                                        id='table_range',
                                        data=self.get_data_range(),
                                        columns=[
                                            {'name': 'Левая граница, м', 'id': 'Левая граница, м',
                                             'type': 'numeric'},
                                            {'name': 'Правая граница, м', 'id': 'Правая граница, м',
                                             'type': 'numeric'},
                                        ],
                                        editable=True
                                    ),
                                    className="mb-4"
                                ),

                                html.Div(
                                    id='dir',
                                    children='Директория',
                                    className="mb-4"
                                ),

                                dbc.Row(
                                    dbc.ButtonGroup(
                                        [
                                            dbc.RadioItems(
                                                id="export_file",
                                                className="btn-group",
                                                inputClassName="btn-check",
                                                labelClassName="btn btn-primary btn-sm",
                                                labelCheckedClassName="active",
                                                options=[
                                                    {"label": "mat", "value": 1},
                                                    {"label": "html", "value": 2},
                                                    {"label": "csv", "value": 3},
                                                    {"label": "png", "value": 4},
                                                ],
                                                value=1,
                                            ),
                                            dbc.RadioItems(
                                                id="export_chart",
                                                className="btn-group",
                                                inputClassName="btn-check",
                                                labelClassName="btn btn-outline-primary",
                                                labelCheckedClassName="active",
                                                options=[
                                                    {"label": "h-parameter", "value": 1},
                                                    {"label": "Видность", "value": 2},
                                                ],
                                                value=1,
                                            ),
                                            dbc.Button(
                                                'Экспортировать',
                                                id='button-export',
                                                className="me-1"
                                            ),
                                        ],
                                        vertical=True,
                                    ),
                                    align="center",
                                    className="mb-4"
                                )
                            ],
                            width=2,
                            align="center",
                        )
                    ],
                    justify="around",
                ),
                dbc.Row(
                    [
                        html.Div(
                            id='selected-data',
                            children=''
                        ),
                        html.Div(
                            id='hidden',
                            style={'display': 'none'}
                        )
                    ]
                )
            ],
            fluid=True
        )

        if self.app is not None and hasattr(self, "callbacks"):
            self.callbacks(self.app)

    def callbacks(self, app):
        @app.callback(
            [
                Output('visibility', 'figure'),
                Output('h-parameter', 'figure'),
            ],
            [
                Input('button-build', 'n_clicks'),
                # Input('visibility', 'clickData'),
                State('table_input', 'data'),
                State('table_range', 'data')
            ],
            prevent_initial_call=True
        )
        def calculate(n_clicks, data_input, data_range):
            triggered_id = ctx.triggered_id
            if triggered_id == 'button-build':
                def select_file():
                    root = Tk()
                    root.withdraw()
                    root.focus_force()
                    res = askopenfilenames(parent=root)
                    root.destroy()
                    return res

                self.set_filenames(select_file())
                float_parameters = self.str2float(*[i['Значение'] for i in data_input])
                filenames = self.get_filenames()
                if isinstance(float_parameters, list):
                    if len(float_parameters) == 7:
                        self.signal = [Signal.Signal(np.fromfile(i), *float_parameters, name=i.split('/')[-1]) for i in
                                       filenames]
                    else:
                        self.show_error()

                visibility = [i.get_visibility() for i in self.signal]
                h_param = [i.get_h_param() for i in self.signal]
                self.set_figure()
                for key, value in zip(['visibility', 'h-parameter'], [visibility, h_param]):
                    for x, y, name in value:
                        self.figure[key].add_trace(
                            go.Scatter(
                                x=x, y=y,
                                mode='lines',
                                name=name,
                                line=dict(width=1)
                            )
                        )
                    self.figure[key].update_layout(showlegend=True)

            return self.figure['visibility'], self.figure['h-parameter']

        @app.callback(
            Output('table_range', 'data'),
            Input('visibility', 'relayoutData'),
        )
        def display_relayout_data(relayoutData):
            try:
                self.set_data_range(relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]'])
            except:
                pass
            return self.get_data_range()

        @app.callback(
            Output('hidden', 'children'),
            [
                Input('button-export', 'n_clicks'),
                State("export_file", "value"),
                State("export_chart", "value"),
            ],
            prevent_initial_call=True
        )
        def export(n_clicks, value_file, value_chart):
            def save_file(file_name, extension):
                root = Tk()
                root.withdraw()
                root.focus_force()

                data = [(extension, f'*.{extension}')]

                res = asksaveasfilename(filetypes=data, defaultextension=data,
                                        initialfile=file_name)
                root.destroy()
                return res

            if value_chart == 1:
                chart = [i.get_h_param() for i in self.signal]
                key = 'h-parameter'
            else:
                chart = [i.get_visibility() for i in self.signal]
                key = 'visibility'

            filename = '_'.join([name.split('.')[0] for x, y, name in chart])

            if value_file == 1:
                mdic = {'data_' + name.split('.')[0]: {'x': x, 'y': y} for x, y, name in chart}
                file_out = save_file(filename, 'mat')
                if file_out:
                    savemat(f"{file_out}", mdic)
            elif value_file == 2:
                file_out = save_file(filename, 'html')
                if file_out:
                    self.figure[key].write_html(file_out + '.html')
            elif value_file == 3:
                for x, y, name in chart:
                    df = pd.DataFrame({'x': x, 'y': y})
                    file_out = save_file(name, 'csv')
                    if file_out:
                        df.to_csv(file_out + '.csv')
            elif value_file == 4:
                file_out = save_file(filename, 'png')
                if file_out:
                    img_bytes = self.figure[key].to_image(format='png')
                    print(img_bytes)
                    image = Image.open(io.BytesIO(img_bytes))
                    image.save(file_out + '.png')
            return None

    def set_figure(self):
        self.figure = {
            'visibility': go.Figure(),
            'h-parameter': go.Figure()
        }

        self.figure['visibility'].update_yaxes(type='log')
        self.figure['visibility'].update_yaxes(title_text="Видность")
        self.figure['visibility'].update_xaxes(title_text="Длина плеча интерферометра, м")

        self.figure['h-parameter'].update_yaxes(title_text="h-parameter, дБ")
        self.figure['h-parameter'].update_xaxes(title_text="Длина волокна, м")

        for i in self.figure.keys():
            self.figure[i].update_layout(
            )
            self.figure[i].update_layout(uirevision="Don't change")

    def set_data_input(self, *args):
        data_default_input = OrderedDict(
            [
                ("Величина",
                 ["Время ввода, c", "Скорость, мм/c", "Центральная длина волны источника, нм",
                  "Ширина полосы источника, нм",
                  "Разница эффективных показателей преломления волокна",
                  "Частота АЦП, Гц",
                  "Частота фазовой модуляции"]),
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
            self.dir = '/'.join(self._filenames[0].split('/')[:-1]) + '/'
        else:
            self.dir = ''
        return self.dir

    def get_filenames(self):
        return self._filenames


if __name__ == '__main__':
    dash_app = DashApp()
    dash_app.app.run_server(debug=False, use_reloader=False)
