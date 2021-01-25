from .utils_osm import generate_filter, retrieve_osm, generate_osm_gdf, _to_file
from .utils_map import html_box
from .settings import DEFAULT_TIMEOUT, DEFAULT_OVERPASS_ENDPOINT, DEFAULT_PATH, DEFAULT_DRIVER


class OsmDownload:
    """
    Download OSM ways and nodes within a given geometry from the Overpass API.
    
    Parameters
    ----------
    geometry: shapely.geometry.Polygon or shapely.geometry.MultiPolygon
        geographic boundaries to fetch geometries within
    osm_type: string
        type of filter to retieve if custom_filter is None (e.g 'all_roads', 'river', 'water_features', 'coastline', 'forest', 'buildings', 'parks', 'none')
    custom_filter: list of strings
        a custom filter to be used instead of the already defined in the osm_type
        
    Returns
    -------
    osmData: geopandas.GeoDataFrame
        response retrieved from overpass api in a geopandas.GeoDataFrame
    
    """
    def __init__(self, geometry,  osm_type='none', custom_filter=None):

        self.geometry = geometry

        self.osm_type = None
        if custom_filter is None:
            self.osm_type = osm_type
            self.filter = self.get_filter()
        else:
            self.filter = custom_filter
        self.osm_json = self.get_osm_json()
        self.osm_gdf = self.get_osm_gdf()

        #methods
    def _repr_html_(self):
        return html_box(item=self)

    def get_filter(self):
        """
        Create a filter to retrieve osm data
    
        Parameters
        ----------
        osm_type: string
            {'all_roads', 'river', 'none'}
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
        timeout: int
            the timeout interval for the HTTP request. Set to 180 by default.
        overpass_endpoint: string
            API endpoint to use for the overpass queries. Default set to 'http://overpass-api.de/api'
            
        Returns
        -------
        osmData: geojson
                response retrieved from overpass API
                """
        osm_json = retrieve_osm(geometry=self.geometry, osm_filter=self.filter, timeout=DEFAULT_TIMEOUT, overpass_endpoint=DEFAULT_OVERPASS_ENDPOINT, metadata=False)
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

    def save_gdf_to_file(self, filename=DEFAULT_PATH, driver=DEFAULT_DRIVER):
        """
        Save response geogapdas.GeoDataFrame to local file
        
        Parameters
        ----------
        gdf: geopandas.GeoDataFrame
            response from overpass API in geopandas.GeoDataFrame format
        filename: string
            File path or file handle to write to. Default: osm_data
        driver : string, default: 'ESRI Shapefile'
            The OGR format driver used to write the vector file.
        """         
        if driver == "ESRI Shapefile":
            filename += ".shp"

        elif driver == "GeoJSON":
            filename += ".geojson"
        
        else:
            raise ValueError(f'driver {driver} is not supported. Try with "ESRI Shapefile" or ""GeoJSON"')
            
        if not self.osm_gdf.empty:
            try:
                _to_file(gdf=self.osm_gdf, filename=filename, driver=driver)
                self.filename = filename
            except:
                raise ValueError('Export gdf to file failed!')
            
        else:
            raise ValueError('gdf does not exist. Try to generate gdf before saving.')

    def osm_metadata(self):
         self.osm_json_metadata = retrieve_osm(geometry=self.geometry, osm_filter=self.filter, timeout=DEFAULT_TIMEOUT, overpass_endpoint=DEFAULT_OVERPASS_ENDPOINT, metadata=True)
         
        #note:we could add the osm_Daosm_Data_roadsta_roadsformat output. ATM i'm working with csv

