#import requests
import geopandas as gpd
import pandas as pd
from .utils_geo import generate_tiles, geometry_to_gdf, generate_manifest
from shapely.geometry import shape, MultiPolygon, Polygon
from .settings import DEFAULT_CRS, DEFAULT_COORDS

#save manifest as wkt to reduce size of manifest

class CollectionOsm:
    """
    This is the main CollectionOsm class. This collection class will produce a tile manifest at an especific zoom level
     to keep track of the OSM retrieving process.

    Parameters
    ----------
    geometry: shapely.geometry.Polygon or shapely.geometry.MultiPolygon
        geographic boundaries to fetch geometries within
        if None, default coordinates will be set to [(-180,-85), (180, -85), (180, 85), (-180, 85), (-180, -85)]
    zoom: int
        zoom levels to generate the tiles
    crs: str
        the starting CRS of the passed-in geometry. if None, it will be set to "EPSG:4326"
    geom_tiles: bool
        if True the manifest will be generated for the tile geometry. False will provide the
        manifest for the input geometry.
    Returns
    ----------
    manifest: geopandas.GeoDataFrame
            manifest geodataframe.

    """
    def __init__(self, geometry=None, zoom=5, crs=None, geom_tiles=True):
        
        self.zoom = zoom
        self.crs = crs or DEFAULT_CRS 
        self.tiles = None
        self.geometry = geometry or Polygon(DEFAULT_COORDS)
        self.geom_tiles = geom_tiles

        #generate geometry gdf
        self.geometry_gdf = self.get_geom_gdf()
        self.tiles_gdf = self.get_tiles_gdf()
            
        #generate manifest
        self.manifest = self.get_manifest()

        #methods
        
    def get_tiles_gdf(self):
        """
        Generate tiles for a determined zoom level.

        Parameters
        ---------
        crs: string
            coordinate system for the output tiles
        zoom: int
            zoom level for the generation of tiles

        Returns
        --------
        gdf: geopandas.GeoDataFrame
        """
        gdf = generate_tiles(crs=self.crs, zoom=self.zoom)
        return gdf
    
    def get_geom_gdf(self):
        """
        Parse input geometry to geopandas.GeoDataFrame

        Parameters
        -----------
        geometry: shapely.geometry.Polygon or shapely.geometry.Multipolygon
            geometry to parse into a geopandas.GeoDataFrame
        crs: string
            coordinate system for the output file

        Returns
        -------
        gdf: geopandas.GeoDataFrame
        
        """
        gdf = geometry_to_gdf(geometry=self.geometry, crs=self.crs)
        return gdf
    
    def get_manifest(self):
        """
        Generates geopandas.GeoDataFrame for tracking the osm retrieving process

        Parameters
        ----------
        geometry: geopandas.GeoDataFrame
            geometry parsed in a geopandas.GeoDataFrame
        tiles: geopandas.GeoDataFrame
            tiles parsed in a geopandas.GeoDataFrame
        geom_tiles: bool
            if True the manifest will be generated for the tile geometry. False will provide the
            manifest for the input geometry.
            
        Returns
        --------
        manifest: geopandas.GeoDataFrame
            """
        manifest = generate_manifest(geometry=self.geometry_gdf, tiles=self.tiles_gdf, geom_tiles=self.geom_tiles)
        return manifest
        