"""General utils function to map the retrieved data with folium"""
import folium
import json
from .utils_geo import set_crs

def generate_folium_map(bounds, gdf, zoom_start, basemap, color):
    """
    Visualize geopandas.GeoDataFrame with folium.
    
    Parameters
    ----------
    bounds: tuple or list
        Latitude and Longitude of Marker (Northing, Easting). If None, it will be set to [45.5, -122.3]
    gdf: geopandas.GeoDataFrame
        GeoDataFrame to be visualized with folium
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
    if len(bounds)>2:
        raise ValueError(f'Two element expected in bounds - Latitude and Longitude of Map (Northing, Easting)')
    folium_map = folium.Map([ bounds[0], bounds[1]],
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
