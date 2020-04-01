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

from collections import OrderedDict, Mapping, Sequence
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
                with open(arg,"r") as f:
                    return f.read()
            def dump(arg):  
                return "%s" % arg

from pyhcs import BASENAME

#%%

BASETYPE        = {t.__name__: t for t in [type, bool, int, float, str, datetime]}
__type2name = lambda t: t.__name__  # lambda t: {v:k for (k,v) in BASETYPE.items()}[t]    

#%%

OCONFIGNAME     = ["index",                                             \
                   "fmt", "lang", "sep", "enc", "date", "proj",         \
                   "path", "file"] #analysis:ignore
"""Metadata fields related to output template.
"""

INDEX           = OrderedDict( [
    ("id",       {"name": "id",              "type": __type2name(int),        "desc": "The healthcare service identifier - This identifier is based on national identification codes, if it exists."}),
    ("name",     {"name": "hospital_name",   "type": __type2name(str),        "desc": "The name of the healthcare institution"}),
    ("site",     {"name": "site_name",       "type": __type2name(str),        "desc": "The name of the specific site or branch of a healthcare institution"}),
    ("lat",      {"name": "lat",             "type": __type2name(float),      "desc": "Latitude (WGS 84)"}),
    ("lon",      {"name": "lon",             "type": __type2name(float),      "desc": "Longitude (WGS 84)"}),
    ("geo_qual", {"name": "geo_qual",        "type": __type2name(int),        "desc": "A quality indicator for the geolocation - 1: Good, 2: Medium, 3: Low, -1: Unknown"}),
    ("street",   {"name": "street",          "type": __type2name(str),        "desc": "Street name"}),
    ("number",   {"name": "house_number",    "type": __type2name(str),        "desc": "House number"}),
    ("postcode", {"name": "postcode",        "type": __type2name(str),        "desc": "Postcode"}),
    ("city",     {"name": "city",            "type": __type2name(str),        "desc": "City name (sometimes refers to a region or a municipality)"}),
    ("cc",       {"name": "cc",              "type": __type2name(str),        "desc": "Country code (ISO 3166-1 alpha-2 format)"}),
    ("country",  {"name": "country",         "type": __type2name(str),        "desc": "Country name"}),
    ("beds",     {"name": "cap_beds",        "type": __type2name(int),        "desc": "Measure of capacity by number of beds (most common)"}),
    ("prac",     {"name": "cap_prac",        "type": __type2name(int),        "desc": "Measure of capacity by number of practitioners"}),
    ("rooms",    {"name": "cap_rooms",       "type": __type2name(int),        "desc": "Measure of capacity by number of rooms"}),
    ("ER",       {"name": "emergency",       "type": __type2name(bool),       "desc": "Flag 'yes/no' for whether the healthcare site provides emergency medical services"}),
    ("type",     {"name": "facility_type",   "type": __type2name(str),        "desc": "If the healthcare service provides a specific type of care, e.g. psychiatric hospital"}),
    ("PP",       {"name": "public_private",	 "type": __type2name(int),        "desc": "Status 'private/public' of the healthcare service"}),
    ("specs",    {"name": "list_specs",      "type": __type2name(str),        "desc": "List of specialties recognized in the European Union and European Economic Area according to EU Directive 2005/36/EC"}),
    ("tel",      {"name": "tel",             "type": __type2name(int),        "desc": "Telephone number"}),
    ("email",    {"name": "email",           "type": __type2name(str),        "desc": "Email address"}),
    ("url",      {"name": "url",             "type": __type2name(str),        "desc": "URL link to the institution's website"}),
    ("refdate",  {"name": "ref_date",        "type": __type2name(datetime),   "desc": "The reference date of the data (DD/MM/YYYY)"}),
    ("pubdate",  {"name": "pub_date",        "type": __type2name(datetime),   "desc": "The date that the data was last published (DD/MM/YYYY)"})
   ] )
# notes: 
#  i. house_number should be string, not int.. .e.g. 221b Baker street
#  ii. we use an ordered dict to use the same column order when writing the output file

FMT             = {"geojson": "json", "json": "json", "csv": "csv", "gpkg": "gpkg"}    
LANG            = "en"
SEP             = ","
ENC             = "utf-8"
DATE            = "%d/%m/%Y"# format DD/MM/YYYY
PROJ            = None # "WGS84"
    
