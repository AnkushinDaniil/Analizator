import sys
import threading

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow

from Data.Dash_app import DashApp


class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('analizator_GUI.ui', self)  # Load the .ui file
        self.signal = []
        self.filenames = []
        self.showMaximized()  # Show the GUI
        self.visibilityWidget.show_graph()

def run_dash():
    dash_app = DashApp()
    dash_app.app.run_server(debug=True, use_reloader=False)


def main():
    main_app = QApplication(sys.argv)
    window = Ui()
    threading.Thread(target=run_dash, args=(), daemon=True).start()
    main_app.exec_()


if __name__ == '__main__':
    main()
