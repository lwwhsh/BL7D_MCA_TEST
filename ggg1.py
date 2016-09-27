import sys
from PyQt4.QtGui import QWidget, QPushButton, QMainWindow, QMdiArea, QVBoxLayout, QApplication
from PyQt4.QtCore import Qt

from pylab import *
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backend_bases import key_press_handler


class MyMainWindow(QMainWindow):
    """ Defines a simple MainWindow with a QPushButton that plots a Random Wave Fucntion
    which must be shown in a Window within a QMdiArea Widget.
    """

    def __init__(self, parent=None):
        """
        """

        super(MyMainWindow,self).__init__(parent)
        self.setWidgets()

    def setWidgets(self, ):
        """ Createsthe QPushButton and QMdiArea Widgets, organising them in
        QVBoxLayout as a central Widget of the MainWindow
        """

        vBox = QVBoxLayout()
        mainFrame = QWidget()

        self._plotGraphButton = QPushButton("Plot Graph")
        self._plotGraphButton.clicked.connect(self.plotRandom)

        self._mdiArea = QMdiArea()
        vBox.addWidget(self._plotGraphButton)
        vBox.addWidget(self._mdiArea)

        mainFrame.setLayout(vBox)
        self.setCentralWidget(mainFrame)


    # This is the function called when the Plot Graph Button is pressed
    #and where the Picking event does not work.
    # When the button is pressed a new window with the plot is shown, but
    #it is not possible to drag the rectangle patch with the mouse.
    def plotRandom(self, ):
        """ Generates and Plots a random wave function (+noise) embedding into a
        QMdiAreaSubWindow.
        """
        print "Plotting!!"
        x = linspace(0,10,1000)
        w = rand(1)*10
        y = 100*rand(1)*sin(2*pi*w*x)+rand(1000)

        p = PlotGraph(x,y)
        child = self._mdiArea.addSubWindow(p.plotQtCanvas())
        child.show()



class PlotGraph(object):
    """
    """

    def __init__(self, x,y):
        """ This class plots the data and encapsulates the figure instance in a FigureCanvasQt4Agg,
        which can be used to create a QMdiArea SubWindow.
         A rectangle patch is added to the plot and linked to the methods that
        can drag it horizontally in the graph.

        Arguments:
        - `x`: Data
        - `y`: Data
        """
        self._x = x
        self._dx = x[1]-x[0]
        self._y = y


    def _createPlotWidget(self, ):
        """ Creates a figure and a NavigationBar organising them vertically into a QWidget,
        which can be used by a QMdiArea.addSubWindow method.
        """
        self._mainFrame = QWidget()

        self._fig = figure(facecolor="white")
        self._canvas = FigureCanvas(self._fig)
        self._canvas.setParent(self._mainFrame)
        self._canvas.setFocusPolicy(Qt.StrongFocus)

        # Standard NavigationBar and button press management
        self._mplToolbar = NavigationToolbar(self._canvas, self._mainFrame)
        self._canvas.mpl_connect('key_press_event', self.on_key_press)

        # Layouting
        vbox = QVBoxLayout()
        vbox.addWidget(self._canvas)  # the matplotlib canvas
        vbox.addWidget(self._mplToolbar)
        self._mainFrame.setLayout(vbox)

    def plotQtCanvas(self, ):
        """ Plots data using matplotlib, adds a draggable Rectangle and connects the dragging
        methods to the mouse events
        """
        self._createPlotWidget()
        ax = self._fig.add_subplot(111)
        ax.plot(self._x,self._y)
        ax.set_xlim(self._x[0],self._x[-1])
        ax.set_ylim(-max(self._y)*1.1,max(self._y)*1.1)

        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        wd = (xlim[1]-xlim[0])*0.1
        ht = (ylim[1]-ylim[0])

        rect = Rectangle((xlim[0],ylim[0]),wd,ht,alpha=0.3,color="g",picker=True)
        ax.add_patch(rect)


        # Connecting Events to Rectangle dragging methods
        self._canvas.mpl_connect("pick_event",self.on_pick)
        self._canvas.mpl_connect("button_release_event",self.on_release)

        return self._mainFrame

    def on_pick(self,event):
        """ Manages the Artist Picking event. This method register which
        Artist was picked and connects the rectOnMove method to the mouse
        motion_notify_event SIGNAL.

        Arguments:
        - `event`:
        """
        if isinstance(event.artist, Rectangle):

            rectWd = event.artist.get_width()
            if event.mouseevent.button == 1:
                self._dragged = event.artist
                self._id = self._canvas.mpl_connect("motion_notify_event",self.rectOnMove)


    def rectOnMove(self, event):
        """ After being picked, updates the new position of the Artist.

        Arguments:
        - `event`:
        """
        rectWd = self._dragged.get_width()
        if event.xdata:
            i = event.xdata
            n2 = rectWd/2.0
            if i>=n2 and i<(self._x[-1]-n2):
                self._dragged.set_x(i-n2)
                self._canvas.draw()

    def on_release(self,event):
        """ When the mouse button is released, simply disconnect the
        SIGNAL motion_notify_event and the rectOnMove method.

        Arguments:
        - `event`:
        """
        self._canvas.mpl_disconnect(self._id)


    def on_key_press(self, event):
        # implement the default mpl key press events described at
        # http://matplotlib.org/users/navigation_toolbar.html#navigation-keyboard-shortcuts
        key_press_handler(event, self._canvas, self._mplToolbar)



if __name__ == '__main__':
    qApp = QApplication(sys.argv)
    MainWindow = MyMainWindow()

    # By calling the piece of code bellow everything works fine and the
    # the rectangle patch can be dragged, as expected.

    # This piece of code "theoretically" does the same thing as the
    # method plotRandom() defined in the class MyMainWindow.
    print "Plotting!!"
    x = linspace(0,10,1000)
    w = rand(1)*10
    y = 100*rand(1)*sin(2*pi*w*x)
    ####################################################################

    p = PlotGraph(x,y)
    child = MainWindow._mdiArea.addSubWindow(p.plotQtCanvas())
    child.show()

    MainWindow.show()
    sys.exit(qApp.exec_())