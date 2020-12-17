from utils_osm import generate_filter, retrieve_osmData
from settings import DEFAULT_PATH

class OsmDownload:
    """
    Download OSM ways and nodes within a given geometry from the Overpass API.
    
    Parameters
    ----------
    manifest: geopandas.GeoDataFrame
            manifest geodataframe.
    osm_type: string
        type of filter to retieve if custom_filter is None (e.g 'all_roads)
    infrastructure: string
        infrastructure type that will be use to build the overpas api query (e.g. 'way["highway"]')
    custom_filter: string
        a custom filter to be used instead of the already defined in the osm_type
        
    Returns
    -------
    
    """
    def __init__(self, manifest,  osm_type, infrastructure, custom_filter=None, output_path=None):

        self.manifest = manifest
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
        self.osmData = self.get_osmData()
        

            
    #def __repr__(self):
    #    return 'yes'
    #
        #methods

    def get_filter(self):
        osm_filter = generate_filter(osm_type=self.osm_type)
        return osm_filter

    def get_osmData(self):
        osmData_manifest = retrieve_osmData(manifest=self.manifest, infrastructure = self.infrastructure, osm_filter= self.filter, path=self.output_path)
        #note:we could add the format output. ATM i'm working with csv
        return osmData_manifest