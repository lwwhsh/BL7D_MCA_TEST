import sys
from PyQt4 import QtCore, QtGui, QtSvg
from PyQt4.Qt import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import StringIO

class Circle(QtGui.QWidget):
    def __init__(self):
        super(Circle, self).__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(500, 500)

    def paintEvent(self, event):
        p = QtGui.QPainter()
        p.begin(self)
        p.setPen(QtGui.QColor(255,0,0))
        p.drawEllipse(100, 100, 300, 300)
        p.end()

class MPLPlot(QtGui.QWidget):
    def __init__(self):
        super(MPLPlot, self).__init__()

        figure = Figure()
        axes = figure.gca()
        axes.set_title("Use the mouse wheel to zoom")
        axes.plot(np.random.rand(5))
        canvas = FigureCanvas(figure)
        canvas.setGeometry(0, 0, 500, 500)

        imgdata = StringIO.StringIO()
        figure.savefig(imgdata, format='svg')
        imgdata.seek(0)
        xmlreader = QtCore.QXmlStreamReader(imgdata.getvalue())
        self.renderer = QtSvg.QSvgRenderer(xmlreader)

    def paintEvent(self, event):
        p = QtGui.QPainter()
        p.begin(self)
        self.renderer.render(p)
        p.end()


class MyView(QtGui.QGraphicsView):
    def __init__(self):
        QtGui.QGraphicsView.__init__(self)

        scene = QtGui.QGraphicsScene(self)
        self.scene = scene

        plot = MPLPlot()
        scene.addWidget(plot)

        circle = Circle()
        self.circle = circle
        scene.addWidget(circle)

        self.setScene(scene)

    def wheelEvent(self, event):
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        zoom_in = 1.15
        zoom_out = 1.0 / zoom_in
        if event.delta() > 0:
            self.scale(zoom_in, zoom_in)
        else:
            self.scale(zoom_out, zoom_out)

app = QtGui.QApplication(sys.argv)
view = MyView()
view.show()
sys.exit(app.exec_())