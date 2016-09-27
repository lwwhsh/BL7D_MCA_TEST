from matplotlib import pyplot as plt
import numpy as np


class MovingPlot(object):
    """ MovingPlot plots a figure that flows across the screen.  Right and left
    arrows move the figure one step"""


    def __init__(self, r0=[-0.8, 1.0], v0=[0.1, 0.]):
        # set up grid
        r = np.linspace(0.2, 2, 20)
        t = np.linspace(np.pi / 4, 7 * np.pi / 4, 20)
        r, t = np.meshgrid(r, t)
        self.x = r * np.cos(t)
        self.y = r * np.sin(t)

        self.x0 = r0[0]
        self.y0 = r0[1]
        self.vx = v0[0]
        self.vy = v0[1]

        # create figure and axes for reuse
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

        self.ax.axvline(0.5, ls="--", c="k", lw=2)

        # draw the initial frame
        self.frame = 0
        self.draw(self.frame)

        # call self.update everytime a 'key_press_event' happens
        # bind this behavior to an object so it persists
        self.cid = self.fig.canvas.mpl_connect('key_press_event', self.update)
        plt.show()


    def update(self, event):
        """Changes the frame number based on event and draws a new frame if the
        frame changed"""
        if event.key == 'right':
            print 'forward'
            self.frame += 1
        elif event.key == 'left':
            print 'backward'
            self.frame -= 1
        else:
            return
        self.draw(self.frame)


    def draw(self, t):
        """Draws the frame occuring at time=t"""
        x = self.x - self.vx * t
        y = self.y - self.vy * t
        z = (x - self.x0) ** 2 + (y - self.y0) ** 2
        self.ax.pcolor(self.x, self.y, z)
        self.fig.canvas.draw()


if __name__ == "__main__":
    mplot = MovingPlot()