# -*- coding : utf-8 -*­
from PyQt5 import QtWidgets
import sys
app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QWidget()
window.setWindowTitle("Пepвaя программа на PyQt")
window.resize(300, 70)
label = QtWidgets.QLabel("<center>Пpивeт, 11t1Иp ! </center>")
btnQuit = QtWidgets.QPushButton("&Зaкpыть окно")
vbox = QtWidgets.QVBoxLayout ()
vbox.addWidget(label)
vbox.addWidget(btnQuit)
window.setLayout(vbox)
btnQuit.clicked.connect(app.quit)
window.show()
sys.exit(app.exec_())