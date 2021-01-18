"""Global settings"""

# default CRS to set for input geometries and output tiles
DEFAULT_CRS = "EPSG:4326"
DEFAULT_TILES = [-180, -85, 180, 85]
DEFAULT_COORDS = [(-180,-85), (180, -85), (180, 85), (-180, 85), (-180, -85)]


#default settings for rertrieving osm data from the overpass API
DEFAULT_PATH = './osm_data.shp'
DEFAULT_DRIVER = 'ESRI Shapefile'
DEFAULT_TIMEOUT=180
DEFAULT_OVERPASS_ENDPOINT='http://overpass-api.de/api'

#default setting for the folium visualization
DEFAULT_ZOOM_START = 10
DEFAULT_BASEMAP = 'cartodbpositron'
DEFAULT_COLOR = '#8c9191'