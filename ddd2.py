#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

## namespace organization changed in PyQt5 but the class name was kept.
## importing this way makes it easier to change to PyQt5 later
from PyQt4.QtGui import (QMainWindow, QApplication, QDockWidget, QWidget,
                         QGridLayout, QSlider)
from PyQt4.QtCore import Qt
from PyQt4 import QtCore

import numpy
import matplotlib.pyplot
import matplotlib.backends.backend_qt4agg

import readline
import epics
import time
import os


progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class MainWindow(QMainWindow):

  # TODO: How can change max bins(energy) value.
  # define X axis for mca bins
  x = numpy.arange(0, 2048, 1)

  # define and initialise signal for mca Done callback signal
  # commSignal = QtCore.pyqtSignal(object)
  commSignal = QtCore.Signal()

  def __init__(self):
    QMainWindow.__init__(self)

    self.commSignal.connect(self.plot)

    self.figure  = matplotlib.pyplot.figure()
    self.drawing = self.figure.add_subplot(111)
    self.canvas  = matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg(self.figure)

    self.setCentralWidget(self.canvas)

    dock = QDockWidget("Values")
    self.addDockWidget(Qt.RightDockWidgetArea, dock)

    sliders = QWidget()
    sliders_grid = QGridLayout(sliders)

    self.dxpAcqPV  = epics.PV('BL7D:dxpXMAP:Acquiring')

    self.dxpMcaPVs = []
    self.NoOfElement = 7

    for i in range(1, 8, 1):
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
    for i in range(0, self.NoOfElement, 1) :
       avgMca = avgMca + sum(mcas[i])

    print('Average: %d ') %(avgMca / self.NoOfElement)

    # TODO : please implement zoom in / zoom out.
    self.drawing.plot(self.x, mcas[0],
                      self.x, mcas[1],
                      self.x, mcas[2],
                      self.x, mcas[3],
                      self.x, mcas[4],
                      self.x, mcas[5],
                      self.x, mcas[6], linewidth=1.0)

    self.drawing.set_ylim(0, 2500)
    self.drawing.set_xlim(550, 680)
    self.drawing.grid()
    self.canvas.draw()

if __name__ == "__main__":
  app = QApplication(sys.argv)
  main = MainWindow()
  main.show()
  sys.exit(app.exec_())
