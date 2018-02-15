from pygments.console import x

from matplotlib import cm
from matplotlib.mlab import griddata
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.axes3d import *
import numpy as np
import scipy as sp
import scipy.interpolate


def tre_d(layer):
	layer.select([])
	layer.setSelectedFeatures([obj.id() for obj in layer])
	mylayer = qgis.utils.iface.activeLayer()
	tre_d(mylayer)	

	from shapely.wkb import loads
	
	x=[]
	y=[]
	z=[]
	for elem in mylayer.selectedFeatures():
		   
		geom= elem.geometry() 
		wkb = geom.asWkb()
				  
		x.append(loads(wkb).x)
		y.append(loads(wkb).y)
		z.append(loads(wkb).z)

		x=[]
		y=[]
		z=[]
	for elem in mylayer.selectedFeatures():
		geom= elem.geometry() 
		x.append(geom.asPoint()[0])
		y.append(geom.asPoint()[1])
		z.append(elem.attributeMap()[15].toFloat()[0])

fig = plt.figure()
ax = Axes3D(fig)
ax.scatter3D(x,y,z,c=z,cmap=plt.cm.jet)
plt.show()
# création d'une grille 2D
xi = np.linspace(min(x), max(x))
yi = np.linspace(min(y), max(y))
X, Y = np.meshgrid(xi, yi)
# interpolation
Z = griddata(x, y, z, xi, yi)
fig = plt.figure()
ax = Axes3D(fig)
ax.plot_surface(X, Y, Z, rstride=1, cstride=1,cmap=cm.jet,linewidth=1, antialiased=True)
plt.show()
# construction de la grille
spline = sp.interpolate.Rbf(x,y,z,function='thin-plate')
xi = np.linspace(min(x), max(x))
yi = np.linspace(min(y), max(y))
X, Y = np.meshgrid(xi, yi)
# interpolation
Z = spline(X,Y)
