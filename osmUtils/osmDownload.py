from .utils_osm import generate_filter, retrieve_osm, generate_osm_gdf, _to_file
from .utils_map import html_box
from .settings import DEFAULT_TIMEOUT, DEFAULT_OVERPASS_ENDPOINT

class OsmDownload:
    """
    Download OSM ways and nodes within a given geometry from the Overpass API.
    
    Parameters
    ----------
    geometry: shapely.geometry.Polygon or shapely.geometry.MultiPolygon
        geographic boundaries to fetch geometries within
    osm_type: string
        type of filter to retieve if custom_filter is None (e.g 'all_roads',  'river', 'none')
    custom_filter: string
        a custom filter to be used instead of the already defined in the osm_type
        
    Returns
    -------
    osmData: geopandas.GeoDataFrame
        response retrieved from overpass api in a geopandas.GeoDataFrame
    
    """
    def __init__(self, geometry,  osm_type='none', custom_filter=None, **kwargs):

        self.geometry = geometry
        self.kwargs = kwargs
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
        osm_json = retrieve_osm(geometry=self.geometry, osm_filter=self.filter, timeout=DEFAULT_TIMEOUT, overpass_endpoint=DEFAULT_OVERPASS_ENDPOINT)
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

    def save_gdf_to_file(self, filename='./osm_data', driver="ESRI Shapefile"):
        """
        Save response geogapdas.GeoDataFrame to local file
        
        Parameters
        ----------
        gdf: geopandas.GeoDataFrame
            response from overpass API in geopandas.GeoDataFrame format
        output_path: string
            File path or file handle to write to.
        driver : string, default: 'ESRI Shapefile'
            The OGR format driver used to write the vector file.
        """            
        if driver == "ESRI Shapefile":
            filename += ".shp"

        elif drive == "GeoJSON":
            filename += ".geojson"
        
        else:
            # error message 
            
        if self.gdf:
            try:
                _to_file(gdf=self.gdf, filename=filename, driver=driver)
                self.filename = filename
            except:
                # unsuccessful message
            
        else:
            # error msg


            

# class SavetoFile:
#     """
#         Save response geogapdas.GeoDataFrame to local file
        
#         Parameters
#         ----------
#         gdf: geopandas.GeoDataFrame
#             response from overpass API in geopandas.GeoDataFrame format
#         output_path: string
#             File path or file handle to write to.
#         driver : string, default: 'ESRI Shapefile'
#             The OGR format driver used to write the vector file.
#         """
#     def __init__(self ,gdf, filename='./osm_data.shp', driver="ESRI Shapefile", **kwargs):
#         self.gdf = gdf
#         self.filename = filename
#         self.driver = driver
#         self.kwargs = kwargs
#         self.save = self.save_gdf_to_file()

#     def _repr_html_(self):
#         return html_box(item=self)

#     def save_gdf_to_file(self, filename='./osm_data.shp', driver="ESRI Shapefile"):
#         """
#         Save response geogapdas.GeoDataFrame to local file
        
#         Parameters
#         ----------
#         gdf: geopandas.GeoDataFrame
#             response from overpass API in geopandas.GeoDataFrame format
#         output_path: string
#             File path or file handle to write to.
#         driver : string, default: 'ESRI Shapefile'
#             The OGR format driver used to write the vector file.
#         """
#         _to_file(gdf=self.gdf, filename='./osm_data.shp', driver="ESRI Shapefile")
#         return 'successfully exported!'

