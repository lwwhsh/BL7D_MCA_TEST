import sys
import platform

from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class MplCanvas(FigureCanvas):

    def __init__(self):

        # initialization of the canvas
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)

        self.ax = self.fig.add_axes([.15, .15, .75, .75])
        self.canvas = self.ax.figure.canvas

        # my added
        # self.ax = self.fig.add_axes([.15, .15, .75, .75])
        # cursor = C_Cursor(self.LvsT, useblit=True, color='red', linewidth=2 )

        x = np.arange(0, 20, 0.1)

        self.ax.plot(x, x**2, 'o')
        self.ax.grid()
        self.ax.set_xlim(-2, 2)
        self.ax.set_ylim(-2, 2)

        self.visible = True
        self.horizOn = True
        self.vertOn = True
        self.useblit = True

        # if self.useblit:
        #     lineprops['animated'] = True

        self.lineh = self.ax.axhline(self.ax.get_ybound()[0], visible=False)
        self.linev = self.ax.axvline(self.ax.get_xbound()[0], visible=False)

        self.background = None
        self.needclear = False

        self.count = 0

        # cid0 = self.mpl_connect('axes_enter_event', self.enter_axes)
        cid1 = self.mpl_connect('button_press_event', self.onpick)
        cid2 = self.mpl_connect('motion_notify_event', self.onmove)
        cid3 = self.mpl_connect('draw_event', self.clear)
        cid4 = self.mpl_connect('key_press_event',self.press)

        self.draw()

    def clear(self, event):
        # clear the cursor
        if self.useblit:
            self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.linev.set_visible(False)
        self.lineh.set_visible(False)

    def onmove(self, event):
        # on mouse motion draw the cursor if visible
        # print("move")
        if event.inaxes != self.ax:
            self.linev.set_visible(False)
            self.lineh.set_visible(False)

            if self.needclear:
                self.canvas.draw()
                self.needclear = False
            return

        self.needclear = True
        if not self.visible:
            return

        self.linev.set_xdata((event.xdata, event.xdata))
        self.lineh.set_ydata((event.ydata, event.ydata))
        self.linev.set_visible(self.visible and self.vertOn)
        self.lineh.set_visible(self.visible and self.horizOn)

        self._update()

    def _update(self):

        if self.useblit:
            if self.background is not None:
                self.canvas.restore_region(self.background)

            self.ax.draw_artist(self.linev)
            self.ax.draw_artist(self.lineh)
            self.canvas.blit(self.ax.bbox)
        else:
            self.canvas.draw_idle()

        return False

    def enter_axes(self, event):

        print "Enter"

    def onpick(self, event):
        print "click"
        print 'you pressed', event.canvas

        a = np.arange(10)
        print a
        print self.count

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(a)
        fig.show()

    def press(self, event):
        print ('press', event.key)
        self.fig.canvas.draw()


class MplWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.vbl = QtGui.QVBoxLayout()
        self.canvas = MplCanvas()
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    form = MplWidget()
    form.show()
    # form.resize(400, 400)
    app.exec_()
