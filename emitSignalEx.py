# -*- coding:utf-8 -*-

from PyQt4 import QtCore, QtGui


class WidgetEmitter(QtGui.QWidget):
    procSignal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, name='A'):
        super(WidgetEmitter, self).__init__(parent)

        self.widgetName = name
        self.lineEdit = QtGui.QLineEdit(self)
        self.lineEdit.setText("Hello! I am " + self.widgetName)
        self.button = QtGui.QPushButton("Send Message from "+self.widgetName, self)
        self.layout = QtGui.QHBoxLayout(self)
        self.layout.addWidget(self.lineEdit)
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self.on_button_clicked)

    def on_button_clicked(self):
        self.procSignal.emit(self.lineEdit.text())

    @QtCore.pyqtSlot(str)
    def on_procStart(self, message):
        print('This is on_procStart')
        self.lineEdit.setText("From "+self.widgetName+" :" + message)
        self.raise_()


class widgetB(WidgetEmitter):
    print('This is widget B')

    def __init__(self, *args, **kwargs):
        WidgetEmitter.__init__(self, name='B')


class widgetA(WidgetEmitter):
    print('This is widget A')

    def __init__(self, *args, **kwargs):
        WidgetEmitter.__init__(self, name='A')


class mainwindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(mainwindow, self).__init__(parent)

        self.button = QtGui.QPushButton("Click Me", self)
        self.button.clicked.connect(self.on_button_clicked)

        self.setCentralWidget(self.button)

        self.widgetA = widgetA()
        self.widgetB = widgetB()

        self.widgetA.procSignal.connect(self.widgetB.on_procStart)
        self.widgetB.procSignal.connect(self.widgetA.on_procStart)

    @QtCore.pyqtSlot()
    def on_button_clicked(self):
        self.widgetA.show()
        self.widgetB.show()

        self.widgetA.raise_()


if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    main = mainwindow()
    main.show()
    sys.exit(app.exec_())
