#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _config

Configuration module providing, among others, with the formatting template for 
the output integrated data.

**Dependencies**

*require*:      :mod:`os`, :mod:`warnings`, :mod:`collections`, :mod:`datetime`

*optional*:     :mod:`json`

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Tue Mar 31 22:51:37 2020

#%%
import warnings#analysis:ignore

from collections import OrderedDict
from os import path as osp

from datetime import datetime

try:                          
    import simplejson as json
except ImportError:
    try:                          
        import json
    except ImportError:
        class json:
            def load(arg):  
                with open(arg,'r') as f:
                    return f.read()
            def dump(arg):  
                return '%s' % arg

from . import BASE


#%%

IPATH           = '../data/raw/'

OINDEX          = OrderedDict( [
    ('id',       {'name': 'id',              'type': int,        'desc': "The healthcare service identifier - This identifier is based on national identification codes, if it exists."}),
    ('name',     {'name': 'hospital_name',   'type': str,        'desc': "The name of the healthcare institution"}),
    ('site',     {'name': 'site_name',       'type': str,        'desc': "The name of the specific site or branch of a healthcare institution"}),
    ('lat',      {'name': 'lat',             'type': float,      'desc': "Latitude (WGS 84)"}),
    ('lon',      {'name': 'lon',             'type': float,      'desc': "Longitude (WGS 84)"}),
    ('geo_qual', {'name': 'geo_qual',        'type': int,        'desc': "A quality indicator for the geolocation - 1: Good, 2: Medium, 3: Low, -1: Unknown"}),
    ('street',   {'name': 'street',          'type': str,        'desc': "Street name"}),
    ('number',   {'name': 'house_number',    'type': str,        'desc': "House number"}),
    ('postcode', {'name': 'postcode',        'type': str,        'desc': "Postcode"}),
    ('city',     {'name': 'city',            'type': str,        'desc': "City name (sometimes refers to a region or a municipality)"}),
    ('cc',       {'name': 'cc',              'type': str,        'desc': "Country code (ISO 3166-1 alpha-2 format)"}),
    ('country',  {'name': 'country',         'type': str,        'desc': "Country name"}),
    ('beds',     {'name': 'cap_beds',        'type': int,        'desc': "Measure of capacity by number of beds (most common)"}),
    ('prac',     {'name': 'cap_prac',        'type': int,        'desc': "Measure of capacity by number of practitioners"}),
    ('rooms',    {'name': 'cap_rooms',       'type': int,        'desc': "Measure of capacity by number of rooms"}),
    ('ER',       {'name': 'emergency',       'type': bool,       'desc': "Flag 'yes/no' for whether the healthcare site provides emergency medical services"}),
    ('type',     {'name': 'facility_type',   'type': str,        'desc': "If the healthcare service provides a specific type of care, e.g. psychiatric hospital"}),
    ('PP',       {'name': 'pulic_private',	'type': int,        'desc': "Status 'private/public' of the healthcare service"}),
    ('specs',    {'name': 'list_specs',      'type': str,        'desc': "List of specialties recognized in the European Union and European Economic Area according to EU Directive 2005/36/EC"}),
    ('tel',      {'name': 'tel',             'type': int,        'desc': "Telephone number"}),
    ('email',    {'name': 'email',           'type': str,        'desc': "Email address"}),
    ('url',      {'name': 'url',             'type': str,        'desc': "URL link to the institution's website"}),
    ('refdate',  {'name': 'ref_date',        'type': datetime,   'desc': "The reference date of the data (DD/MM/YYYY)"}),
    ('pubdate',  {'name': 'pub_date',        'type': datetime,   'desc': "The date that the data was last published (DD/MM/YYYY)"})
   ] )
# notes: 
#  i. house_number should be string, not int.. .e.g. 221b Baker street
#  ii. we use an ordered dict to use the same column order when writing the output file

ODATE           = '%d/%m/%Y'# format DD/MM/YYYY
OLANG           = 'en'
OSEP            = ','
OENC            = 'utf-8'

OPATH           = '../data/' # '../data/%s'
OFILE           = '%s.%s'
OFMT            = {'geojson': 'json', 'json': 'json', 'csv': 'csv', 'gpkg': 'gpkg'}    
OPROJ           = None # 'WGS84'

IPLACE          = ['street', 'number', 'postcode', 'city', 'country']
# LATLON        = ['lat', 'lon'] # 'coord' # 'latlon'
# ORDER         = 'lL' # first lat, second Lon 


#%%

__config = 'config'
__cfgfile = '%s%s.json' % (__config, BASE) 
__thisdir = osp.dirname(__file__)

__gvar = ['ipath', 'oindex', 'odate', 'olang', 'osep', 'oenc',  \
          'opath', 'ofile', 'ofmt', 'oproj', 'iplace'] #analysis:ignore

try:
    assert osp.exists(osp.join(__thisdir, __cfgfile))
    with open(__cfgfile, 'r') as fp:
        __metadata = json.load(fp)
except (AssertionError,ImportError):
    warnings.warn('metadata file not available - it will be created')
    __metadata = {}
    for var in __gvar:
        try:
            exec("__metadata.update({'" + str(var).lower() + "' : " + str(var).upper() + "})")
        except:
            continue
    # this is nothing else than:
    #__metadata = {'ipath':      IPATH,
    #              'oindex':     OINDEX,
    #              'odate':      ODATE,
    #              'olang':      OLANG,
    #              'osep':       OSEP,
    #              'oenc':       OENC,
    #              'opath':      OPATH,
    #              'ofile':      OFILE,
    #              'ofmt':       OFMT,  
    #              'oproj':      OPROJ,
    #              'iplace':     IPLACE
    #              }
    with open(__cfgfile, 'w') as fp:
        json.dump(__metadata,fp)
else:
    warnings.warn('loading configuration parameters from metadata file')
    for var in __gvar:
        try:
            exec(str(var).upper() + " = __metadata.get('" + str(var).lower() + "'," + str(var).upper()+ ")")
        except:
            continue
    # this is nothing else than:
    #IPATH       = __metadata.get('ipath', IPATH)
    #OINDEX      = __metadata.get('oindex', OINDEX)
    #ODATE       = __metadata.get('odate', ODATE)
    #OLANG       = __metadata.get('olang', OLANG)
    #OSEP        = __metadata.get('osep', OSEP)
    #OENCODING   = __metadata.get('oenc', OENC)
    #OPATH       = __metadata.get('opath', OPATH)
    #OFILE       = __metadata.get('ofile', OFILE)
    #OFMT        = __metadata.get('ofmt', OFMT)    
    #OPROJ       = __metadata.get('oproj', OPROJ)
    #IPLACE      = __metadata.get('iplace', IPLACE)
