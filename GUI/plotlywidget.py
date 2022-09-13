from PyQt5 import QtWidgets, QtCore
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
app = QtWidgets.QApplication([''])
from PyQt5 import QtWebEngineWidgets
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class PlotlyWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.browser = QtWebEngineWidgets.QWebEngineView(self)

        vertical_layout = QtWidgets.QVBoxLayout()
        vertical_layout.addWidget(self.browser)

        self.setLayout(vertical_layout)


    def show_graph(self):
        url = QtCore.QUrl(u'http://127.0.0.1:8050/')
        self.browser.load(url)

