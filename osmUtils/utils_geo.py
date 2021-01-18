
"""General utility functions."""
import geopandas as gpd
import pandas as pd
import mercantile as mt
import folium
from shapely.geometry import shape, MultiPolygon, Polygon, box
from .settings import DEFAULT_CRS, DEFAULT_TILES, DEFAULT_BASEMAP, DEFAULT_ZOOM_START

def generate_tiles(crs, zoom):
        """
        Generate tiles for the manifest.
        """

        #generate tiles
        tiles = []
        
        #calculate bbox for input geometry if geom is none:

        for tile in mt.tiles(*DEFAULT_TILES, zoom, truncate=False):

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
            gdf = set_crs(gdf, crs)

        elif gdf.crs != crs:
            gdf = reproject_gdf(gdf,crs)
        return gdf

def geometry_to_gdf(geometry, crs):
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
            raise ValueError('The geometry is invalid')
        #check that the geometry is a polygon or multipolygon
        if not isinstance(geometry, (Polygon, MultiPolygon)):
            raise ValueError('The geometry must be a shapely.geometry.Polygon or shapely.geometry.MultiPolygon')
    
        #create gdf from the incomming geometry

        gdf = gpd.GeoDataFrame(geometry)
        gdf = gdf.set_geometry(0)
        gdf = gdf.rename(columns={0:'geometry'})

        if gdf.crs is None:
            gdf = set_crs(gdf, crs)

        elif gdf.crs != crs:
            gdf = reproject_gdf(gdf,crs)

        return gdf

def generate_manifest(geometry, tiles, geom_tiles):
    
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

    geom_tiles_gdf = gpd.sjoin(tiles, geometry, how='left', op='intersects',  lsuffix='tiles', rsuffix='geom')

    ## Keep only intersecting tile geoms
    manifest = geom_tiles_gdf[pd.notna(geom_tiles_gdf.geometry_geom)]
    manifest['exclude'], manifest['exported'], manifest['uploaded'] = [0, 0, 0]

    if geom_tiles:
        manifest = manifest.drop_duplicates(subset=['geometry_tiles'])
        manifest = manifest.drop(columns=['geometry_geom', 'index_geom']).rename(columns={'tile_id':'id'})
        manifest = manifest.rename(columns={'geometry_tiles':'geometry'})
        manifest = manifest.set_geometry('geometry')
    else:
        manifest = manifest.drop_duplicates(subset=['geometry_geom'])
        manifest = manifest.drop(columns=['geometry_tiles', 'tile_id']).rename(columns={'index_geom':'id'})
        manifest = manifest.rename(columns={'geometry_geom':'geometry'})
        manifest = manifest.set_geometry('geometry')

    return manifest

def set_crs(gdf, crs):
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
    
def reproject_gdf(gdf,to_crs):
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

## move to utils_graph
def generate_folium_choropleth_map(gdf):
    """
    Visualize geopandas.GeoDataFrame with folium.
    
    Parameters
    ----------
    gdf: geopandas.GeoDataFrame
        GeoDataFrame to be visualized with folium
    Returns
    -------
    folium_map : folium.folium.Map
    """
    bounds = list(gdf.bounds.iloc[0])
    geom = box(bounds[0], bounds[1], bounds[2], bounds[3])

    location = [geom.centroid.y, geom.centroid.x]
    folium_map = folium.Map(location,
                  zoom_start=DEFAULT_ZOOM_START,
                  tiles=DEFAULT_BASEMAP)
    folium.Choropleth(geo_data=gdf).add_to(folium_map)
    folium.LayerControl().add_to(folium_map)
    return folium_map

def get_html_iframe(folium_map):
    """
    Generate html iframe of the folium map
    """
    return folium_map._repr_html_()