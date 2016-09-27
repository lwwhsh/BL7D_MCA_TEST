"""
The SpanSelector is a mouse widget to select a xmin/xmax range and plot the
detail view of the selected region in the lower axes
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
from matplotlib.widgets import Cursor
from epics import PV
import epics
import readline


class TestMCAdisplay:
    def __init__(self):
        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(211) #, axisbg='#FFFFCC')

        self.x = np.arange(0, 2048, 1)  # mca has 2048 channels
        self.y = epics.caget('BL7D:dxpXMAP:mca4')   # np.sin(2 * np.pi * self.x) + 0.5 * np.random.randn(len(self.x))

        self.lines, = self.ax.plot(self.x, self.y, '-')
        self.ax.set_ylim(-2, 2)
        self.ax.set_title('Press left mouse button and drag to test')

        self.ax2 = self.fig.add_subplot(212) #, axisbg='#FFFFCC')
        self.line2, = self.ax2.plot(self.x, self.y, '-')

        self.mca4PV = PV('BL7D:dxpXMAP:mca4',
                         callback=self.mcaSpetrumCALLBACK)

    def mcaSpetrumCALLBACK(self, **kwargs):
        self.y = kwargs['value']
        self.lines.set_data(self.x, self.y)
        #self.ax.set_xlim(0, self.y.__len__() - 1) # 2047)
        self.ax.set_ylim(self.y.min(), self.y.max())
        #self.ax.set_autoscale_on(True)
        self.fig.canvas.draw()

    def onselect(self, xmin, xmax):
        indmin, indmax = np.searchsorted(self.x, (xmin, xmax))
        print('indmin:%d, indmax:%s, xmin:%d, xmax:%d') %(indmin, indmax, xmin, xmax)
        indmax = min(len(self.x) - 1, indmax)

        thisx = self.x[indmin:indmax]
        thisy = self.y[indmin:indmax]
        self.lines.set_data(thisx, thisy)
        self.ax.set_xlim(thisx[0], thisx[-1])
        self.ax.set_ylim(thisy.min(), thisy.max())
        # self.ax.set_autoscale_on(True)
        self.fig.canvas.draw()


def main():
    disp = TestMCAdisplay()

    # set useblit True on gtkagg for enhanced performance
    span = SpanSelector(disp.ax, disp.onselect, 'horizontal',
                        useblit=True, rectprops=dict(alpha=0.5, facecolor='red'))

    # cursor = Cursor(disp.ax2, useblit=True, color='yellow', linewidth=1)

    plt.show()


if __name__ == '__main__':
    main()
