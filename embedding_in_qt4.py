# -*- encoding: utf-8 -*-
# embedding_in_qt4.py --- Simple Qt4 application embedding matplotlib canvases

from __future__ import unicode_literals
import sys
import os
import random
from matplotlib.backends import qt_compat
use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore
else:
    from PyQt4 import QtGui, QtCore
from numpy import arange, sin, pi, linspace
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import epics
import readline
import time


progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=200):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        # We want the axes cleared every time plot() is called
        self.axes.hold(False)
        # TODO: is not working properly?
        self.axes.grid()

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""

    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.plot(t, s)

    def computer_sum(self, mcas):
        sums = 0.0

        for i in range(0, len(mcas)):
            sums = sums + sum(mcas[i])

        sums = sums / (i+1)
        print 'sum: %d' %sums


class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every Acquiring-PV with a new plot."""

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        # timer = QtCore.QTimer(self)
        # timer.timeout.connect(self.update_figure)
        # timer.start(2000)
        # -------------------------------------------------------------------
        self.dxpMcaPVs = []
        self.mcas = []

        for i in range(1, 8, 1):
            self.dxpMcaPVs.append(epics.PV('BL7D:dxpXMAP:mca' + str(i)))

        self.dxpStartPV = epics.PV("BL7D:dxpXMAP:EraseStart")
        self.dxpAcqPV = epics.PV('BL7D:dxpXMAP:Acquiring')

        # TODO: how can update mca bins? it update self.xlim value
        self.xlim = 2048
        self.n = linspace(0, self.xlim - 1, self.xlim)
        self.addCallbackAcq()

        self.c = MyStaticMplCanvas()

    def compute_initial_figure(self):
        pass # self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')

    # callback for get mca data.
    def OnChanged(self, pvname=None, value=None, char_value=None, **kw):
        if value is 1: # value 1=Acquiring, 0=Done
            print 'Acquiring...', time.ctime()
            return
        self.mcas = []
        for i in self.dxpMcaPVs :
            self.mcas.append(i.get())

        self.update_figure()

    def addCallbackAcq(self):
        # IMPORTANT: add_callback definition position. it define after callback function
        self.dxpAcqPV.add_callback(self.OnChanged)

    def update_figure(self):
        # Build a list of all MCA integers between 0 to self.xlim length
        # self.axes.plot(self.n, self.mcas[0], 'b-', self.n, self.mcas[1], 'r-', linewidth=0.5)
        self.axes.plot(self.n, self.mcas[0],
                       self.n, self.mcas[1],
                       self.n, self.mcas[2],
                       self.n, self.mcas[3],
                       self.n, self.mcas[4],
                       self.n, self.mcas[5],
                       self.n, self.mcas[6], linewidth=0.5)

        # self.axes.set_xlim(540, 680)
        self.axes.grid()
        self.draw()
        self.c.computer_sum(self.mcas)


class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        # self.setWindowTitle("application main window")
        # self.setWindowIcon(QtGui.QIcon('test_icon.png'))

        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtGui.QWidget(self)

        l = QtGui.QVBoxLayout(self.main_widget)
        sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=80)
        dc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=80)
        l.addWidget(sc)
        l.addWidget(dc)

        # Place the toolbar
        self.navi_toolbar = NavigationToolbar(dc, self.main_widget)
        # if use grid_layout use like this, self.LAYOUT_A.addWidget(self.navi_toolbar, *(1, 1))
        l.addWidget(self.navi_toolbar)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("All hail matplotlib!", 2000)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtGui.QMessageBox.about(self, "About",
                                """embedding_in_qt4.py example
Copyright 2016 WoulWoo Lee

This program is a simple mca monitoring of DXP detector example.
use Qt4 application embedding matplotlib canvases.

It may be used and modified with no restriction; raw copies as well as
modified versions may be distributed without limitation."""
                                )

if __name__ == '__main__':
    qApp = QtGui.QApplication(sys.argv)
    aw = ApplicationWindow()
    aw.setWindowTitle("%s Ver %s" %(progname, progversion))
    aw.setWindowIcon(QtGui.QIcon('test_icon.png'))
    aw.show()
    sys.exit(qApp.exec_())
    # qApp.exec_()
