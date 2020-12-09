
"""General utility functions."""
from . import settings
import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon

def geometry_to_gdf(self, geometry, crs):
        """
        Create GeoDataFrame from a (multi)polygon.
        Parameters
        ----------
        geometry : shapely.geometry.Polygon or shapely.geometry.MultiPolygon
            geographic boundaries to fetch geometries within
        Returns
        -------
        gdf : geopandas.GeoDataFrame
        """
        #check that incomming geometry is valid
        if not geometry.is_valid:
            print('The geometry is invalid')
        #check that the geometry is a polygon or multipolygon
        if not isinstance(geometry, (Polygon, MultiPolygon)):
            print('The geometry must be a shapely.geometry.Polygon or shapely.geometry.MultiPolygon')
    
        #create gdf from the incomming geometry

        gdf = gpd.GeoDataFrame(geometry)
        gdf = gdf.set_geometry(0)
        gdf = gdf.rename(columns={0:'geometry'})

        if gdf.crs is None:
            gdf = self.set_crs(gdf, crs)

        elif gdf.crs != self.crs:
            gdf = self.reproject_gdf(gdf,crs)

        return gdf

def set_crs(gdf):
    """
    Set CRS in GeoDataFrame when current projection is not defined.
    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        the geodataframe to set the projection
    Returns
    -------
    gdf : geopandas.GeoDataFrame
        the geodataframe with the projection defined """
    gdf = gdf.set_crs(default_crs)
    return gdf
    
def reproject_gdf(gdf,to_crs):
    """Project a GeoDataFrame from its current CRS to another.
    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        the GeoDataFrame to be projected
    to_crs : string 
        CRS to project the geodataframe
    Returns
    ----------
    gdf_proj : geopandas.GeoDataFrame
        the projected GeoDataFrame"""
    
    gdf_proj = gdf.to_crs(epsg=to_crs)
    return gdf_proj


# import requests
# import json
# import time
# import datetime as dt
# from shapely.geometry import LineString, mapping, shape, box


# def _get_pause_duration(
#     default_duration=5, 
#     overpass_endpoint='http://overpass-api.de/api'
#     ):

#     """
#     Check the Overpass API status endpoint to determine how long to wait until
#     next slot is available.
#     """

#     try:
#         url = overpass_endpoint.rstrip('/') + '/status'
#         response = requests.get(url)#, headers=_get_http_headers())
#         status = response.text.split('\n')[3]
#         status_first_token = status.split(' ')[0]
#     # if we cannot reach the status endpoint or parse its output, log an
#     # error and return default duration
#     except:
#         print(f'Unable to query {url}')
#         return default_duration
#     try:
#         # if first token is numeric, it's how many slots you have available - no
#         # wait required
#         available_slots = int(status_first_token)
#         pause_duration = 0
#     except:
#         # if first token is 'Slot', it tells you when your slot will be free
#         if status_first_token == 'Slot':
#             utc_time_str = status.split(' ')[3]
#             utc_time = dt.datetime.strptime(utc_time_str,'%Y-%m-%dT%H:%M:%SZ,')
#             pause_duration = int((utc_time - dt.datetime.utcnow()).total_seconds() + 1)
#             pause_duration = max(pause_duration, 1)

#         # if first token is 'Currently', it is currently running a query
#         elif status_first_token == 'Currently':
#             time.sleep(default_duration)
#             pause_duration = _get_pause_duration()
#         else:
#             print(f'Unrecognized server status: "{status}"')
#             return default_duration

#     return pause_duration


# def overpass_request(
#     query_string, 
#     pause_duration=1, 
#     timeout=180,
#     overpass_endpoint='http://overpass-api.de/api'
#     ):
#     """
#     Send a request to the Overpass API via HTTP POST and return the JSON
#     response.
#     Parameters
#     ----------
#     query_string : str
#         Overpass API query string
#     pause_duration : int
#         how long to pause in seconds before requests, if None, will query API
#         status endpoint to find when next slot is available
#     timeout : int
#         the timeout interval for the requests library
#     Returns
#     -------
#     dict
#     """
#     url = overpass_endpoint.rstrip('/') + '/interpreter'

#     # Check server status first and wait if overloaded
#     if pause_duration is None:
#         pause_duration = _get_pause_duration()
#     print(f'Pausing {pause_duration} seconds before making API POST request')
#     time.sleep(pause_duration)

#     # Post request
#     data = {'data': query_string}
#     print(f'Posting to {url} with timeout={timeout}, "{data}"')
#     response = requests.post(url, data={'data': query_string}, timeout=timeout)

#     try:
#         response_json = response.json()
#         if 'remark' in response_json:
#             print(f'Server remark: "{response_json["remark"]}"')

#     except:
#         if response.status_code in [429, 504]:
#             error_pause_duration = _get_pause_duration()
#             print(f'Server returned status {response.status_code} and no JSON data: retrying in {error_pause_duration} seconds.')
#             time.sleep(error_pause_duration)
#             response_json = overpass_request(query_string, pause_duration=pause_duration, timeout=timeout)
#         # else, this was an unhandled status_code, throw an exception
#         else:
#             print(f'Server returned status code {response.status_code} and no JSON data.')
#             print(f'Server returned no JSON data\n{response} {response.reason}\n{response.text}')
            
