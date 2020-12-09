#import requests
#import geopandas as gpd

import mercantile as mt
from shapely.geometry import shape
#from .utils import

class CollectionOsm:
    """
    This is the main CollectionOsm class. This collection class will produce a tile manifest at an especific zoom level
     to keep track of the OSM retrieving process.

    Parameters
    ----------
    geometry: shapely.geometry.Polygon or shapely.geometry.MultiPolygon
        geographic boundaries to fetch geometries within
    zoom: int
        zoom levels to generate the tiles
    crs: str
        the starting CRS of the passed-in geometry. if None, it will be set to "EPSG:4326"
    manifest_geom: str
        geometry to be mantained in the manifest. 'tile' will mantain the tile geoms in the manifest
        while 'geom' will mantain the original geom.

    """
    def __init__(self, geometry=None, zoom=5, crs='EPSG:4326', tile_geom=True, **kwargs):
        self.geometry = geometry
        self.zoom = zoom
        self.crs = crs
        if tile_geom:
            self.tiles = self.generate_tiles()
        #else:
        #    #generate manifest for inserted geom
        #    print('todo')
            
    #def __repr__(self):
    #    return 'yes'
    #
        #methods
        
    def generate_tiles(self):
        """
        Generate tiles for the manifest.
        """

        #generate tiles
        tiles = []
        for tile in mt.tiles(-180, -85, 180, 85, self.zoom, truncate=False):

            tile_id = f"{tile.z}_{tile.x}_{tile.y}"

            geom = mt.feature(tile)['geometry']
            polygon = shape(geom)

            tiles.append({
                'tile_id': tile_id,
                'geometry': polygon
            })

        # generate geodataframe with tiles
        tiles_df = gpd.GeoDataFrame(tiles)
        
        #check projection of tiles and geometry for the spatial join
        

        return tiles_df