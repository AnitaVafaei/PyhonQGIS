import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from qgis.core import QgsVectorLayer, QgsProject, QgsApplication, QgsProcessingFeedback, QgsProcessingContext
from qgis.analysis import QgsNativeAlgorithms
import processing
import matplotlib.pyplot as plt

# Start QGIS application
QgsApplication.setPrefixPath("/path/to/qgis/installation", True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Synthetic grid of points
grid_size = 20
urban_area_bounds = (-122.45, 37.75, -122.40, 37.80)
x = np.linspace(urban_area_bounds[0], urban_area_bounds[2], grid_size)
y = np.linspace(urban_area_bounds[1], urban_area_bounds[3], grid_size)
points = [Point(lon, lat) for lat in y for lon in x]

# Simulate temperature data
np.random.seed(42)
temperatures = np.random.uniform(20, 30, len(points))

# Create a DataFrame
temperature_data = {'Latitude': [point.y for point in points],
                    'Longitude': [point.x for point in points],
                    'Temperature': temperatures}

df = pd.DataFrame(temperature_data)

# Create a GeoDataFrame
geometry = [Point(lon, lat) for lon, lat in zip(df['Longitude'], df['Latitude'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')

# Save the GeoDataFrame to a shapefile
gdf.to_file('/path/to/synthetic_temperature_data.shp')

# Load synthetic temperature data as a vector layer
layer_path = '/path/to/synthetic_temperature_data.shp'
layer_name = 'Synthetic Temperature Data'
layer = QgsVectorLayer(layer_path, layer_name, 'ogr')
QgsProject.instance().addMapLayer(layer)

# Interpolation using QGIS Processing Toolbox
processing.run("qgis:interpolatepoints", {
    'INPUT': layer,
    'FIELD': 'Temperature',
    'OUTPUT': '/path/to/interpolated_temperature_surface.tif',
    'METHOD': 0,  # Inverse Distance Weighting
    'RADIUS': 500  # Search radius
})

# Spatial analysis: Identify hotspots using zonal statistics
processing.run("qgis:zonalstatistics", {
    'INPUT_RASTER': '/path/to/interpolated_temperature_surface.tif',
    'RASTER_BAND': 1,
    'INPUT_VECTOR': layer,
    'COLUMN_PREFIX': 'temperature_stats',
    'STATISTICS': [2]  # Mean value
})

# Map Visualization
canvas = QgsMapCanvas()
canvas.setExtent(layer.extent())
canvas.setLayers([layer, '/path/to/interpolated_temperature_surface.tif'])
canvas.zoomToFullExtent()
canvas.show()

# Print synthetic temperature data
print("Synthetic Temperature Data:")
print(df.head())

# Plot the synthetic temperature data
plt.scatter(df['Longitude'], df['Latitude'], c=df['Temperature'], cmap='viridis', marker='o')
plt.colorbar(label='Temperature (°C)')
plt.title('Synthetic Temperature Data')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.show()

# Stop QGIS application
qgs.exitQgis()