#         # 429 is 'too many requests' and 504 is 'gateway timeout' from server
#         # overload - handle these errors by recursively calling overpass_request
#         #if response.status_code in [429, 504]:
#         #    error_pause_duration = _get_pause_duration()
#         #    print(f'Server returned status {response.status_code} and no JSON data: retrying in {error_pause_duration} seconds.')
#         #    time.sleep(error_pause_duration)
#         #    data = {'data': query_string}
#         #    print(f'Posting to {url} with timeout={timeout}, "{data}"')
#         #    response = requests.post(url, data={'data': query_string}, timeout=timeout)
#         #    try:
#         #        response_json = response.json()
#         #        if 'remark' in response_json:
#         #            print(f'Server remark: "{response_json["remark"]}"')
#         #    except:
#         #        if response.status_code in [429, 504]:
#         #            
#         #            print(f'Server returned status {response.status_code} and no JSON data')
#         #            response_json = []
#         #        else:
#         #            response_json = []
#                     #pass
#             #response_json = overpass_request(data=data, pause_duration=pause_duration, timeout=timeout)
#             #response_json = overpass_request(query_str, pause_duration=pause_duration, timeout=timeout)
#         # else, this was an unhandled status_code, throw an exception
#         #else:
#         #    print(f'Server returned status code {response.status_code} and no JSON data.')
#         #    print(f'Server returned no JSON data\n{response} {response.reason}\n{response.text}')

#     return response_json

# def _get_coordinate_string(geometry):
#     """
#     Extract exterior coordinates from polygon(s) to pass to OSM in a query by
#     polygon. Ignore the interior ("holes") coordinates. Round to 6 places.
#     """
#     x, y = geometry.exterior.xy
#     coords = list(zip(x, y))
#     return ' '.join([f'{xy[1]:.6f} {xy[0]:.6f}' for xy in coords])

# def download_OSM(
#     polygon,
#     infrastructure='way["highway"]',
#     filters='',
#     timeout=180,
#     overpass_endpoint='http://overpass-api.de/api'
# ):
#     """
#     Query Overpass API and parse response to a list of LineString(s)
#     """
#     polygon_coord_str = _get_coordinate_string(polygon)
#     overpass_settings = f'[out:json][timeout:{timeout}]'
    
#     # Query string in Overpass QL
#     # Essetially look for everything that matches 
#     #  `infrastructure` and `filters`
#     #  within `poly`
#     #  selecting children with `>`
#     query_str = f'{overpass_settings};({infrastructure}{filters}(poly:"{polygon_coord_str}");>;);out;'
#     try:
        
#         response_json = overpass_request(
#             query_str, 
#             timeout=timeout, 
#             overpass_endpoint=overpass_endpoint
#         )
#     except:
        
#         response_json = None
#     return response_json

# def cut_geom(polygon, N):

#     """
#     Cut geometry of request is to big. NOTE_: NEEDS TO BE CHECKED

#     """

#     # Get bounds of grid
#     lon_end,lat_start,lon_start,lat_end = polygon.bounds
#     print(lon_end,lat_start,lon_start,lat_end)

#     num_cells = N * N
#     lon_edge = (lon_end - lon_start) / (num_cells ** 0.5)
#     lat_edge = (lat_end - lat_start) / (num_cells ** 0.5)

#     # Generate grid over feature
#     polys = []
#     lon = lon_start
#     for i in range(0, N):
#         x1 = lon
#         x2 = lon + lon_edge
#         lon += lon_edge
#         lat = lat_start
#         for j in range(0, N):
#             y1 = lat
#             y2 = lat + lat_edge
#             lat += lat_edge
#             polygon_temp = box(x1, y1, x2, y2)
#             polys.append(polygon_temp)

#     # Intersects grid against feature
#     intersected_feats = []
#     for p in polys:
#         is_intersect = p.intersects(polygon)
#         if is_intersect:
#             intersection = p.intersection(polygon)
#             intersected_feats.append(intersection)
        
#     return intersected_feats

# def OSM_response_to_lines(response_json):
#     """
#     Parse Overpass API json response to extract ways as linestrings
#     """
#     if not 'elements' in response_json:
#         print("No elements in response!")
#         return []
    
#     # Iterate through elements in Overpass API response
#     nodes_xy = {}
#     ways = {}
#     for el in response_json['elements']:
#         if el['type'] == 'node':
#             # Save nodes as points
#             nodes_xy[el['id']] = (el['lon'], el['lat'])
#         if el['type'] == 'way':
#             # Save ways as lists of their node IDs
#             ways[el['id']] = el['nodes']

#     # Create line strings from lists of nodes
    
#     ########
#     # TODO: Add simplification logic here
#     #  e.g. remove duplicate points, etc.

#     geoms = []
# fail_nodes = []
# for way_nodes in ways.values():
#     try:
#         line_ = LineString([nodes_xy[n] for n in way_nodes])
#         geoms.append(line_)
#     except:
#         print(f'{way_nodes} failed!')
#         fail_nodes.append(way_nodes)
        
#     try:

#         geoms = []
#         for  way_nodes in ways.values():
#             try:
#                 _line = LineString([nodes_xy[n] for en in way_nodes])
#                 geoms.append(_line)
#             except:
#                 # catch individual points that cannot be used to generate  a way (we need to nodes for a way)
#                 print(f'{way_nodes} failed') #improve error message
#     except:
#         geoms = None
#     return geoms