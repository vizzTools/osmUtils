""" General util fucntion for retrieving osm from the Overpass API"""
import os
import requests
import json
import time
import geopandas as gpd
import pandas as pd
import datetime as dt
from shapely.geometry import LineString,  box, Polygon, MultiPolygon
from .settings import DEFAULT_PATH, DEFAULT_DRIVER
#from shapely.geometry import mapping, shape, box,

def generate_filter(osm_type):
    """
    Create a filter to retrieve osm data
    
    Parameters
    ----------
    osm_type: string
        {'all_roads', 'river', 'water_features', 'coastline', 'forest', 'buildings', 'parks', 'none'}, 
    Returns
    -------
    osm_filter: string
        filter to be used in the overpass API query
    """
    filters = dict()
    filters['all_roads'] = [(
        'way["highway"][!"tunnel"]["area"!="yes"]["highway"!~"cycleway|footway|path|pedestrian|steps|track|corridor|' \
        'elevator|escalator|proposed|bridleway|abandoned|platform"]'
    )]
    filters['river'] = [('way["waterway"="river"]')]
    filters['water_features'] = ['way["natural"="water"]',  'relation["natural"="water"]']
    filters['coastline'] = ['way["natural"="coastline"]']
    filters['forest'] = ['way["landuse"="forest"]', 'relation["landuse"="forest"]']
    filters['buildings'] = ['way["building"]', 'relation["building"]']
    filters['parks'] = ['node["leisure"="park"]', 'way["leisure"="park"]', 'relation["leisure"="park"]']
    filters['none'] = ['']

    #todo: add more filters
    if osm_type in filters:
        osm_filter = filters[osm_type]
    else:
        raise ValueError(f'Unrecognised filter type: {osm_type}')
    return osm_filter

def get_pause_duration(
    default_duration=5, 
    overpass_endpoint='http://overpass-api.de/api'
):
    """
    Check the Overpass API status endpoint to determine how long to wait until
    next slot is available.
    """
    try:
        url = overpass_endpoint.rstrip('/') + '/status'
        response = requests.get(url)#, headers=_get_http_headers())
        status = response.text.split('\n')[3]
        status_first_token = status.split(' ')[0]
    # if we cannot reach the status endpoint or parse its output, log an
    # error and return default duration
    except:
        print(f'Unable to query {url}')
        return default_duration
    try:
        # if first token is numeric, it's how many slots you have available - no
        # wait required
        available_slots = int(status_first_token)
        pause_duration = 0
    except:
        # if first token is 'Slot', it tells you when your slot will be free
        if status_first_token == 'Slot':
            utc_time_str = status.split(' ')[3]
            utc_time = dt.datetime.strptime(utc_time_str,'%Y-%m-%dT%H:%M:%SZ,')
            pause_duration = int((utc_time - dt.datetime.utcnow()).total_seconds() + 1)
            pause_duration = max(pause_duration, 1)

        # if first token is 'Currently', it is currently running a query
        elif status_first_token == 'Currently':
            time.sleep(default_duration)
            pause_duration = get_pause_duration()
        else:
            print(f'Unrecognized server status: "{status}"')
            return default_duration

def overpass_request(
    query_string, 
    pause_duration=1, 
    timeout=180,
    overpass_endpoint='http://overpass-api.de/api'
):
    """
    Send a request to the Overpass API via HTTP POST and return the JSON
    response.
    Parameters
    ----------
    query_string : str
        Overpass API query string
    pause_duration : int
        how long to pause in seconds before requests, if None, will query API
        status endpoint to find when next slot is available
    timeout : int
        the timeout interval for the requests library
    Returns
    -------
    response_json: dict

    """
    url = overpass_endpoint.rstrip('/') + '/interpreter'

    # Check server status first and wait if overloaded
    if pause_duration is None:
        pause_duration = get_pause_duration()
    print(f'Pausing {pause_duration} seconds before making API POST request')
    time.sleep(pause_duration)

    # Post request
    data = {'data': query_string}
    print(f'Posting to {url} with timeout={timeout}, "{data}"')
    response = requests.post(url, data={'data': query_string}, timeout=timeout)

    try:
        response_json = response.json()
        if 'remark' in response_json:
            print(f'Server remark: "{response_json["remark"]}"')

    except:
        if response.status_code in [429, 504]:
            error_pause_duration = get_pause_duration()
            print(f'Server returned status {response.status_code} and no JSON data: retrying in {error_pause_duration} seconds.')
            time.sleep(error_pause_duration)
            response_json = overpass_request(query_string, pause_duration=pause_duration, timeout=timeout)
        # else, this was an unhandled status_code, throw an exception
        else:
            print(f'Server returned status code {response.status_code} and no JSON data.')
            print(f'Server returned no JSON data\n{response} {response.reason}\n{response.text}')
            

    return response_json

