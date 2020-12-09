#import requests
import mercantile as mt
import geopandas as gpd
import pandas as pd
from shapely.geometry import shape, MultiPolygon, Polygon

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
    def __init__(self, geometry=None, zoom=5, crs=None, tile_geom=True, **kwargs):
        
        self.zoom = zoom
        if crs is None:
            self.crs = default_crs
        else:
            self.crs = crs
        self.tiles = None
        
        #generate geometry gdf
        self.geometry = self.geometry_to_gdf(geometry=geometry, crs=self.crs)
        
        if tile_geom:
            self.tiles = self.generate_tiles(crs=self.crs)
            
        #generate manifest
        self.manifest = self.generate_manifest(geometry=self.geometry, tiles=self.tiles)
        
            
        #else:
        #    #generate manifest for inserted geom
        #    print('todo')
            
    #def __repr__(self):
    #    return 'yes'
    #
        #methods
        
    def generate_tiles(self, crs):
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
        gdf = gpd.GeoDataFrame(tiles)
        
        #check projection 
        if gdf.crs is None:
            gdf = self.set_crs(gdf, crs)

        elif gdf.crs != self.crs:
            gdf = self.reproject_gdf(gdf,crs)
        return gdf
    
    def geometry_to_gdf(self,geometry, crs):
        """
        Create GeoDataFrame from a (multi)polygon.
        Parameters
        ----------
        geometry : shapely.geometry.Polygon or shapely.geometry.MultiPolygon
            geographic boundaries to fetch geometries within
        Returns
        -------
        gdf : geopandas.GeoDataFrame
        """
        #check that incomming geometry is valid
        if not geometry.is_valid:
            print('The geometry is invalid')
        #check that the geometry is a polygon or multipolygon
        if not isinstance(geometry, (Polygon, MultiPolygon)):
            print('The geometry must be a shapely.geometry.Polygon or shapely.geometry.MultiPolygon')
    
        #create gdf from the incomming geometry

        gdf = gpd.GeoDataFrame(geometry)
        gdf = gdf.set_geometry(0)
        gdf = gdf.rename(columns={0:'geometry'})

        if gdf.crs is None:
            gdf = self.set_crs(gdf, crs)

        elif gdf.crs != self.crs:
            gdf = self.reproject_gdf(gdf,crs)

        return gdf

    def set_crs(self, gdf, crs):
        """
        Set CRS in GeoDataFrame when current projection is not defined.
        Parameters
        ----------
        gdf : geopandas.GeoDataFrame
            the geodataframe to set the projection
        Returns
        -------
        gdf : geopandas.GeoDataFrame
            the geodataframe with the projection defined """
        gdf = gdf.set_crs(crs)
        
        return gdf

    def reproject_gdf(self, gdf,to_crs):
        """Project a GeoDataFrame from its current CRS to another.
        Parameters
        ----------
        gdf : geopandas.GeoDataFrame
            the GeoDataFrame to be projected
        to_crs : string 
            CRS to project the geodataframe
        Returns
        ----------
        gdf_proj : geopandas.GeoDataFrame
            the projected GeoDataFrame"""

        gdf_proj = gdf.to_crs(epsg=to_crs)
        return gdf_proj
    
    def generate_manifest(self, geometry, tiles):
    
        """Generates a gedodataframe manifest to keep track of the osm retrieving process.
            Parameters
            ----------
            geometry : geopandas.GeoDataFrame
                the GeoDataFrame to be projected
            tiles : geopandas.GeoDataFrame 
                tiles geodataframe to be intersected with the incomming geometry.
                if None, it will produce a manifest just for the incomming geometry.
            Returns
            ----------
            manifest : geopandas.GeoDataFrame
                manifest geodataframe"""


        if tiles is None:
            #return manifest for geometry
            geom_tiles = geometry
        else:
            geom_tiles = gpd.sjoin(tiles, geometry, how='left', op='intersects',  lsuffix='tiles', rsuffix='geom')

        ## Keep only intersecting tile geoms
        manifest = geom_tiles[pd.notna(geom_tiles.geometry_geom)]
        #add the tracking information
        manifest['exclude'] = 0
        manifest['exported'] = 0
        manifest['uploaded'] = 0

        return manifest