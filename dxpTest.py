""" this is dxpXMAp test file """

import epics
import time
import readline

dxpMcaPVs = []
mcas = []

for i in range(1,8,1):
    dxpMcaPVs.append(epics.PV('BL7D:dxpXMAP:mca' + str(i)))

dxpStartPV = epics.PV("BL7D:dxpXMAP:EraseStart")
dxpAcqPV = epics.PV('BL7D:dxpXMAP:Acquiring')

gotChanges = 0

def onChanges(pvname=None, value=None, char_value=None, **kw):
    global gotChanges, dxpMcaPVs

    print '=== PV Changed!!! ', pvname, char_value, time.ctime()
    if char_value != '0':
        print '--- Acquiring...---'
        return

    for i in dxpMcaPVs :
        mcaTemp = i.get()
        mcas.append(mcaTemp.max())
        print '--- Got data, Max: %d' %mcaTemp.max()

    gotChanges = 1

dxpAcqPV.add_callback(onChanges)

print "==============Now wait for changes===========\n"

t0 = time.time()

while( (time.time() - t0) < (3600 * 12) ):
   if gotChanges == 1:
       time.sleep(1.0)
       gotChanges = 0
       print '\n--- Again Start/Erase\n'
       dxpStartPV.put(1)
   else :
       time.sleep(1.e-3)

print 'DONE'