def get_coordinate_string(geometry):
    """
    Extract exterior coordinates from polygon(s) to pass to OSM in a query by
    polygon. Ignore the interior ("holes") coordinates. Round to 6 places.

    Parameters
    -----------
    geometry: shapely.geometry.Polygon or shapely.geometry.MultiPolygon
        geographic boundaries to fetch geometries within
    Return
    ------
    polygon_coord_str: str
        polygon coordinates in string format which is needed for the overpass API query

    """

    # extract the exterior coordinates of the geometry to pass to the API later
    polygons_coords = []
    if isinstance(geometry, Polygon):
        x, y = geometry.exterior.xy
        polygons_coords.append(list(zip(x, y)))
    elif isinstance(geometry, MultiPolygon):
        for polygon in geometry:
            x, y = polygon.exterior.xy
            polygons_coords.append(list(zip(x, y)))
    else:
        print('Geometry must be a shapely Polygon or MultiPolygon')

    # convert the exterior coordinates of the polygon(s) to the string format
    # the API expects
    polygon_coord_strs = []
    for coords in polygons_coords:
        s = ''
        separator = ' '
        for coord in list(coords):
            # round floating point lats and longs to 6 decimal places (ie, ~100 mm),
            # so we can hash and cache strings consistently
            s = f'{s}{separator}{coord[1]:.6f}{separator}{coord[0]:.6f}'
        polygon_coord_strs.append(s.strip(separator))

    return polygon_coord_strs

def OSM_response_to_lines(response_json):
    """
    Parse Overpass API json response to extract ways as linestrings
    Parameters
    ----------
    response_json: dict
        response retrieved from the overpass API
    Returns
    -------
    geoms: shapely.geometry.LineString
        line strings from retrieved nodes

    """
    if not 'elements' in response_json:
        print("No elements in response!")
        return []
    
    # Iterate through elements in Overpass API response
    nodes_xy = {}
    ways = {}
    for el in response_json['elements']:
        if el['type'] == 'node':
            # Save nodes as points
            nodes_xy[el['id']] = (el['lon'], el['lat'])
        if el['type'] == 'way':
            # Save ways as lists of their node IDs
            ways[el['id']] = el['nodes']

    # Create line strings from lists of nodes
    
    ########
    # TODO: Add simplification logic here
    #  e.g. remove duplicate points, etc.
    # TODO: Add cleaning for polygons
    try:
        geoms = []
        for way_nodes in ways.values():
            try:
                line_ = LineString([nodes_xy[n] for n in way_nodes])
                geoms.append(line_)
            except:
                print(f'{way_nodes} failed!')
    except:
        geoms = None
    return geoms

def cut_geom(polygon, N):
    """
    Cut geometry in n*2n parts
    Parameters
    ----------
    polygon: shapely.geometry.Polygon
        polygon to be split in n*n parts
    n: int
        number of parts to split the input geometry
    Retunrs
    -------
    intersected_feats: shapely.geometry.MultiPolygon
        """
    # Get bounds of grid
    lon_end,lat_start,lon_start,lat_end = polygon.bounds
    print(lon_end,lat_start,lon_start,lat_end)

    num_cells = N * N
    lon_edge = (lon_end - lon_start) / (num_cells ** 0.5)
    lat_edge = (lat_end - lat_start) / (num_cells ** 0.5)

    # Generate grid over feature
    polys = []
    lon = lon_start
    for i in range(0, N):
        x1 = lon
        x2 = lon + lon_edge
        lon += lon_edge
        lat = lat_start
        for j in range(0, N):
            y1 = lat
            y2 = lat + lat_edge
            lat += lat_edge
            polygon_temp = box(x1, y1, x2, y2)
            polys.append(polygon_temp)

    # Intersects grid against feature
    intersected_feats = []
    for p in polys:
        is_intersect = p.intersects(polygon)
        if is_intersect:
            intersection = p.intersection(polygon)
            intersected_feats.append(intersection)
        
    return intersected_feats

