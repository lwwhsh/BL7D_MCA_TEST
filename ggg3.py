# -*- coding: utf-8 -*-
import sys
from os import path
import readline
import time
import epics
import matplotlib.pyplot as plt
import numpy as np

from PyQt4.QtCore import Qt
from PyQt4 import QtCore, QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar


progname = path.basename(sys.argv[0])
progversion = "0.1"


class Point:
    def __init__(self, ax, pos, callback=None):
        self.callback = callback
        self.line = ax.axvline(pos, ls="--", c="k")
        self.pos = pos
        self.active = False

        plt.connect('button_press_event', self.on_press)
        plt.connect('button_release_event', self.on_release)
        plt.connect('motion_notify_event', self.on_motion)

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


class LineFitter:
    # commSignal = QtCore.Signal()
    def __init__(self):
        # self.commSignal.connect(self.plot)

        self.mcas = []
        self.dxpMcaPVs = []
        self.noOfElement = 7
        self.dxpAcqPV = epics.PV('BL7D:dxpXMAP:Acquiring')

        # Create dxp mca PVs
        for i in range(1, self.noOfElement + 1, 1):
            self.dxpMcaPVs.append(epics.PV('BL7D:dxpXMAP:mca' + str(i)))

        # Read current mcas
        for i in self.dxpMcaPVs:
            self.mcas.append(i.get())

        # Create x axis value
        self.x = np.arange(0, len(self.mcas[0]), 1)

        # Create plot graph GUI
        # plt.ion()
        self.fig, self.ax = plt.subplots()
        self.fig.set_tight_layout(False)
        self.fig.canvas.set_window_title(progname + ' Ver.' + progversion)
        self.fig.suptitle('BL7D MCA with ROI bar')
        # 1st plot mca data
        self.ax.plot(self.x, self.mcas[0], self.x, self.mcas[1],
                     self.x, self.mcas[2], self.x, self.mcas[3],
                     self.x, self.mcas[4], self.x, self.mcas[5],
                     self.x, self.mcas[6], linewidth=1.0)

        self.ax.grid()
        self.ax.autoscale()

        self.lowROI = Point(self.ax, max(self.x) * 0.3, self.callback)
        self.highROI = Point(self.ax, max(self.x) * 0.7, self.callback)

        # We need to draw *and* flush
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

        # ---------------------------------------------------------------------
        self.addCallbackAcq()

    def onChanged(self, pvname=None, value=None, char_value=None, **kw):
        # print('onChanged: '), char_value, time.ctime()
        # value 1=Acquiring, 0=Done
        if value is 1:
            return

        # self.commSignal.emit(self.plot) # emit the signal
        # self.commSignal.emit() # emit the signal
        self.plot()

    def addCallbackAcq(self):
        # IMPORTANT: add_callback definition position. it define after callback function
        self.dxpAcqPV.add_callback(self.onChanged)

    def plot(self):
        self.ax.hold(None)

        self.mcas = []
        avgMca = 0.0

        for i in self.dxpMcaPVs:
            self.mcas.append(i.get())

        for i in range(0, self.noOfElement, 1):
            avgMca = avgMca + sum(self.mcas[i][int(self.lowROI.pos):int(self.highROI.pos)])

        print('=== Average: --%d--') %(avgMca / self.noOfElement), time.ctime()

        if self.ax.lines:
            i = 0
            for line in self.ax.lines:
                # this plot has total 9(7mca + 2axvline) lines,
                # so need not include last 2(axvline) lines
                if i < 7:
                    line.set_xdata(self.x)
                    line.set_ydata(self.mcas[i])
                    i += 1
                else:
                    pass

        # y-axis set to autoscale
        self.ax.relim()
        self.ax.autoscale(enable=True, axis=u'y', tight=None)
        # self.ax.autoscale_view()
        # We need to draw *and* flush
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    # --------------------------------------------------------------------------

    def callback(self):
        # TODO: implement cursor freez of min/max use self.lowROI.get_xbound()
        # TODO: Display Low / High ROI value
        if self.lowROI.pos < 0 or None:
            self.lowROI.line.set_xdata(10)
            self.lowROI.pos = 10
        if self.highROI.pos < 100 or None:
            self.highROI.line.set_xdata(100)
            self.highROI.pos = 100

        self.ax.figure.canvas.draw()


l = LineFitter()

plt.show()