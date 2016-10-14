import scipy, numpy, pylab
from numpy import *
from pylab import *
from scipy import *
from scipy.optimize import leastsq


# generate some data
# change the parameters as you see fit
gaussian = lambda x: 3*exp(-(10-x)**2/10.) + 1*exp(-(30-x)**2/10.)
y_power = gaussian(arange(100))
x_pos = arange(100)

# 1d Gaussian func
gauss_fit = lambda p, x: p[0]*(1/sqrt(2*pi*(p[2]**2)))*exp(-(x-p[1])**2/(2*p[2]**2))+p[3]*(1/sqrt(2*pi*(p[5]**2)))*exp(-(x-p[4])**2/(2*p[5]**2))

# 1d Gaussian fit
e_gauss_fit = lambda p, x, y: (gauss_fit(p, x) - y)

# inital guesses for Gaussian Fit. just do it around the peaks
v0 = [1, 10, 1, 1, 30, 1]

# Gauss Fit
out = leastsq(e_gauss_fit, v0[:], args=(x_pos, y_power), maxfev=100000, full_output=1)
# fit parameters out
v = out[0]
# covariance matrix output
covar = out[1]
xxx = arange(min(x_pos), max(x_pos), x_pos[1]-x_pos[0])
# this will only work if the units are pixel and not wavelength
ccc = gauss_fit(v, xxx)

# make a plot
fig = figure(figsize=(9, 9))
ax1 = fig.add_subplot(111)
# spectrum
ax1.plot(x_pos, y_power, 'gs')
# fitted spectrum
ax1.plot(xxx, ccc, 'b-')
# max position in data
ax1.axvline(x=xxx[where(ccc == max(ccc))[0]][0], color='r')
setp(gca(), ylabel='power', xlabel='pixel position')
# pylab.savefig('plotfitting.png')

print('=== xpos: %d, xxx: %d===') %(len(x_pos), len(xxx))
pylab.show()

print 'p[0], a1: ', v[0]
print 'p[1], mu1: ', v[1]
print 'p[2], sigma1: ', v[2]
print 'p[3], a2: ', v[0]
print 'p[4], mu2: ', v[1]
print 'p[5], sigma2: ', v[2]