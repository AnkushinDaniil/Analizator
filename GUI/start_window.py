import sys
import os
from multiprocessing import freeze_support, Process
from concurrent.futures import ThreadPoolExecutor
from PyQt5 import QtWidgets, QtCore

QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
app = QtWidgets.QApplication([''])
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow

from Data.Dash_app import DashApp


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

class Ui(QMainWindow):

    def __init__(self):
        super(Ui, self).__init__()  # Call the inherited classes __init__ method
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.visibilityWidget = PlotlyWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(10)
        sizePolicy.setVerticalStretch(10)
        sizePolicy.setHeightForWidth(self.visibilityWidget.sizePolicy().hasHeightForWidth())
        self.visibilityWidget.setSizePolicy(sizePolicy)
        self.visibilityWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.visibilityWidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.visibilityWidget.setObjectName("visibilityWidget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.visibilityWidget)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout.addWidget(self.visibilityWidget)
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.signal = []
        self.filenames = []
        self.showMaximized()  # Show the GUI
        self.visibilityWidget.show_graph()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", " Анализатор"))


def run_dash():
    dash_app = DashApp()
    dash_app.app.run_server(debug=False, use_reloader=False)


def main():
    freeze_support()
    main_app = QApplication(sys.argv)
    window = Ui()
    Process(target=run_dash, daemon=True).start()
    # threading.Thread(target=run_dash, args=(), daemon=True).start()
    main_app.exec_()


# def doer(func):
#     func()


if __name__ == '__main__':
    main()
