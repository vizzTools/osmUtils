from .utils_map import generate_folium_map, get_html_iframe, embed_map



class OsmVisualize:
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
    def __init__(self, gdf, **kwargs):
        self.gdf = gdf
        self.kwargs = kwargs
        self.foilum_map = self.get_map()

    # methods
    def _repr_html_(self):
        return get_html_iframe(self.foilum_map)

    def get_map(self, path='index.html'):
        """
        Visualize geopandas.GeoDataFrame with folium.
    
        Parameters
        ----------
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
        m = generate_folium_map(gdf= self.gdf, kwargs=self.kwargs)
        return embed_map(m, path)