def get_cut_dfs(polygon_list, filters):
    """
    Iterates over a list of polygons and retrieves the OSM geometries that intersect with them.
    Combines into a single GeoDataFrame.

    Parameters
    ----------
    polygon_list: List of Shapely Polygons
    Returns GeoDataFrame
    --------

    """
    list_dfs = []
    for geom in polygon_list:
        response_json = download_OSM(geom,filters)
        try:
            if len(response_json) and response_json['elements']:
                print('Respose_recieved...')
                    ## Create graph and convert of GeoDataFrame
                try:
                    geoms = OSM_response_to_lines(response_json)
                    #df = get_Lines_gdf(G)
                    if geoms:
                        df = gpd.GeoDataFrame(geometry=geoms)
                        list_dfs.append(df)
                except:
                    print('Fail generation of graph... No response')
        except:
            if (response_json==None) or ('remark' in response_json):
                print('response retrieved...')
                polygon_list = cut_geom(geom, 2)
                sublist_dfs = get_cut_dfs(polygon_list, filters)
                list_dfs.append(sublist_dfs)
            else:
                print('There is no data for this tile')
    try:         
       gdf = pd.concat(list_dfs)
    except:
       print('no objects to concatenate')
       gdf = None
    
    return gdf


def download_OSM(
    geometry,
    filters='',
    timeout=180,
    overpass_endpoint='http://overpass-api.de/api'
):
    """
    Request to Overpass API
    Parameters
    ----------
    geometry: shapely.geometry.Polygon or shapely.geometry.MultiPolygon
        geographic boundaries to fetch geometries within
    infrastructure: string
        infrastructure type that will be use to build the overpas api query (e.g. 'way["highway"]')
    filters: string
        filter to be used in the query for retrieving osm data from the overpass API
    timeout: int
        the timeout interval for the requests library
    overpass_enpoint: string
    Retunrs
    -------
    response_json: dict
        response retrived from the overpass API
    """
    if not geometry.is_valid:
        print('Shape does not have a valid geometry')
    if not isinstance(geometry, (Polygon, MultiPolygon)):
        print('Geometry must be a shapely Polygon or MultiPolygon.')
        
    geometry_coord_str = get_coordinate_string(geometry)
    print('Geometry coordines converted into string')
    overpass_settings = f'[out:json][timeout:{timeout}]'
    
    try:
        response_json = []
        for filter_ in filters:
            for polygon_coord_str in geometry_coord_str:
                print(polygon_coord_str)
                query_str = f'{overpass_settings};({filter_}(poly:"{polygon_coord_str}");>;);out;'
                print(query_str)
                print(f'Requesting data within polygon from API in {len(polygon_coord_str)} request(s)')
                response_j = overpass_request(
                            query_str, 
                            timeout=timeout, 
                            overpass_endpoint=overpass_endpoint
                        )
                response_json.append(response_j)
    except:
        response_json = None
    return response_json

