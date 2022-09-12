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
        # self.fig.update_traces()
        # self.fig.write_html('temp.html',
        #                     full_html=False,
        #                     include_plotlyjs='cdn')
        # dir_path = os.path.dirname(os.path.realpath(__file__))
        # url = QtCore.QUrl.fromLocalFile(dir_path + '/' + 'temp.html')
        url = QtCore.QUrl(u'http://127.0.0.1:8050/')
        self.browser.load(url)
        # self.browser.setHtml('temp.html')

