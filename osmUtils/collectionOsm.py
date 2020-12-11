#import requests
import geopandas as gpd
import pandas as pd
from utils import generate_tiles, geometry_to_gdf, generate_manifest
from shapely.geometry import shape, MultiPolygon, Polygon
from settings import DEFAULT_CRS, DEFAULT_COORDS

#from .utils import
#save manifest as wkt to reduce size of manifest

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

    Returns
    ----------
    manifest: geopandas.GeoDataFrame
            manifest geodataframe.

    """
    def __init__(self, geometry=None, zoom=5, crs=None):
        
        self.zoom = zoom
        if crs is None:
            self.crs = DEFAULT_CRS
        else:
            self.crs = crs
        self.tiles = None
        
     
        self.geometry = geometry or Polygon(DEFAULT_COORDS)

        #generate geometry gdf
        self.geometry_gdf = self.get_geom_gdf()
        self.tiles_gdf = self.get_tiles_gdf()
            
        #generate manifest
        self.manifest = self.get_manifest()
        
            
        #else:
        #    #generate manifest for inserted geom
        #    print('todo')
            
    #def __repr__(self):
    #    return 'yes'
    #
        #methods
        
    def get_tiles_gdf(self):
        gdf = generate_tiles(crs=self.crs, zoom=self.zoom)
        return gdf
    
    def get_geom_gdf(self):
        gdf = geometry_to_gdf(geometry=self.geometry, crs=self.crs)
        return gdf
    
    def get_manifest(self):
        manifest = generate_manifest(geometry=self.geometry_gdf, tiles=self.tiles_gdf)
        return manifest
        