#!/usr/bin/env python
"""
Fit each of the two peaks to a lorentzian profile.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

from show_scope import TekCSV

FILENAME = 'F0001CH2.CSV'

csv = TekCSV(FILENAME)

time = csv.data[:, 3]
volts = csv.data[:, 4]

# Normalizing the data
# limit the data for single quantum case
mask1 = (5.19 < time)*(time < 5.61)
time1 = time[mask1]
volts1 = volts[mask1]

# limit the data for double quantum case
mask2 = (4.89 < time)*(time < 5.20)
time2 = time[mask2]
volts2 = volts[mask2]


# subtract the background
def bg_subtract(x, y):
    m = (y[-1] - y[0])/(x[-1] - x[0])
    return y - (m*(x - x[0]) + y[0])

volts1 = bg_subtract(time1, volts1)
volts2 = bg_subtract(time2, volts2)

# flip over x-axis
volts1 = -1 * volts1
volts2 = -1 * volts2


# Fitting the data
# Lorentzian fitting function
def lorentz(x, *p):
    I, gamma, x0 = p
    return I * gamma**2 / ((x - x0)**2 + gamma**2)

# initial parameter guesses
# [height, HWHM, shift]
p1 = np.array([0.28, .09, 5.4], dtype=np.double)    # single quantum
p2 = np.array([.905, .06, 5.044], dtype=np.double)  # double quantum


def fit(p, x, y):
    return curve_fit(lorentz, x, y, p0 = p)

# Get the fitting parameters for the best lorentzian
solp1, ier1 = fit(p1, time1, volts1)
solp2, ier2 = fit(p2, time2, volts2)


# error stuff
# coefficient of determination
def calc_r2(y, f):
    avg_y = y.mean()
    sstot = ((y - avg_y)**2).sum()
    ssres = ((y - f)**2).sum()
    return 1 - ssres/sstot

# calculate the errors
r2_1 = calc_r2(volts1, lorentz(time1, *solp1))
r2_2 = calc_r2(volts2, lorentz(time2, *solp2))


# plotting
def set_lim(x, y):
    plt.xlim([x[0] - (x[-1] - x[0])*.1, x[-1] + (x[-1] - x[0])*.1])
    plt.ylim([y.min() - (y.max() - y.min())*.1, y.max() + (y.max() - y.min())*.1])

plt.subplot(1, 2, 1)
# plot data
plt.scatter(time1, volts1, marker='+')
# plot lorentzian fit
plt.plot(time1, lorentz(time1, *solp1))
plt.xticks(rotation=17)
set_lim(time1, volts1)

plt.xlabel(csv.header['Horizontal Units'] + ' (arbitrary)')
plt.ylabel(csv.header['Vertical Units'] + ' (arbitrary)')
plt.title('Single Quantum Transition')
amp, gamma, x0 = solp1[0], solp1[1], solp1[2]
equation = "$I = %.3g $\n$ \gamma = %.3g $\n$ x_0 = %.3g $\n$ r^2 = %.3g$" % (amp, gamma, x0, r2_1)
plt.annotate(equation, xy=(5.2, 0.23), fontsize=13)

plt.subplot(1, 2, 2)
# plot data
plt.scatter(time2, volts2, marker='+')
# plot lorentzian fit
plt.plot(time2, lorentz(time2, *solp2))
plt.xticks(rotation=17)
set_lim(time2, volts2)

plt.xlabel(csv.header['Horizontal Units'] + ' (arbitrary)')
plt.title('Double Quantum Transition')
amp, gamma, x0 = solp2[0], solp2[1], solp2[2]
equation = "$I = %.3g $\n$ \gamma = %.3g $\n$ x_0 = %.3g $\n$ r^2 = %.3g$" % (amp, gamma, x0, r2_2)
plt.annotate(equation, xy=(4.9, .7), fontsize=13)

plt.suptitle('Lorentzian Fits of the Data')

plt.savefig('../lorentzian-fit.png')
plt.savefig('../lorentzian-fit.eps')
plt.show()