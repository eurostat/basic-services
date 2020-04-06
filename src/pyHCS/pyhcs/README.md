pyhcs
=====

Harmonised formatting of national data on healthcare services.
---

**Quick install and start**

[![Binder](https://mybinder.org/badge_logo.svg)](http://mybinder.org/v2/gh/eurostat/statistics-coded/master?filepath=index.ipynb)

TBC

Once installed, the module can be imported simply:

```python
>>> import pyhcs
```

**Notebook examples**

TBC

**Usage**

###### Manual setting

You will need first to create a special class given the metadata associated each 
the national data:

```python
>>> from pyhcs import base, czhcs
>>> CZHCS = base.hcsFactory(czhcs.METADATA)
```

In this case, we create the class using predefined metadata (available from a `czhcs` module dedicated to
CZ data) that configure the input schema of the data. Instead you could use metadata stored in a JSON file.

Following, it is pretty straigthforward to create an instance of a national dataset:

```python
>>> cz = CZHCS()
>>> cz.load_source()
>>> cz.format_data()
>>> cz.save_data(fmt = 'csv')
```

Note the output schema (see also "attributes" in the documentation [below](#Data)) is defined in the [`config.py`](config.py) file.

###### Automated running

```python
>>> from pyhcs import harmonise
>>> harmonise.run(country = 'CZ')
```

<!-- .. ` -->
###### Features

* Various possible geocoding, including `GISCO`.

Default coder is `GISCO`, but you can use a different geocoder also using an appropriate key:

```python
>>> from pyhcs import harmonise
>>> harmonise.run(country = 'BG', coder = {'Bing': "<your_api_key>")
```

* Automated translation,
* ...

**<a name="Data"></a>Data resources**
 
* National resources: see documentation regarding the [metadata about healthcare services](https://github.com/eurostat/healthcare-services/blob/master/docs/GISCO_healthcare_services_metadata.pdf).
* The Geographic Information System of the Commission at _Eurostat_: [_GISCO_ ](http://ec.europa.eu/eurostat/web/gisco/overview).
* _GISCO_ webservices: [_find-nuts_](http://europa.eu/webtools/rest/gisco/nuts/find-nuts.py) and [_geocode_](http://europa.eu/webtools/rest/gisco/api?).
 
**<a name="Software"></a>Software resources/dependencies**

* Packages for data handling: [`pandas`](http://pandas.pydata.org).
* Packages for geocoding:  [`geopy`](https://github.com/geopy/geopy), [`pyproj`](https://github.com/pyproj4/pyproj) and [`happygisco`](https://github.com/eurostat/happyGISCO).
* Package for JSON formatting:  [`geojson`](https://github.com/jazzband/geojson).
* Package for translations:  [`googletrans`](https://github.com/ssut/py-googletrans).
<!-- * Packages for map visualisations: [`ipyleaflet`](https://github.com/jupyter-widgets/ipyleaflet) or [`folium`](https://github.com/python-visualization/folium). -->

