pyeuhcs
=======

Module for the integration and harmonisation of EU data on nation-wide  healthcare services.
---

**Quick install and start**

[![Binder](https://mybinder.org/badge_logo.svg)](http://mybinder.org/v2/gh/eurostat/healthcare-services/master?filepath=src/geo-py)

Once installed, the module can be imported simply:

```python
>>> import pyeudatnat
>>> import pyeuhcs
```

**Notebook examples**

* A [basic example](https://nbviewer.jupyter.org/github/eurostat/healthcare-services/blob/master/src/geo_py/notebooks/01_HCS_basic_example.ipynb) regarding healthcare services to start with the module.
* ...

**Usage**

###### Manual setting

You will need first to create a special class given the metadata associated each 
the national data:

```python
>>> from pyeuhcs import config
>>> CZhcs = config.facilityFactory(facility = 'HCS', country = 'CZ')
```

In this case, we create the class using predefined metadata (available from a `czhcs` module dedicated to
CZ data) that configure the input schema of the data. Instead you could use metadata stored in a JSON file.

Following, it is pretty straigthforward to create an instance of a national dataset:

```python
>>> cz = CZhcs()
>>> cz.load_data()
>>> cz.format_data()
>>> cz.save_data(fmt = 'csv')
```

Note the output schema (see also "attributes" in the documentation [below](#Data)) is defined in the [`config.py`](config.py) file.

###### Automated running

```python
>>> from pyeuhcs import harmonise
>>> harmonise.run(facility = 'HCS',country = 'CZ')
```

<!-- .. ` -->
###### Geocodiing

Default coder is `GISCO`, but you can use a different geocoder also using an appropriate key:

```python
>>> from pyeuhcs import harmonise
>>> harmonise.run(facility = 'HCS', country = 'BG', coder = {'Bing': "<your_api_key>")
```

**<a name="Data"></a>Data resources**
 
* National resources: see documentation regarding the [metadata about healthcare services](https://github.com/eurostat/healthcare-services/blob/master/docs/GISCO_healthcare_services_metadata.pdf).
* The Geographic Information System of the Commission at _Eurostat_: [_GISCO_ ](http://ec.europa.eu/eurostat/web/gisco/overview).
* _GISCO_ webservices: [_find-nuts_](http://europa.eu/webtools/rest/gisco/nuts/find-nuts.py) and [_geocode_](http://europa.eu/webtools/rest/gisco/api?).
 
