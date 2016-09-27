#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os

## namespace organization changed in PyQt5 but the class name was kept.
## importing this way makes it easier to change to PyQt5 later
from PyQt4.QtGui import (QMainWindow, QApplication, QDockWidget, QWidget,
                         QGridLayout, QSlider, QCheckBox, QLabel, QLineEdit,
                         QIntValidator)
from PyQt4.QtCore import Qt
from PyQt4 import QtCore

import numpy
import matplotlib.pyplot

#test1
from matplotlib import pyplot as plt

import matplotlib.backends.backend_qt4agg

import readline
import epics
import time


progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class Point:
    def __init__(self, ax, pos, callback=None):
        self.callback = callback
        self.line = ax.axvline(pos, ls="--", c="k")
        self.pos = pos
        self.active = False

        self.line.connect('button_press_event', self.on_press)
        self.line.connect('button_release_event', self.on_release)
        self.line.connect('motion_notify_event', self.on_motion)

    def on_press(self, e):
        if self.line.contains(e)[0]:
            self.active = True
            self.on_motion(e)

    def on_motion(self, e):
        if not self.active:
            return
        self.line.set_xdata(e.xdata)
        if self.callback:
            self.pos = e.xdata
            self.callback()
        else:
            self.line.figure.canvas.draw()

    def on_release(self, e):
        self.on_motion(e)
        self.active = False


class MainWindow(QMainWindow):

    # TODO: How can change max bins(energy) value.
    # define X axis for mca bins
    maxBins = 2048
    x = numpy.arange(0, maxBins, 1)

    # define and initialise signal for mca Done callback signal
    # commSignal = QtCore.pyqtSignal(object)
    commSignal = QtCore.Signal()

    def __init__(self):
        QMainWindow.__init__(self)

        self.commSignal.connect(self.plot)

        # self.figure  = matplotlib.pyplot.figure()
        # test1
        self.figure = plt.figure()

        self.drawing = self.figure.add_subplot(111)

        #test1
        #self.drawing.axvline(599, ls="--", c="r", lw=2)

        self.canvas  = matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg(self.figure)

        self.setCentralWidget(self.canvas)

        dock = QDockWidget("Values")
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        # -----------------------------------------------------------------
        sliders = QWidget()
        sliders_grid = QGridLayout(sliders)

        chkRepeaterRun = QCheckBox("&Repeater...")
        chkRepeaterRun.setFocusPolicy(Qt.NoFocus)
        sliders_grid.addWidget(chkRepeaterRun,0,0)

        self.lowROI  = QLineEdit()
        #self.lowROI.setFocusPolicy(Qt.NoFocus)
        self.lowROI.setValidator(QIntValidator(0, self.maxBins - 1))
        self.highROI = QLineEdit()
        #self.highROI.setFocusPolicy(Qt.NoFocus)
        self.highROI.setValidator(QIntValidator(0, self.maxBins -1))
        sliders_grid.addWidget(self.lowROI,  1, 0)
        sliders_grid.addWidget(self.highROI, 2, 0)

        dock.setWidget(sliders)

        #self.a = Point(self.figure, self.maxBins/4, self.callback)
        #self.b = Point(self.figure, self.maxBins/2, self.callback)
        #-----------------------------------------------------------------

        self.dxpAcqPV  = epics.PV('BL7D:dxpXMAP:Acquiring')

        self.dxpMcaPVs = []
        self.noOfElement = 7

        for i in range(1, self.noOfElement+1, 1) :
            self.dxpMcaPVs.append(epics.PV('BL7D:dxpXMAP:mca' + str(i)))

        self.plot()
        self.addCallbackAcq()

    def onChanged(self, pvname=None, value=None, char_value=None, **kw):
        # print('onChanged: '), char_value, time.ctime()
        # value 1=Acquiring, 0=Done
        if value is 1 :
            return

        # self.commSignal.emit(self.plot) # emit the signal
        self.commSignal.emit()  # emit the signal

    def addCallbackAcq(self):
        # IMPORTANT: add_callback definition position. it define after callback function
        self.dxpAcqPV.add_callback(self.onChanged)

    def plot(self):
        self.drawing.hold(False)

        mcas = []
        avgMca = 0.0

        for i in self.dxpMcaPVs :
           mcas.append(i.get())
        for i in range(0, self.noOfElement, 1) :
            avgMca = avgMca + sum(mcas[i][560:630])

        print('Average: %d ') %(avgMca / self.noOfElement), time.ctime()

        # TODO : please implement zoom in / zoom out.
        self.drawing.plot(self.x, mcas[0], self.x, mcas[1],
                          self.x, mcas[2], self.x, mcas[3],
                          self.x, mcas[4], self.x, mcas[5],
                          self.x, mcas[6], linewidth=1.0)

        # self.drawing.set_ylim(0, 2500)
        # self.drawing.set_xlim(550, 680)
        self.drawing.relim()

        # test1
        self.drawing.axvline(599, ls="--", c="r", lw=2)

        self.drawing.grid()
        self.canvas.draw()

    def callback(self):
        ''' manual set line position like this
        self.a.line.set_xdata(0.4)
        self.b.line.set_xdata(0.5)
        '''
        #self.ax.figure.canvas.draw()
        self.canvas.draw()
        #self.ax2.figure.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
