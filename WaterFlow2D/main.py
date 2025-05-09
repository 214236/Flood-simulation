import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import matplotlib.patches as patches

from function import PlotTerrain2D

# Parameters
sizeX = 20
sizeY = 10
sourceY = 5
SourcePower = 1

x = np.linspace(0, sizeX, 100)
y = np.linspace(0, sizeY, 100)
X, Y = np.meshgrid(x, y)
water = np.zeros(X.shape)
water[0, sourceY] = SourcePower

fig, axis = PlotTerrain2D(sizeX, sizeY, sourceY)
axis.plot(x, water[0, :], color='blue', linewidth=2)

