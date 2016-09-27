from pylab import *


class Point:
    def __init__(self, pos, callback=None):
        self.callback = callback
        self.line = axvline(pos, ls="--", c="k")
        self.pos = pos
        self.active = False

        connect('button_press_event', self.on_press)
        connect('button_release_event', self.on_release)
        connect('motion_notify_event', self.on_motion)

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
    def __init__(self, apos, bpos, xdata, ydata):
        self.ax = figure().gca()
        self.ax.plot(xdata, ydata)

        self.a = Point(apos, self.callback)
        self.b = Point(bpos, self.callback)
        self.xdata = xdata
        self.ydata = ydata
        #self.plot_data, = self.ax.plot([], [], lw=4)
        #self.plot_fit, = self.ax.plot([], [], lw=2)

        #self.ax2 = figure().gca()
        #self.plot_corrected, = self.ax2.plot(xdata, ydata)

    def callback(self):
        #aa, bb = sort([self.a.pos, self.b.pos])
        #m = (self.xdata >= aa) & (self.xdata <= bb)

        #self.plot_data.set_data(self.xdata[m], self.ydata[m])

        #cc = (bb - aa) / 5
        #xx = array([aa - cc, bb + cc])

        #a, b = polyfit(x[m], y[m], 1)

        #self.plot_fit.set_data(xx, a * (xx + b / a))
        #self.plot_corrected.set_data(self.xdata + b / a - self.ydata / a, self.ydata)

        # self.ax2.autoscale()  ????

        ''' manual set line position like this
        self.a.line.set_xdata(0.4)
        self.b.line.set_xdata(0.5)
        '''
        self.ax.figure.canvas.draw()
        #self.ax2.figure.canvas.draw()


# y, x = loadtxt("FeAl28-sample1-2.XLS", usecols=(2, 3), unpack=True)[:, 5:-2]
x = np.arange(0.0, 1.0, 0.01)
y = np.sin(2 * 2 * np.pi * x)

# x = -x

l = LineFitter(amax(x) * 0.1, amax(x) * 0.2, x, y)

show()