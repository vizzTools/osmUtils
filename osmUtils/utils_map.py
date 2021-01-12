"""General utils function to map the retrieved data with folium"""
import folium
import json
from .utils_geo import set_crs
from shapely.geometry import box
from .settings import DEFAULT_ZOOM_START, DEFAULT_BASEMAP, DEFAULT_COLOR


def generate_folium_map(gdf, kwargs):
    """
    Visualize geopandas.GeoDataFrame with folium.
    
    Parameters
    ----------
    gdf: geopandas.GeoDataFrame
        GeoDataFrame to be visualized with folium

    **kwargs
    ---------
    zoom_start: int
        Initial zoom level for the map. If Nne, default level set to 10.
    basemap: string
        Map tileset to use. If None, cartodb dark_matter used.
    color: string
        stroke color. If None, '#f7f5b5' is used.
    Returns
    -------
    folium_map : folium.folium.Map
    """
    gdf_projected = set_crs(gdf=gdf, crs='EPSG:3857')
    gjson = get_gjson(gdf_projected)

    bounds = bounds = list(gdf.bounds.iloc[0])
    geom = box(bounds[0], bounds[1], bounds[2], bounds[3])


    zoom_start=kwargs['zoom_start'] if 'zoom_start' in kwargs else DEFAULT_ZOOM_START
    basemap=kwargs['basemap'] if 'basemap' in kwargs else DEFAULT_BASEMAP
    color=kwargs['color'] if 'color' in kwargs else DEFAULT_COLOR


    folium_map = folium.Map([geom.centroid.y, geom.centroid.x],
                  zoom_start=zoom_start,
                  tiles=basemap)
    style_function = lambda x: {'color': color, 'weight':1, 'opacity':1}
    points = folium.features.GeoJson(gjson, style_function=style_function)
    folium_map.add_child(points)

    return folium_map


def get_gjson(gdf):
    """
    Generates geojson from geopandas.GeoDataFrame
    """
    gjson = gdf.to_json()
    return gjson

def get_html_iframe(folium_map):
    """
    Generate html iframe of the folium map
    """
    return folium_map._repr_html_()
