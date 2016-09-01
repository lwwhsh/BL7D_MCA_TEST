import readline
import epics
import time
import numpy as np
import pylab as pl
from drawnow import drawnow

dxpMcaPVs = []
mcas = []


mcasNP = np.zeros((7, 2048), dtype='i', order='C')

# make X axis value
x = []
for i in range(0, 2048, 1):
    x.append(i)

for i in range(1, 8, 1):
    dxpMcaPVs.append(epics.PV('BL7D:dxpXMAP:mca' + str(i)))

dxpAcqPV = epics.PV('BL7D:dxpXMAP:Acquiring')

gotChanges = 0

# callback for get mca data.
def OnChanged(pvname=None, value=None, char_value=None, **kw):
    global gotChanges, x, mcas

    if char_value != '0':
        return

    mcas = []

    print dxpMcaPVs

    for i in dxpMcaPVs:
        mcas.append(i.get())

    gotChanges = 1

dxpAcqPV.add_callback(OnChanged)



def makeFig():
    pl.plot(x, mcas[0],
            x, mcas[1],
            x, mcas[2],
            x, mcas[3],
            x, mcas[4],
            x, mcas[5],
            x, mcas[6])

pl.ion()            # enable interactivity
fig = pl.figure()   # make a figure



t0 = time.time()

while((time.time() - t0) < (3600 * 12)):
   if gotChanges == 1:
       '''
       pl.cla()

       pl.plot(x, mcas[0],
               x, mcas[1],
               x, mcas[2],
               x, mcas[3],
               x, mcas[4],
               x, mcas[5],
               x, mcas[6])

       pl.grid(True)
       pl.xlabel('Bins')
       pl.xlabel('Counts')

       pl.show()
       pl.draw()
       '''

       drawnow(makeFig)

       gotChanges = 0

   else :
       time.sleep(0.05)

pl.close()

print 'DONE'
