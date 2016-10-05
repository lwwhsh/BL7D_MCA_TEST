###################################################################
#                                                                 #
#                     PLOTTING A LIVE GRAPH                       #
#                  ----------------------------                   #
#            EMBED A MATPLOTLIB ANIMATION INSIDE YOUR             #
#            OWN GUI!                                             #
#                                                                 #
###################################################################

from __future__ import print_function
import readline
import epics
import sys
import os
import functools
import random as rd
from PyQt4 import QtGui
from PyQt4 import QtCore
import numpy as np
import matplotlib
from matplotlib.figure import Figure
from matplotlib.animation import TimedAnimation
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import time
import threading
matplotlib.use("Qt4Agg")


def setCustomSize(x, width, height):
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(x.sizePolicy().hasHeightForWidth())
    x.setSizePolicy(sizePolicy)
    x.setMinimumSize(QtCore.QSize(width, height))
    x.setMaximumSize(QtCore.QSize(width, height))

''''''


class CustomMainWindow(QtGui.QMainWindow):

    def __init__(self):

        super(CustomMainWindow, self).__init__()

        # Define the geometry of the main window
        self.setGeometry(300, 300, 800, 400)
        self.setWindowTitle("Plotting in Live Graph, Ver 0.1")

        # Place the QUIT sub menu in the File menu
        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        # Create FRAME_A
        self.FRAME_A = QtGui.QFrame(self)
        self.FRAME_A.setStyleSheet("QWidget { background-color: %s }"
                                   % QtGui.QColor(210, 210, 235, 255).name())
        self.LAYOUT_A = QtGui.QGridLayout()
        self.FRAME_A.setLayout(self.LAYOUT_A)
        self.setCentralWidget(self.FRAME_A)

        # Place the zoom button
        self.zoomBtn = QtGui.QPushButton(text='Fit...')
        setCustomSize(self.zoomBtn, 100, 50)
        self.zoomBtn.clicked.connect(self.zoomBtnAction)    # send signal.
        self.LAYOUT_A.addWidget(self.zoomBtn, *(0, 0))

        # Place the matplotlib figure
        self.myFig = CustomFigCanvas()
        self.LAYOUT_A.addWidget(self.myFig, *(0, 1))

        # Place the toolbar
        self.navi_toolbar = NavigationToolbar(self.myFig, self.FRAME_A)
        self.LAYOUT_A.addWidget(self.navi_toolbar, *(1, 1))

        # Add the callbackfunc to ..
        myDataLoop = threading.Thread(name   = 'myDataLoop',
                                      target = dataSendLoop,
                                      args   = (self.addData_callbackFunc,))
        myDataLoop.start()

        self.show()

    ''''''

    def zoomBtnAction(self):
        self.myFig.zoomIn(5)

    def addData_callbackFunc(self, value):
        # print("Add data: " + str(value))
        self.myFig.addData(value)
        ## epics.caput('BL7D:dxpXMAP:EraseStart', 1)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()


''' End Class '''


