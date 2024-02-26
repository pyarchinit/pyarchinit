import numpy as np
import pandas as pd
import geopandas as gpd
import pykrige.ok as ok
from pykrige.ok import OrdinaryKriging
from pykrige.rk import Krige
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.spatial.distance import cdist

# Define the bounds of NEOM (approximate)
min_x, max_x = 34, 36
min_y, max_y = 26, 28

# Generate 100 random points within these bounds
np.random.seed(0)  # For reproducibility
x = np.random.uniform(min_x, max_x, 100)
y = np.random.uniform(min_y, max_y, 100)

# Generate some z values representing data at these points
# For simplicity, we'll just use random numbers here
z = np.random.rand(100)

# Create a GeoDataFrame
data = {'x': x, 'y': y, 'z': z}
points_gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data['x'], data['y']))

# Ordinary Kriging
OK = OrdinaryKriging(x, y, z, variogram_model='spherical', verbose=False, enable_plotting=False)
z_pred, ss = OK.execute('grid', np.linspace(min_x, max_x, 100), np.linspace(min_y, max_y, 100))

# Plotting
fig, ax = plt.subplots()
cax = ax.imshow(z_pred, origin='lower', extent=[min_x, max_x, min_y, max_y])
ax.scatter(x, y, color='white')  # Add original points
fig.colorbar(cax, label='Z value')

# Identify the area with high kriging values
threshold = np.percentile(z_pred, 90)  # Adjust as needed
high_value_area = np.where(z_pred > threshold)

# Calculate the bounding box of this area
bbox_min_x = min_x + (max_x - min_x) * high_value_area[1].min() / 100
bbox_max_x = min_x + (max_x - min_x) * high_value_area[1].max() / 100
bbox_min_y = min_y + (max_y - min_y) * high_value_area[0].min() / 100
bbox_max_y = min_y + (max_y - min_y) * high_value_area[0].max() / 100

# Draw bounding box
bbox = Rectangle((bbox_min_x, bbox_min_y), bbox_max_x-bbox_min_x, bbox_max_y-bbox_min_y, fill=False, edgecolor='red')
ax.add_patch(bbox)

plt.show()

# Fit a model to the semivariogram data and perform cross-validation
param_dict = {"method": ["ordinary", "universal"],
              "variogram_model": ["linear", "power", "gaussian", "spherical"],
              "nlags": [4, 6, 8]}


estimator = GridSearchCV(Krige(), param_dict, verbose=True)
coordinates = np.column_stack((x, y))
estimator.fit(coordinates, z)

# Print the best parameters
print(estimator.best_params_)

# Plot the empirical and fitted semivariogram
if hasattr(estimator, 'best_estimator_'):
    distance_coordinates = np.linspace(0, np.max(cdist(coordinates, coordinates)), 100)
    print(distance_coordinates)
    variogram_model = estimator.best_estimator_.variogram_model
    print(variogram_model)
    #variogram_parameters = estimator.best_estimator_.variogram_parameters
    #print(variogram_parameters)
    #if variogram_parameters is None:
    variogram_parameters = {'model': 'spherical', 'range': 10, 'sill': 1}
    # Get the variogram model function and parameters
    variogram_function = OK.variogram_function
    variogram_parameters = OK.variogram_model_parameters   #variogram_values = variogram_function(distance_coordinates,variogram_parameters = {'model': 'spherical', 'range': 10, 'sill': 1})
    variogram_values = variogram_function(distance_coordinates, None)
    plt.plot(distance_coordinates, variogram_values, 'r-')
    plt.title('Fitted Variogram Model')
    plt.xlabel('Distance')
    plt.ylabel('Semivariance')
    plt.grid(True)
    plt.show()




