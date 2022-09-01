from PyQt5 import QtWidgets, QtCore
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
app = QtWidgets.QApplication([''])
from PyQt5 import QtWebEngineWidgets
import plotly.graph_objects as go
import chart_studio.plotly.plotly as py
import plotly.io as pio
from qtplotly import PlotlyApplication
plotly_app = PlotlyApplication()


class PlotlyWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.browser = QtWebEngineWidgets.QWebEngineView(self)

        vertical_layout = QtWidgets.QVBoxLayout()
        vertical_layout.addWidget(self.browser)

        self.fig = go.Figure()

        self.setLayout(vertical_layout)


    def show_graph(self):
        # df = px.data.tips()
        # fig = px.box(df, x="day", y="total_bill", color="smoker")
        self.fig.update_traces()
        # url = py.iplot(self.fig, filename='123')
        self.browser.load(plotly_app.create_url(name))
        self.browser.setHtml(self.fig.to_html(include_plotlyjs='cdn'))

