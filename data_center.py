import ee
import geopandas as gpd
import requests
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt

# Authenticate and initialize Earth Engine API
ee.Authenticate()
ee.Initialize(project='acm-research-f26')
print("Google Earth Engine initialized successfully.")

#load data 
gdf = gpd.read_file('./Data/im3_dataset.gpkg',layer='point') #taking specific coordinates
#convert coordinates to lat/long
gdf = gdf.to_crs(epsg=4326)

data_center = (gdf.dropna(subset=['geometry']).sample(n=1).iloc[0]) #select random data center
lon = data_center.geometry.x
lat = data_center.geometry.y
print('Name: ', data_center['name'])
print('State: ', data_center['state'])
print('Coordinates: ', lon, lat)

#google earth engine point since originally is [lon,lat] and it needs to be [lat,lon]
center = ee.Geometry.Point([lon, lat])

#area around data center
buffer_meters = 1000 #buffer radius in meters
region = center.buffer(buffer_meters).bounds()

#search sentintel-2 imagery
sentinel = (
    ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(region)
    .filterDate('2026-01-01', '2026-09-01')
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)) #less than 10% cloud coverage
)
image_count = sentinel.size().getInfo()
print("Number of images found from Sentinel-2: ", image_count)

#sort newest to oldest
sentinel = sentinel.sort('system:time_start', False)
#select newest image
image = ee.Image(sentinel.first())

date = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd').getInfo()
cloud_coverage = image.get('CLOUDY_PIXEL_PERCENTAGE').getInfo()
print('Selected date: ', date)
print('Cloud coverage: ', cloud_coverage)

#bands
bands = image.select([
    'B2',  # Blue
    'B3',  # Green
    'B4',  # Red
    'B8',  # near infrared
    'B11', # shortwave infrared 
])

#calcuate NDVI for B8 and B4 and NDBI for B11 and B8
ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI') #vegetation signal
ndbi = image.normalizedDifference(['B11', 'B8']).rename('NDBI') #built-up/dry-surface signal

#exract ndvi and ndbi features
environmental_features = ndvi.addBands(ndbi).clip(region)
stats = environmental_features.reduceRegion(
    reducer=ee.Reducer.mean(),
    geometry=region,
    scale=20,
    maxPixels=1e9
)
stats = stats.getInfo()
ndvi_mean = stats.get('NDVI')
ndbi_mean = stats.get('NDBI')
print('\nEnvironmental Features')
print('Data Center: ', data_center['name'])
print('NDVI Mean: ', ndvi_mean)
print('NDBI Mean: ', ndbi_mean)

#create rgb image
rgb = image.select([
    'B4',  # Red
    'B3',  # Green
    'B2'   # Blue   
])

#download rgb preview image
vis_params = {
    'bands': ['B4', 'B3', 'B2'],
    'min': 0,
    'max': 3000,
    'dimensions': 1000,
    'region': region
}
url = rgb.getThumbURL(vis_params)
response = requests.get(url)
response.raise_for_status

satellite_image = Image.open(BytesIO(response.content))

#display image
plt.figure(figsize=(10, 10))
plt.imshow(satellite_image)
plt.title(f'Satellite Image of {data_center["name"]} on {date}\nCloud Coverage: {cloud_coverage}%')
plt.axis('off')
plt.tight_layout()
plt.show()
