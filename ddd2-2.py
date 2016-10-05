#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os

# namespace organization changed in PyQt5 but the class name was kept.
# importing this way makes it easier to change to PyQt5 later
from PyQt4.QtGui import (QMainWindow, QApplication, QDockWidget, QWidget,
                         QGridLayout, QSlider, QCheckBox, QLabel, QLineEdit,
                         QIntValidator)
from PyQt4.QtCore import Qt
from PyQt4 import QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

import numpy as np
import matplotlib.pyplot as plt
import readline
import epics
import time


progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class Point:

    def __init__(self, canvas, ax, pos, callback=None):
        self.callback = callback
        self.line = ax.axvline(pos, ls="--", c="k")
        self.pos = pos
        self.active = False

        canvas.mpl_connect('button_press_event', self.on_press)
        canvas.mpl_connect('button_release_event', self.on_release)
        canvas.mpl_connect('motion_notify_event', self.on_motion)

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
    # x = np.arange(0, maxBins, 1)

    # define and initialise signal for mca Done callback signal
    # commSignal = QtCore.pyqtSignal(object)
    commSignal = QtCore.Signal()

    def __init__(self):
        QMainWindow.__init__(self)

        self.commSignal.connect(self.plot)

        self.figure, self.drawing = plt.subplots()
        self.figure.set_tight_layout(True)
        self.canvas = FigureCanvas(self.figure)

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
        # self.lowROI.setFocusPolicy(Qt.NoFocus)
        self.lowROI.setValidator(QIntValidator(0, self.maxBins - 1))
        self.highROI = QLineEdit()
        # self.highROI.setFocusPolicy(Qt.NoFocus)
        self.highROI.setValidator(QIntValidator(0, self.maxBins -1))
        sliders_grid.addWidget(self.lowROI,  1, 0)
        sliders_grid.addWidget(self.highROI, 2, 0)

        dock.setWidget(sliders)
        # -----------------------------------------------------------------

        self.dxpMcaPVs = []
        self.mcas = []
        self.noOfElement = 7
        self.dxpAcqPV = epics.PV('BL7D:dxpXMAP:Acquiring')

        for i in range(1, self.noOfElement+1, 1) :
            self.dxpMcaPVs.append(epics.PV('BL7D:dxpXMAP:mca' + str(i)))

        # Read current mcas
        for i in self.dxpMcaPVs:
            self.mcas.append(i.get())

        # Create x axis value
        self.x = np.arange(0, len(self.mcas[0]), 1)

        # 1st plot mca data
        self.drawing.plot(self.x, self.mcas[0], self.x, self.mcas[1],
                          self.x, self.mcas[2], self.x, self.mcas[3],
                          self.x, self.mcas[4], self.x, self.mcas[5],
                          self.x, self.mcas[6], linewidth=1.0)

        self.drawing.grid()
        self.drawing.autoscale()

        self.a = Point(self.canvas, self.drawing, self.maxBins / 4, self.callback)
        self.b = Point(self.canvas, self.drawing, self.maxBins / 2, self.callback)

        # self.plot()
        # We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

        self.addCallbackAcq()

    def onChanged(self, pvname=None, value=None, char_value=None, **kw):
        # print('onChanged: '), char_value, time.ctime()
        # value 1=Acquiring, 0=Done
        if value is 1 :
            return

        # self.commSignal.emit(self.plot) # emit the signal
        self.commSignal.emit()  # emit the signal

    def addCallbackAcq(self):
        # IMPORTANT: add_callback definition position.
        # it define after callback function
        self.dxpAcqPV.add_callback(self.onChanged)

    def plot(self):
        self.drawing.hold(None)

        self.mcas = []
        avgMca = 0.0

        # get new dxpDatas to mcas
        for i in self.dxpMcaPVs :
            self.mcas.append(i.get())
        for i in range(0, self.noOfElement, 1) :
            avgMca = avgMca + sum(self.mcas[i][560:630])

        print ('Average: %d ') %(avgMca / self.noOfElement), time.ctime()

        # TODO : please implement zoom in / zoom out.
        # redraw new mca data.
        if self.drawing.lines:
            i = 0
            for line in self.drawing.lines:
                # this plot has total 9(7mca + 2axvline) lines,
                # so need not include last 2(axvline) lines
                if i < 7:
                    line.set_xdata(self.x)
                    line.set_ydata(self.mcas[i])
                    i += 1
                else:
                    pass

        # y-axis set to autoscale
        self.drawing.relim()
        self.drawing.autoscale(enable=True, axis=u'y', tight=None)
        # self.ax.autoscale_view()

        # We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

        # self.canvas.draw()

    def callback(self):
        ''' manual set line position like this
        self.a.line.set_xdata(0.4)
        self.b.line.set_xdata(0.5)
        '''
        self.drawing.figure.canvas.draw()
        # self.canvas.draw()
        # self.ax2.figure.canvas.draw()
        # self.drawing.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
