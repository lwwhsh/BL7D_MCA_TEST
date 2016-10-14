import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

####################################################################


class MyWindow(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)

        self.label = QLabel(" ")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.connect(self, SIGNAL("didSomethings"),
                     self.update_label)
        self.do_something()

    def do_something(self):
        self.emit(SIGNAL("didSomething"), "important", "information")

    def update_label(self, value1, value2):
        self.label.setText(value1 + " " + value2)

####################################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_(), )