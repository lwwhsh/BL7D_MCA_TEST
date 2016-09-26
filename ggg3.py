# -*- coding: utf-8 -*-
import sys
from os import path
import readline
import time
import epics
import matplotlib.pyplot as plt
import numpy as np

from PyQt4.QtCore import Qt
from PyQt4 import QtCore


progname = path.basename(sys.argv[0])
progversion = "0.1"


class Point:
    def __init__(self, pos, callback=None):
        self.callback = callback
        self.line = plt.axvline(pos, ls="--", c="k")
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

        # Create PLOT graph GUI
        # plt.ion()
        self.fig, self.ax = plt.subplots()
        self.fig.set_tight_layout(False)
        self.fig.canvas.set_window_title(progname + ' Ver.' + progversion)
        self.fig.suptitle('BL7D MCA with ROI bar')
        # first plot mca data
        self.ax.plot(self.x, self.mcas[0], self.x, self.mcas[1],
                     self.x, self.mcas[2], self.x, self.mcas[3],
                     self.x, self.mcas[4], self.x, self.mcas[5],
                     self.x, self.mcas[6], linewidth=1.0)

        # self.ax = self.fig.gca()
        self.ax.set_autoscaley_on(True)

        # self.ax.plot(self.x, ydata)
        self.ax.grid()

        self.lowROI  = Point(max(self.x) * 0.3, self.callback)
        self.highROI = Point(max(self.x) * 0.7, self.callback)

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
        # self.commSignal.emit()  # emit the signal
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

        # TODO : implement ROI avarage
        for i in range(0, self.noOfElement, 1):
            avgMca = avgMca + sum(self.mcas[i][int(self.lowROI.pos):int(self.highROI.pos)])

        print('=== Average: --%d-- ') %(avgMca / self.noOfElement), time.ctime()

        if self.ax.lines:
            i = 0
            for line in self.ax.lines:
                # total 9(6mca + 2 axvline) line, so need remove last 2(axvline) lines
                if i < 7:
                    line.set_xdata(self.x)
                    line.set_ydata(self.mcas[i])
                    i += 1
                else:
                    pass

        # self.ax.set_ylim(0, 50)
        #- self.ax.set_xlim(0, 2048)
        # self.ax.grid()
        # self.canvas.draw()

        #- self.ax.autoscale_view(scalex=False)
        # We need to draw *and* flush
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    # --------------------------------------------------------------------------

    def callback(self):
        # TODO: implement cursor freez of min/max use self.lowROI.get_xbound()
        if self.lowROI.pos < 0 or None:
            self.lowROI.line.set_xdata(10)
            self.lowROI.pos = 10
        if self.highROI.pos < 100 or None:
            self.highROI.line.set_xdata(100)
            self.highROI.pos = 100

        self.ax.figure.canvas.draw()


l = LineFitter()

plt.show()