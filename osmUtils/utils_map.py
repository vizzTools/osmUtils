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
    gjson_str = get_gjson(gdf_projected)
    gjson = json.loads(gjson_str)

    zoom_start=kwargs.get('zoom_start',  DEFAULT_ZOOM_START)
    basemap=kwargs.get('basemap', DEFAULT_BASEMAP)
    color=kwargs.get('color', DEFAULT_COLOR)
    max_features = kwargs.get('max_features',None)
    max_index = (max_features and max_features <= len(gjson['features'])) or len(gjson['features'])
    features = gjson['features'][:max_index]

    bounds = list(gdf.bounds.iloc[0])
    geom = box(bounds[0], bounds[1], bounds[2], bounds[3])

    m = folium.Map(
                location = [geom.centroid.y, geom.centroid.x],
                zoom_start=zoom_start,
                tiles=basemap
                )


    style_function = lambda x: {'color': color, 'weight':1, 'opacity':1}
    folium.GeoJson({
        "type":"FeatureCollection",
        "features": features
    }, style_function=style_function).add_to(m)

    return m


def get_gjson(gdf):
    """
    Generates geojson from geopandas.GeoDataFrame
    """
    gjson = gdf.to_json()
    return gjson

def embed_map(m, path):
    """Resolves Folium rendering in chrome+Jupyter issue by saving to local path"""
    from IPython.display import IFrame
    if '.html' not in path: path += '.html'
    
    m.save(path)
    return IFrame(path, width='100%', height='750px')

def get_html_iframe(folium_map):
    """
    Generate html iframe of the folium map
    """
    return folium_map._repr_html_()
