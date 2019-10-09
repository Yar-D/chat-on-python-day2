#  Графический интерфейс PyQt 5
import sys
from PyQt5 import QtWidgets
from design import window


class ExampleApp(QtWidgets.QMainWindow, window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.send_message)

    def send_message(self):
        self.plainTextEdit.appendPlainText(self.lineEdit.text())
        self.lineEdit.clear()

def main():
    app = QtWidgets.QApplication(sys.argv)
    mwindow = ExampleApp()
    mwindow.show()
    app.exec_()


main()
