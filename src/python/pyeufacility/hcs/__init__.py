#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. __init__

* Initialisation module of country programmes for HCS configuration loading.
* Declaration of Healthcare Services configuration metadata.

**Description**

This module statically defines the HCS variable that can be used to generate the
`JSON` configuration metadata file `hcs.json`.

This can be ignored when `hcs.json` already exists and no change on the metadata
has been made. It can otherwise be used for update.

**Dependencies**

*require*:      :mod:`os`, :mod:`collections`, :mod:`datetime`

*call*:         :mod:`pyeudatnat`

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_
# *since*:        Wed Dec  2 16:47:18 2020

#%%
from os import path as osp
from collections import OrderedDict
from datetime import datetime

try:
    from pyeudatnat import BASENAME as __BASENAME, COUNTRIES as __COUNTRIES
except:
    __BASENAME = ''
    __COUNTRIES = {}

#from pyeufacility import PACKPATH


# note: paths are relative to pyeufacility dir, where the hcs.json will be stored
HCS             = {
    "path":     "../../../data/healthcare", # osp.abspath("../../../ddata/healthcare")
    "info":     "metadata.pdf", # osp.abspath("../../d../data/healthcare/metadata.pdf")
    "options": OrderedDict( [
        ("lang",    "en"),
        ("fmt",     {"geojson": "geojson", "csv": "csv", "gpkg": "gpkg"}),
        ("proj",    None), # "WGS84"
        ("sep",     ","),
        ("encoding",  "utf-8"),
        ("dtfmt",   "%d/%m/%Y")
        ] ),
    "index":    OrderedDict( [
        ("id",       {"name": "id",                     "desc": "The healthcare service identifier - This identifier is based on national identification codes, if it exists.",
                      "type": int.__name__,             "values": None}),
        ("name",     {"name": "hospital_name",          "desc": "The name of the healthcare institution",
                      "type": str.__name__,             "values": None}),
        ("site",     {"name": "site_name",              "desc": "The name of the specific site or branch of a healthcare institution",
                      "type": str.__name__,             "values": None}),
        ("lat",      {"name": "lat",                    "desc": "Latitude (WGS 84)",
                      "type": float.__name__,           "values": None}),
        ("lon",      {"name": "lon",                    "desc": "Longitude (WGS 84)",
                      "type": float.__name__,           "values": None}),
        ("geo_qual", {"name": "geo_qual",               "desc": "A quality indicator for the geolocation - 1: Good, 2: Medium, 3: Low, -1: Unknown",
                      "type": int.__name__,             "values": [-1, 1, 2, 3]}),
        ("street",   {"name": "street",                 "desc": "Street name",
                      "type": str.__name__,             "values": None}),
        ("number",   {"name": "house_number",           "desc": "House number",
                      "type": str.__name__,             "values": None}),
        ("postcode", {"name": "postcode",               "desc": "Postcode",
                      "type": str.__name__,             "values": None}),
        ("city",     {"name": "city", "desc":           "City name (sometimes refers to a region or a municipality)",
                      "type": str.__name__,             "values": None}),
        ("cc",       {"name": "cc", "desc":             "Country code (ISO 3166-1 alpha-2 format)",
                      "type": str.__name__,             "values": list(__COUNTRIES.keys())}),
        ("country",  {"name": "country",                "desc": "Country name",
                      "type": str.__name__,             "values": None}),
        ("beds",     {"name": "cap_beds",               "desc": "Measure of capacity by number of beds (most common)",
                      "type": int.__name__,             "values": None}),
        ("prac",     {"name": "cap_prac",               "desc": "Measure of capacity by number of practitioners",
                      "type": int.__name__,             "values": None}),
        ("rooms",    {"name": "cap_rooms",              "desc": "Measure of capacity by number of rooms",
                      "type": int.__name__,             "values": None}),
        ("ER",       {"name": "emergency",              "desc": "Flag 'yes/no' for whether the healthcare site provides emergency medical services",
                      "type": str.__name__,            "values": ['yes', 'no']}),
        ("type",     {"name": "facility_type",          "desc": "If the healthcare service provides a specific type of care, e.g. psychiatric hospital",
                      "type": str.__name__,             "values": None}),
        ("PP",       {"name": "public_private",         "desc": "Status 'private/public' of the healthcare service",
                      "type": str.__name__,             "values": ['public', 'private']}),
        ("specs",    {"name": "list_specs",             "desc": "List of specialties recognized in the European Union and European Economic Area according to EU Directive 2005/36/EC",
                      "type": str.__name__,             "values": None}),
        ("tel",      {"name": "tel", "desc":            "Telephone number",
                      "type": int.__name__,             "values": None}),
        ("email",    {"name": "email", "desc":          "Email address",
                      "type": str.__name__,             "values": None}),
        ("url",      {"name": "url", "desc":            "URL link to the institution's website",
                      "type": str.__name__,             "values": None}),
        ("refdate",  {"name": "ref_date",               "desc": "The reference date (DD/MM/YYYY) the data refers to. The dataset represents the reality as it was at this date.",
                      "type": datetime.__name__,        "values": None}),
        ("pubdate",  {"name": "pub_date",               "desc": "The publication date of the dataset by Eurostat (DD/MM/YYYY). This should be used to track when this Eurostat dataset has changed.",
                      "type": datetime.__name__,        "values": None}),
        ("comments", {"name": "comments",               "desc": "Comments",
                      "type": str.__name__,             "values": None})
        ] )
      # notes:
      #  i. house_number should be string, not int.. .e.g. 221b Baker street
      #  ii. we use an ordered dict to use the same column order when writing the output file
    }


# __all__ = ['%s%s' % (__BASENAME, __cc, __FAC) for cc in list(COUNTRIES.values())]
__all__ = [ ]#analysis:ignore

__fac = 'hcs'
#__path = osp.join(PACKPATH, __fac)

for __cc in __COUNTRIES.keys():
    __src = '%s%s%s' % (__BASENAME, __cc, __fac)
    # __fsrc = osp.join(__path, '%s.py' % __src)
    __fsrc = '%s.py' % __src
    try:
        assert osp.exists(__fsrc) and osp.isfile(__fsrc)
    except:     pass
    else:
        __all__.append(__src)

try:
    del(__fac, __BASENAME, __COUNTRIES)
    del(__cc, __src, __fsrc)
except: pass