def retrieve_osm(geometry, osm_filter, timeout=180, overpass_endpoint='http://overpass-api.de/api'):
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
        API endpoint to use for the overpass queries
        
    Returns
    -------
    osmData: geojson
            response retrieved from overpass API

    """
    print(f"\nFetching OSM")
    response_json = download_OSM(geometry, filters=osm_filter)
    try:
        if ('remark' not in response_json) and (len(response_json[0]['elements']) == 0):
            print(f'No actual data retrieved')
        elif len(response_json) and (len(response_json[0]['elements'])>0):
            print(f'Data retrieve succesfully!')
    except:
        if (response_json == None) or ('remark' in response_json):
            print(f'Cutting the geometry ...')
            multi_pol = cut_geom(geometry, 2)
            #response_json = download_OSM(multi_pol, filters=osm_filter)
            response_json = get_cut_dfs(multi_pol, filters=osm_filter)
        else:
            print(f'No data retrieved!')
    return response_json

def generate_osm_gdf(response_json):
    """
    Generate GeoDataFrame from a response retrieved from the overpass API
    
    Parameters
    ----------
    response_json: list
        list with the response retrieved from the overpass API
    
    Return
    ------
    osm_gdf: geopandas.GeoDataFrame
        response from overpass API in geopandas.GeoDataFrame format
    
    """
    list_gdfs = []
    for el in response_json:
        geoms = OSM_response_to_lines(el)
        if geoms:
            gdf = gpd.GeoDataFrame(geometry=geoms)
            list_gdfs.append(gdf)
    try:
        osm_gdf = pd.concat(list_gdfs)
    except:
        osm_gdf = None
        print('Dataframe concatenation failed!')
    return osm_gdf

def _to_file(gdf, filename, driver):
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
    # output_path = kwargs.get('output_path', DEFAULT_PATH)
    # driver = kwargs.get('driver', DEFAULT_DRIVER)
    if not os.path.exists('./data'):
        os.makedirs('./data')
    try:
        gdf.to_file(f'./data/{filename}', driver=driver)
    except: raise ValueError('Local export failed!')


    ## TODO - Add in CollectionOsm

    # def retrieve_osmData(manifest, osm_filter, infrastructure,  path):
    # """
    # Download OSM ways and nodes within a given geometry from the Overpass API.
    
    # Parameters
    # ----------
    # manifest: geopandas.GeoDataFrame
    #         manifest geodataframe.
    # osm_type: string
    #     type of filter to retieve if custom_filter is None
    # infrastructure: string
    #     infrastructure type that will be use to build the overpas api query (e.g. 'way["highway"]')
    # custom_filter: string
    #     a custom filter to be used instead of the already defined in the osm_type
        
    # Returns
    # -------
    
    # """
    # if not os.path.exists(path):
    #     os.makedirs(path)
    #     print(f'new directory successfully created it {path}')
    
    # tiles_to_process = manifest[manifest.exclude == 0]

    # #once all the tiles have been processed the tiles_to_process will be 0
    # print(f'Tiles to process: {len(tiles_to_process), len(manifest)}')
    
    # for i in range(0, len(tiles_to_process)):
    #     print(f"{round(100*i/len(tiles_to_process),2)}%")
    #     entry = tiles_to_process.iloc[i]

    #     tile_id = entry['id']
    #     polygon = entry['geometry']

    #     # need to define the storage of the retrieved tiles
    #     export = True
    #     #upload = True
    #     successful_export = True if entry['exported'] == 1 else False
    #     #successful_upload = True if entry['uploaded'] == 1 else False
    #     exclude = True if entry['exclude'] == 1 else False

    #     # If exclude (i.e. no roads), dont export or upload
    #     #if exclude or all([successful_export, successful_upload]):
    #     if exclude or successful_export: 
    #         export = False
    #         #upload = False

    #      # If already exported, dont export again
    #     #elif successful_export and not successful_upload:
    #     #    export = False
    #     #    upload = True

    #     if export:
    #         print(f"\nFetching OSM for {tile_id.replace('_', '/')}\n")
    #         response_json = download_OSM(polygon,infrastructure=infrastructure,filters=osm_filter)

    #         #print(f'response status: {response_json.status_code}, lenght of response: {len(response_json)}')
            
    #         try:
    #             if ('remark' not in response_json) and (len(response_json['elements']) == 0):
    #                 print(f'No actual data in {tile_id}')

    #             elif len(response_json) and response_json['elements']>0:
    #                 print(f'Data retrieve for {tile_id}')
    #                 ## Create graph and convert of GeoDataFrame
    #                 geoms = OSM_response_to_lines(response_json)
    #                 #df = get_Lines_gdf(G)
    #                 if geoms:
    #                     df = gpd.GeoDataFrame(geometry=geoms)
    #                     #df.to_file(f'out.shp')

    #                 ## Attempt temporary LOCAL export
    #                 try:
    #                     df.to_csv(f'{path}/{tile_id}.csv', index=False)
    #                     successful_export = True
    #                     print('successful exported!')

    #                 except:
    #                     print('Local export failed')
    #                     print(f"\nExcluding {tile_id.replace('_', '/')}, no graph produced\n")
    #                     exclude = False
    #             # else:
    #             #     print(f"\nGeneration of graph failed! Excluding {tile_id.replace('_', '/')}, no graph produced\n")
    #             #     exclude = True
    #         except:
    #             # print(f"\nExcluding {tile_id.replace('_', '/')}, no graph produced\n")
    #             # exclude = True
    #             if (response_json == None) or ('remark' in response_json):
    #                 print(f'Cutting the geometry of {tile_id}...')
    #                 multi_pol = cut_geom(polygon, 2)
    #                 list_dfs = get_cut_dfs(multi_pol, infrastructure=infrastructure,filters=osm_filter)
    #                 try:
    #                     df = pd.concat(list_dfs)
    #                 except:
    #                     df = None
    #                     print('Dataframe concatenation failed!')
    #                 if df is not None:
    #                     print('Exporting df...')
    #                     df.to_csv(f'{path}/{tile_id}.csv', index=False)
    #                     successful_export = True
    #                     print('successful exported!')
    #                 else:
    #                     print('No data retrieved')
    #                     successful_export = False
    #                     print('Tile excluded!')
    #                     exclude =True
    #             else:
    #                 print(f'No data for {tile_id}')
    #                 print(f"\nExcluding {tile_id.replace('_', '/')}, no graph produced\n")
    #                 print('Tile excluded!')
    #                 exclude = True



                
    #     ## Update manifest
    #     index = manifest.index[manifest.id == tile_id].tolist()[0]
    #     manifest.at[index, 'exclude'] = 1 if exclude else 0
    #     manifest.at[index, 'exported'] = 1 if successful_export else 0  
    #     #manifest.at[index, 'uploaded'] = 1 if successful_upload else 0
        
    #     return manifest

