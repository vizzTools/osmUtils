"""Global settings"""

# default CRS to set for input geometries and output tiles
DEFAULT_CRS = "EPSG:4326"
DEFAULT_TILES = [-180, -85, 180, 85]
DEFAULT_COORDS = [(-180,-85), (180, -85), (180, 85), (-180, 85), (-180, -85)]


#default settings for rertrieving osm data from the overpass API
DEFAULT_PATH = './osm_data'