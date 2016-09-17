from __future__ import division
import sys
import platform

# Qt4 bindings for core Qt functionalities (non-GUI)
import PyQt4.QtCore as  QtCore

# Python Qt4 bindings for GUI objects
import PyQt4.QtGui as QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *
# import the Qt4Agg FigureCanvas object, that binds Figure to
# Qt4Agg backend. It also inherits from QWidget
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
# Matplotlib Figure object
from matplotlib.figure import Figure

class C_MplCanvas(FigureCanvas):
    def __init__(self):
        # setup Matplotlib Figure and Axis
        self.fig = Figure()
        #self.cursor = Cursor()
        self.fig.set_facecolor('black')
        self.fig.set_edgecolor('black')
        #self.ax = self.fig.add_subplot(111)
        #self.ax.patch.set_facecolor('black')
        # initialization of the canvas
        FigureCanvas.__init__(self, self.fig)
        #super(FigureCanvas, self).__init__(self.fig)


        # we define the widget as expandable
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        # notify the system of updated policy
        FigureCanvas.updateGeometry(self)

        self.xx=0
        self.yy=0
        self.justDoubleClicked=False

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        oneAction = menu.addAction("&One")
        twoAction = menu.addAction("&Two")
        self.connect(oneAction, SIGNAL("triggered()"), self.one)
        self.connect(twoAction, SIGNAL("triggered()"), self.two)
        '''
        if not self.message:
            menu.addSeparator()
            threeAction = menu.addAction("Thre&e")
            self.connect(threeAction, SIGNAL("triggered()"),
                         self.three)
        '''
        menu.exec_(event.globalPos())


    def one(self):
        self.message = QString("Menu option One")
        self.update()


    def two(self):
        self.message = QString("Menu option Two")
        self.update()


    def three(self):
        self.message = QString("Menu option Three")
        self.update()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.TextAntialiasing)
        #painter.drawText(self.rect(), Qt.AlignCenter, text)
        #

        #painter.setPen('red')

        pen=painter.pen()
        painter.setPen(QColor(255, 0, 0))

        painter.drawLine(self.xx-100,self.yy,self.xx+100,self.yy)
        painter.drawLine(self.xx,self.yy-100,self.xx,self.yy+100)
        self.update()

    def mouseReleaseEvent(self, event):
        if self.justDoubleClicked:
            self.justDoubleClicked = False
        else:
            self.setMouseTracking(not self.hasMouseTracking())
            self.update()


    def mouseMoveEvent(self, event):
        self.xx=event.pos().x()
        self.yy=event.pos().y()
        self.update()




class C_MPL(QWidget):

    def __init__(self, parent = None):
        # initialization of Qt MainWindow widget
        super(C_MPL, self).__init__(parent)
        #QtGui.QWidget.__init__(self, parent)

        # instantiate a widget, it will be the main one
        #self.main_widget = QtGui.QWidget(self)
        #vbl = QtGui.QVBoxLayout(self.main_widget)
        # set the canvas to the Matplotlib widget
        self.canvas = C_MplCanvas()

        # create a vertical box layout
        self.vbl = QtGui.QVBoxLayout()
        # add mpl widget to vertical box
        self.vbl.addWidget(self.canvas)
        # set the layout to th vertical box
        self.setLayout(self.vbl)




if __name__ == "__main__":
    import sys

    '''
    def valueChanged(a, b):
        print a, b
    '''
    app = QApplication(sys.argv)
    form = C_MPL()
    #form.connect(form, SIGNAL("valueChanged"), valueChanged)
    form.setWindowTitle("C_MPL")
    #form.move(0, 0)
    form.show()
    #form.resize(400, 400)
    app.exec_()