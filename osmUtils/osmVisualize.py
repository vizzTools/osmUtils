from .utils_map import generate_folium_map, get_html_iframe
from .settings import DEFAULT_BOUNDS, DEFAULT_ZOOM_START, DEFAULT_BASEMAP, DEFAULT_COLOR


class OsmVisualize:
    """
    Visualize geopandas.GeoDataFrame with folium.
    
    Parameters
    ----------
    gdf: geopandas.GeoDataFrame
        GeoDataFrame to be visualized with folium
    bounds: tuple or list
         Latitude and Longitude of Marker (Northing, Easting). If None, it will be set to [45.5, -122.3]
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
    def __init__(self, gdf, bounds=None, zoom_start=None, basemap=None, color=None):

        self.bounds = bounds or DEFAULT_BOUNDS
        self.gdf = gdf
        #todo: add var as kwargs
        self.zoom_start = zoom_start or DEFAULT_ZOOM_START
        self.basemap = basemap or DEFAULT_BASEMAP
        self.color = color or DEFAULT_COLOR

        self.foilum_map = self.get_map()

        #methods
    def _repr_html_(self):
        return get_html_iframe(self.foilum_map)

    def get_map(self):
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
        folium_map = generate_folium_map(bounds=self.bounds, gdf= self.gdf, zoom_start = self.zoom_start, basemap = self.basemap, color=self.color)
        return folium_map

