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
    def __init__(self, geometry,  osm_type='none', infrastructure='way["highway'], custom_filter=None, output_path=None):

        self.geometry = geometry
        self.infrastructure = infrastructure
        self.output_path = output_path or DEFAULT_PATH

        self.osm_type = None
        if custom_filter is None:
            self.osm_type = osm_type
            self.filter = self.get_filter()
        else:
            self.filter = custom_filter
        self.osm_json = self.get_osm_json()
        self.osm_gdf = self.get_osm_gdf()

        #methods

    def get_filter(self):
        """
        Create a filter to retrieve osm data
    
        Parameters
        ----------
        osm_type: string
            {'all_roads'}
        Returns
        -------
        osm_filter: string
            filter to be used in the overpass API query
        """
        osm_filter = generate_filter(osm_type=self.osm_type)
        return osm_filter

    def get_osm_json(self):
        """
        Retrieves OSM data within a given geometry from the Overpass API.
    
         Parameters
        ----------
        geometry: shapely.geometry.Polygon
            geographic boundaries to fetch geometries within
        osm_filter: string
            filter to use for retieve data from the overpass API
        infrastructure: string
            infrastructure type that will be use to build the overpas api query (e.g. 'way["highway"]')
        timeout = 
            the timeout interval for the HTTP request. Set to 180 by default.
        overpass_endpoint: string
            API endpoint to use for the overpass queries. Default set to 'http://overpass-api.de/api'
            
        Returns
        -------
        osmData: geojson
                response retrieved from overpass API
                """
        osm_json = retrieve_osm(geometry=self.geometry, osm_filter=self.filter, infrastructure=self.infrastructure, timeout=DEFAULT_TIMEOUT, overpass_endpoint=DEFAULT_OVERPASS_ENDPOINT)
        #note:we could add the format output. ATM i'm working with csv
        return osm_json
    def get_osm_gdf(self):
        """
        Generate GeoDataFrame from a response retrieved from the overpass API
    
        Parameters
        ----------
        response_json: dict
            dict with the response retrieved from the overpass API
        
        Return
        ------
        osm_gdf: geopandas.GeoDataFrame
            response from overpass API in geopandas.GeoDataFrame format
        
        """
        gdf = generate_osm_gdf(response_json=self.osm_json)
        return gdf
