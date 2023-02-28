import numpy as np
from itertools import product
import yaml 
import matplotlib.pyplot as plt

XLIM = [-16.235, 5.435]
YLIM = [-3.6625, 3.6625]
GRID_NUM = 500
# find the ratio of the limits to each other
inc = np.sqrt((XLIM[1] - XLIM[0]) * (YLIM[1] - YLIM[0])/GRID_NUM)
# create an array of the grid points starting from XLIM[0] increasing by inc not including XLIM[0]
x = np.arange(XLIM[0], XLIM[1], inc)
x = x + np.array([(XLIM[1]-x[-1])*0.5])
y = np.arange(YLIM[0], YLIM[1], inc)
y = y + np.array([(YLIM[1]-y[-1])*0.5])

# create combinations of the grid points
grid = np.array(list(product(x, y)))

# plot a rectangular map with the limits
plt.plot([XLIM[0], XLIM[0], XLIM[1], XLIM[1], XLIM[0]], [YLIM[0], YLIM[1], YLIM[1], YLIM[0], YLIM[0]], 'k')
plt.gca().set_aspect('equal', adjustable='box')
# plot the grid points
plt.plot(grid[:,0], grid[:,1], 'r.')

plt.show()

