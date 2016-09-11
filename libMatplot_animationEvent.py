"""
Emulate an oscilloscope.  Requires the animation API introduced in
matplotlib 1.0 SVN.
"""
import numpy as np
import matplotlib
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import readline
import epics
import time


class Scope(object):
    def __init__(self, ax, maxt=2, dt=0.02):
        print('matplotlib version: ', matplotlib.__version__)
        self.ax = ax
        self.dt = dt
        self.maxt = maxt
        self.tdata = [0]
        self.ydata = [0]
        self.line = Line2D(self.tdata, self.ydata)
        self.ax.add_line(self.line)
        self.ax.set_ylim(-.1, 50000.0)
        self.ax.set_xlim(0, self.maxt)

    def update(self, y):
        lastt = self.tdata[-1]
        if lastt > self.tdata[0] + self.maxt:  # reset the arrays
            self.tdata = [self.tdata[-1]]
            self.ydata = [self.ydata[-1]]
            self.ax.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
            self.ax.figure.canvas.draw()

        t = self.tdata[-1] + self.dt
        self.tdata.append(t)
        self.ydata.append(y)
        self.line.set_data(self.tdata, self.ydata)
        return self.line,

'''
def emitter(p=0.03):
    'return a random value with probability p, else 0'
    while True:
        v = np.random.rand(1)
        if v > p:
            yield 0.
        else:
            yield np.random.rand(1)
'''

def emitter():
    'return a random value with probability p, else 0'
    dxpMca1PV = epics.PV('BL7D:dxpXMAP:mca1')
    dxpAcqPV = epics.PV('BL7D:dxpXMAP:Acquiring')
    mcas = 0.0
    oldAcqStatus = 1
    nowAcqStatus = 0


    while True:
        nowAcqStatus = dxpAcqPV.get()

        if nowAcqStatus is 1 and oldAcqStatus is 0 :
            mcas = sum(dxpMca1PV.get())
            oldAcqStatus = nowAcqStatus
            yield mcas

        else:
            oldAcqStatus = nowAcqStatus
            yield mcas

fig, ax = plt.subplots()
scope = Scope(ax)

# pass a generator in "emitter" to produce data for the update func
# animation.FuncAnimation(fig, func, frames=None, init_func=None, fargs=None, save_count=None, **kwargs)
# class matplotlib.animation.Animation(fig, event_source=None, blit=False)

#ani = animation.Animation(fig, event_source=None, blit=False)
ani = animation.FuncAnimation(fig, scope.update, emitter, interval=100,
                              blit=True)

plt.show()