class CustomFigCanvas(FigureCanvas, TimedAnimation):

    def __init__(self):

        self.addedData = []
        print(matplotlib.__version__)

        # The data
        self.xlim = 2048
        self.n = np.linspace(0, self.xlim - 1, self.xlim)
        self.y = epics.caget("BL7D:dxpXMAP:mca1")

        # The window
        self.fig = Figure(figsize=(5,5), dpi=75)
        self.ax1 = self.fig.add_subplot(111)

        self.ax1.grid()
        self.ax1.hold(False)

        # self.ax1 settings
        self.ax1.set_xlabel('bins')
        self.ax1.set_ylabel('count data')
        self.line1 = Line2D([], [], color='blue')
        self.line1_tail = Line2D([], [], color='red', linewidth=1)
        self.line1_head = Line2D([], [], color='red', marker='o', markeredgecolor='r')
        self.ax1.add_line(self.line1)
        self.ax1.add_line(self.line1_tail)
        self.ax1.add_line(self.line1_head)

        FigureCanvas.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval=100, blit=True)

    def new_frame_seq(self):
        return iter(range(self.n.size))

    def _init_draw(self):
        lines = [self.line1, self.line1_tail, self.line1_head]
        for l in lines:
            l.set_data([], [])

    def addData(self, value):
        self.addedData.append(value)

    def zoomIn(self, value):
        self.ax1.relim()
        self.ax1.set_autoscale_on(True)
        self.ax1.autoscale(enable=True, axis='both', tight=True)
        self.ax1.autoscale_view(tight=True, scalex=True, scaley=True)

        self.draw()

    def _step(self, *args):
        # Extends the _step() method for the TimedAnimation class.
        try:
            TimedAnimation._step(self, *args)
        except Exception as e:
            self.abc += 1
            print(str(self.abc))
            TimedAnimation._stop(self)
            pass

    def _draw_frame(self, framedata):
        margin = 2
        while(len(self.addedData) > 0):
            self.y = np.roll(self.y, -1)
            self.y[-1] = self.addedData[0]
            del(self.addedData[0])

        self.line1.set_data(self.n[0: self.n.size - margin],
                            self.y[0: self.n.size - margin])
        self.line1_tail.set_data(np.append(self.n[-10: -1 - margin],
                                           self.n[-1 - margin]),
                                           np.append(self.y[-10: -1 - margin],
                                                     self.y[-1 - margin]))
        self.line1_head.set_data(self.n[-1 - margin], self.y[-1 - margin])
        self._drawn_artists = [self.line1, self.line1_tail, self.line1_head]


''' End Class '''


# You need to setup a signal slot mechanism, to
# send data to your GUI in a thread-safe way.
# Believe me, if you don't do this right, things
# go very very wrong..
class Communicate(QtCore.QObject):
    data_signal = QtCore.pyqtSignal(float)


''' End Class '''


onChangedSignal = 0
mcas = 0.
dxpMCAs = []

dxpMcaPVs = []
for i in range(1, 8, 1):
    dxpMcaPVs.append(epics.PV('BL7D:dxpXMAP:mca' + str(i)))


def onChanged(pvname=None, value=None, char_value=None, **kw):
    global onChangedSignal, mcas, dxpMcaPV, dxpMCAs
    if value is 1:  # 1=Acquiring, 0=Done.
        # print('Acquiring... ', time.ctime())
        onChangedSignal = 0
        return

    mcas = 0.0

    '''
    for i in dxpMcaPVs:
        mcas = mcas + sum(i.get())

    mcas = (mcas / dxpMcaPVs.__len__())
    '''
    # mcas = sum(dxpMcaPVs[0].get())
    dxpMCAs = []
    for i in dxpMcaPVs:
        dxpMCAs.append(i.get())
    for i in range(0, 7, 1):
        mcas = mcas + sum(dxpMCAs[i][610:680])

    mcas = mcas / 7
    print("MCAs Average... ", mcas)

    onChangedSignal = 1

    # mySrc.data_signal.emit(mcas)


def dataSendLoop(addData_callbackFunc):
    global onChangedSignal, mcas, dxpMcaPV

    # Setup the signal-slot mechanism.
    mySrc = Communicate()
    mySrc.data_signal.connect(addData_callbackFunc)

    onChangedSignal = 0
    mcas = 0.0
    # epics.caput('BL7D:dxpXMAP:EraseStart', 1)

    dxpAcqPV  = epics.PV('BL7D:dxpXMAP:Acquiring', callback=onChanged)
    # epics.caput('BL7D:dxpXMAP:EraseStart', 1)

    while True:
        if onChangedSignal is 1:
            onChangedSignal = 0
            time.sleep(1.0)
            mySrc.data_signal.emit(mcas)  # <- Here you emit a signal!
            # epics.caput('BL7D:dxpXMAP:EraseStart', 1)

        time.sleep(0.02)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Plastique'))
    myGUI = CustomMainWindow()

    sys.exit(app.exec_())
