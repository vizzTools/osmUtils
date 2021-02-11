# Open Street Map Interface

**OSMUtils** is a Python package that interfaces with the [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide) aand lets you download spatial data from OpenStreetMap. You can retrieve data using different predefined filters or [customize your own](https://wiki.openstreetmap.org/wiki/Map_features#Leisure).

To work with **OSMUtils** you just need to import a geometry or bbx to fetch the features within. Once you have downloaded the requested features you can visualize them on a map, save them or retrieve their metadata for producing time-series visualizations.

**OSMUtils** is built on top of GeoPandas and folium. The library also interacts with overpass API (OpenSTreetMap’s API ) to:

- Download any kind of feature with a single line of code
- Download metadata associated with the features
- Visualize features in an interactive map
- Save response to disk as shapefile, Geojson or csv

## Developing

Make a copy of .env.sample (and rename .env, see requirements below)

## Requirement

Environment variables required:

TODO

