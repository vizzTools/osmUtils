from .utils_osm import generate_filter, retrieve_osm, generate_osm_gdf
from .settings import DEFAULT_PATH, DEFAULT_TIMEOUT, DEFAULT_OVERPASS_ENDPOINT

class OsmDownload:
    """
    Download OSM ways and nodes within a given geometry from the Overpass API.
    
    Parameters
    ----------
    geometry: shapely.geometry.Polygon or shapely.geometry.MultiPolygon
        geographic boundaries to fetch geometries within
    osm_type: string
        type of filter to retieve if custom_filter is None (e.g 'all_roads')
    infrastructure: string
        infrastructure type that will be use to build the overpas api query (e.g. 'way["highway"]')
    custom_filter: string
        a custom filter to be used instead of the already defined in the osm_type
        
    Returns
    -------
    osmData: geopandas.GeoDataFrame
        response retrieved from overpass api in a geopandas.GeoDataFrame
    
    """
    def __init__(self, geometry,  osm_type, infrastructure, custom_filter=None, output_path=None):

        self.geometry = geometry
        self.infrastructure = infrastructure
        self.osm_type = None

        self.output_path = output_path
        if output_path is None:
            self.output_path = DEFAULT_PATH

        if custom_filter is None:
            self.osm_type = osm_type
            self.filter = self.get_filter()
        else:
            self.filter = custom_filter
        self.osm_json = self.get_osm_json()
        self.osm_gdf = self.get_osm_gdf()
        

            
    #def __repr__(self):
    #    return 'yes'
    #
        #methods

    def get_filter(self):
        osm_filter = generate_filter(osm_type=self.osm_type)
        return osm_filter

    def get_osm_json(self):
        osm_json = retrieve_osm(geometry=self.geometry, osm_filter=self.filter, infrastructure=self.infrastructure, timeout=DEFAULT_TIMEOUT, overpass_endpoint=DEFAULT_OVERPASS_ENDPOINT)
        #note:we could add the format output. ATM i'm working with csv
        return osm_json
    def get_osm_gdf(self):
        gdf = generate_osm_gdf(response_json=self.osm_json)
        return gdf