PATH            = "../data/" # "../data/%s"
FILE            = "%s.%s"


#%%

class __JSON(object):
    
    is_order_preserved = False # True
    # note: when is_order_preserved is False, this entire class can actually be
    # ignored since the dump/load methods are exactly equivalent to the original
    # dump/load method of the json package
    is_OrderedDict_used = isinstance(INDEX,OrderedDict) 
    
    @classmethod
    def serialize(cls, data):
        if data is None or isinstance(data, (type, bool, int, float, str)):
            return data
        elif isinstance(data, Sequence):    
            if isinstance(data, list):          return [cls.serialize(val) for val in data]
            elif isinstance(data, tuple):       return {"tup": [cls.serialize(val) for val in data]}
        elif isinstance(data, Mapping):    
            if isinstance(data, OrderedDict):   return {"odic": [[cls.serialize(k), cls.serialize(v)] for k, v in data.items()]}
            elif isinstance(data, dict):
                if all(isinstance(k, str) for k in data):
                    return {k: cls.serialize(v) for k, v in data.items()}
                return {"dic": [[cls.serialize(k), cls.serialize(v)] for k, v in data.items()]}
        elif isinstance(data, set):             return {"set": [cls.serialize(val) for val in data]}
        raise TypeError("Type %s not data-serializable" % type(data))
    
    @classmethod
    def restore(cls, dct):
        if "dic" in dct:            return dict(dct["dic"])
        elif "tup" in dct:          return tuple(dct["tup"])
        elif "set" in dct:          return set(dct["set"])
        elif "odic" in dct:         return OrderedDict(dct["odic"])
        return dct
    
    @classmethod
    def dump(cls, data, f, **kwargs):
        try:        assert cls.is_OrderedDict_use is True and cls.is_order_preserved is True 
        except:     json.dump(data, f, **kwargs)
        else:       json.dump(cls.serialize(data), f, **kwargs)
    
    @classmethod
    def load(cls, s, **kwargs):
        try:        assert cls.is_OrderedDict_use is True and cls.is_order_preserved is True 
        except:     return json.load(s, **kwargs)
        else:       return json.load(s, object_hook=cls.restore, **kwargs)


#%%

__thisdir = osp.dirname(__file__)
__cfg = "config"
__cfgfile = osp.join(__thisdir,  "%s%s.json" % (__cfg, BASENAME))

try:
    assert osp.exists(__cfgfile)
    with open(__cfgfile, 'r') as fp:
        __cfgmeta = __JSON.load(fp)
except (AssertionError,ImportError):
    warnings.warn('metadata file not available - it will be created')
    __cfgmeta = {}
    for var in OCONFIGNAME:
        try:
            exec('__cfgmeta.update({"' + str(var).lower() + '" : ' + str(var).upper() + '})')
        except:         continue
    # this is not much different from doing:
    #__cfgmeta  = {"index":     INDEX,
    #              "fmt":       FMT,  
    #              "lang":      LANG,
    #              "sep":       SEP,
    #              "enc":       ENC,
    #              "date":      DATE,
    #              "proj":      PROJ,
    #              "path":      PATH,
    #              "file":      FILE}
    with open(__cfgfile, 'w') as fp:
        __JSON.dump(__cfgmeta,fp)
else:
    warnings.warn('loading configuration parameters from metadata file')
    for var in OCONFIGNAME:
        try:
            exec(str(var).upper() + ' = __cfgmeta.get("' + str(var).lower() + '",' + str(var).upper()+ ')')
        except:         continue
    # this is nothing else than:
    #INDEX      = __cfgmeta.get("index", INDEX)
    #FMT        = __cfgmeta.get("fmt",   FMT)    
    #LANG       = __cfgmeta.get("lang",  LANG)
    #SEP        = __cfgmeta.get("sep",   SEP)
    #ENCODING   = __cfgmeta.get("enc",   ENC)
    #DATE       = __cfgmeta.get("date",  DATE)
    #PROJ       = __cfgmeta.get("proj",  PROJ)
    #PATH       = __cfgmeta.get("path",  PATH)
    #FILE       = __cfgmeta.get("file",  FILE)
