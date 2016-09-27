# -*- coding: utf-8 -*-
__author__ = 'ZhiberKA'

import pyqtgraph as pg
import pyqtgraph.functions as fn
from PyQt4 import QtCore


class CustomViewBox(pg.ViewBox):
    """This class overrides behaviour of parent class. Scaling is performed by mouse wheel when key "CTRL" is pressed.
    Translating is performed by dragging and by mouse wheel.
    """
    mouseWheeled = QtCore.pyqtSignal(object, object)

    def wheelEvent(self, ev, axis=None):
        ev.accept()
        self.onMouseWheeled(ev, axis)
        self.sigRangeChangedManually.emit(self.state['mouseEnabled'])
        self.mouseWheeled.emit(ev, axis)

    def onMouseWheeled(self, ev, axis):
        # case of scaling
        if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
            mask = np.array(self.state['mouseEnabled'], dtype=np.float)
            if axis is not None and axis >= 0 and axis < len(mask):
                mv = mask[axis]
                mask[:] = 0
                mask[axis] = mv
            s = ((mask * 0.02) + 1) ** (ev.delta() * self.state['wheelScaleFactor']) # actual scaling factor
            center = pg.Point(fn.invertQTransform(self.childGroup.transform()).map(ev.pos()))
            self.scaleBy(s, center)
            return

        # case of translating
        ## Ignore axes if mouse is disabled
        mouseEnabled = np.array(self.state['mouseEnabled'], dtype=np.float)
        mask = mouseEnabled.copy()
        if axis is not None:
            mask[1 - axis] = 0.0

        d = map(lambda x: (x[1] - x[0]) / 10, self.viewRange())
        d = np.array(d)
        direct = ev.delta() / 120
        tr = d * direct * mask
        x = tr[0] if mask[0] == 1 else None
        y = tr[1] if mask[1] == 1 else None
        self.setTransformOriginPoint(ev.scenePos())
        self.translateBy(x=x, y=y)


class CrosshairManager(object):
    """This class creates an object that manages the crosshair interaction on plotItem."""
    def __init__(self):
        self.label = pg.LabelItem(justify='right')
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.plt = None

    def linkWithPlotItem(self, plt):
        if self.plt is not None:
            self.plt.remove(self.vLine)
            self.plt.remove(self.hLine)
            self.plt.getViewBox().mouseWheeled.disconnect(self._onMouseWheeled)

        self.plt = plt
        self.plt.addItem(self.vLine, ignoreBounds=True)
        self.plt.addItem(self.hLine, ignoreBounds=True)
        self.proxy = pg.SignalProxy(self.plt.scene().sigMouseMoved, rateLimit=60, slot=self._onMouseMoved)
        self.plt.getViewBox().mouseWheeled.connect(self._onMouseWheeled)

    def _onMouseMoved(self, evt):
        pos = evt[0]
        if self.plt.sceneBoundingRect().contains(pos):
            self._updateCrosshair(pos)

    def _onMouseWheeled(self, evt, axis):
        pos = evt.scenePos()
        self._updateCrosshair(pos)

    def _updateCrosshair(self, pos):
        mousePoint = self.plt.getViewBox().mapSceneToView(pos)
        self.label.setText("<span style='font-size: 12pt'>x=%0.1f" % mousePoint.x())
        self.vLine.setPos(mousePoint.x())
        self.hLine.setPos(mousePoint.y())


if __name__ == "__main__":
    from PyQt4 import QtGui
    import sys
    import numpy as np

    app = QtGui.QApplication(sys.argv)
    view = pg.GraphicsLayoutWidget()
    plt = pg.PlotItem(viewBox=CustomViewBox())
    plt.getViewBox().setMouseEnabled(True, False)
    view.addItem(plt, row=1, col=0)

    curve = pg.PlotCurveItem()
    x = np.linspace(0, 100, 100)
    y = np.sin(x)
    curve.setData(x, y)
    plt.addItem(curve)

    c = CrosshairManager()
    c.linkWithPlotItem(plt)
    view.addItem(c.label, row=0, col=0)
    view.show()
    app.exec_()
