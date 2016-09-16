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


class MainWindow(QMainWindow):

  # TODO: How can change max bins(energy) value.
  # define X axis for mca bins
  x = numpy.arange(0, 2048, 1)

  cos = 0
  sin = 0

  # add LWW
  # define and initialise signal for mca Done callback signal
  commSignal = QtCore.pyqtSignal(object)

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
    self.dxpMca1PV = epics.PV('BL7D:dxpXMAP:mca1')
    self.dxpMca2PV = epics.PV('BL7D:dxpXMAP:mca2')
    self.dxpMca3PV = epics.PV('BL7D:dxpXMAP:mca3')

    self.plot()
    self.addCallbackAcq()

  def onChanged(self, pvname=None, value=None, char_value=None, **kw):
      # print('onChanged: '), char_value, time.ctime()
      if value is 1 : # value 1=Acquiring, 0=Done
          return
      # self.plot()
      self.commSignal.emit(self.plot)

  def addCallbackAcq(self):
      # IMPORTANT: add_callback definition position. it define after callback function
      self.dxpAcqPV.add_callback(self.onChanged)

  def plot(self):
    self.drawing.hold(False)
    s = self.dxpMca1PV.get()
    c = self.dxpMca2PV.get()
    b = self.dxpMca3PV.get()
    print('Average: %d ') %sum((s+c+b) / 3)

    self.drawing.plot(self.x, s, 'r', self.x, c, 'g', self.x, b, 'b')
    self.drawing.set_ylim(0, 2500)
    self.drawing.set_xlim(550, 680) # Todo : please implement zoom in / zoom out.
    self.drawing.grid()
    self.canvas.draw()

if __name__ == "__main__":
  app = QApplication(sys.argv)
  main = MainWindow()
  main.show()
  sys.exit(app.exec_())