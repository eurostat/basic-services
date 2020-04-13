#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _config

Generic configuration module providing, among others, with the formatting template 
for the output integrated data on different facilities.

**Dependencies**

*require*:      :mod:`os`, :mod:`warnings`, :mod:`collections`, :mod:`datetime`

*optional*:     :mod:`json`

*call*:         :mod:`pygeofacility`         

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Tue Mar 31 22:51:37 2020

#%%

from os import path as osp
import warnings

from collections import OrderedDict, Mapping, Sequence#analysis:ignore
from six import string_types
from copy import deepcopy

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

from pygeofacil import PACKPATH, FACILITIES, COUNTRIES
from pygeofacil.misc import MetaData


#%%

__THISFILE      = __file__

OCFGFILE        = osp.basename(__THISFILE).split('.')[0] # "config"

#%%

OBASETYPE       = {t.__name__: t for t in [type, bool, int, float, str, datetime]}
__type2name     = lambda t: t.__name__  # lambda t: {v:k for (k,v) in OBASETYPE.items()}[t]    


__OCFGDATA      = dict.fromkeys(list(FACILITIES.keys()), {})
__OCFGDATA.update( { 
        "HCS": {
                "fmt":      {"geojson": "geojson", "json": "json", "csv": "csv", "gpkg": "gpkg"},
                "lang":     "en",
                "sep":      ",",
                "enc":      "utf-8",
                "date":     "%d/%m/%Y", # format DD/MM/YYYY
                "proj":     None, # "WGS84"
                "path":     "../../../data/", # osp.abspath(osp.join(__THISDIR,"../../../data/")) 
                "file":     "%s.%s",
                "index":    OrderedDict( [ # in Python 3, order of keys is actually preserved
                        ("id",       {"name": "id",                     "desc": "The healthcare service identifier - This identifier is based on national identification codes, if it exists.",
                                      "type": __type2name(int),         "values": None}),
                        ("name",     {"name": "hospital_name",          "desc": "The name of the healthcare institution",   
                                      "type": __type2name(str),         "values": None}),
                        ("site",     {"name": "site_name",              "desc": "The name of the specific site or branch of a healthcare institution",       
                                      "type": __type2name(str),         "values": None}),
                        ("lat",      {"name": "lat",                    "desc": "Latitude (WGS 84)",             
                                      "type": __type2name(float),       "values": None}),
                        ("lon",      {"name": "lon",                    "desc": "Longitude (WGS 84)",             
                                      "type": __type2name(float),       "values": None}),
                        ("geo_qual", {"name": "geo_qual",               "desc": "A quality indicator for the geolocation - 1: Good, 2: Medium, 3: Low, -1: Unknown",        
                                      "type": __type2name(int),         "values": [-1, 1, 2, 3]}),
                        ("street",   {"name": "street",                 "desc": "Street name",          
                                      "type": __type2name(str),         "values": None}),
                        ("number",   {"name": "house_number",           "desc": "House number",    
                                      "type": __type2name(str),         "values": None}),
                        ("postcode", {"name": "postcode",               "desc": "Postcode",        
                                      "type": __type2name(str),         "values": None}),
                        ("city",     {"name": "city", "desc":           "City name (sometimes refers to a region or a municipality)",            
                                      "type": __type2name(str),         "values": None}),
                        ("cc",       {"name": "cc", "desc":             "Country code (ISO 3166-1 alpha-2 format)",              
                                      "type": __type2name(str),         "values": list(COUNTRIES.keys())}),
                        ("country",  {"name": "country",                "desc": "Country name",         
                                      "type": __type2name(str),         "values": None}),
                        ("beds",     {"name": "cap_beds",               "desc": "Measure of capacity by number of beds (most common)",        
                                      "type": __type2name(int),         "values": None}),
                        ("prac",     {"name": "cap_prac",               "desc": "Measure of capacity by number of practitioners",        
                                      "type": __type2name(int),         "values": None}),
                        ("rooms",    {"name": "cap_rooms",              "desc": "Measure of capacity by number of rooms",       
                                      "type": __type2name(int),         "values": None}),
                        ("ER",       {"name": "emergency",              "desc": "Flag 'yes/no' for whether the healthcare site provides emergency medical services",       
                                      "type": __type2name(bool),        "values": ['yes', 'no']}),
                        ("type",     {"name": "facility_type",          "desc": "If the healthcare service provides a specific type of care, e.g. psychiatric hospital",   
                                      "type": __type2name(str),         "values": None}),
                        ("PP",       {"name": "public_private",         "desc": "Status 'private/public' of the healthcare service",	 
                                      "type": __type2name(int),         "values": ['public', 'private']}),
                        ("specs",    {"name": "list_specs",             "desc": "List of specialties recognized in the European Union and European Economic Area according to EU Directive 2005/36/EC",      
                                      "type": __type2name(str),         "values": None}),
                        ("tel",      {"name": "tel", "desc":            "Telephone number",             
                                      "type": __type2name(int),         "values": None}),
                        ("email",    {"name": "email", "desc":          "Email address",           
                                      "type": __type2name(str),         "values": None}),
                        ("url",      {"name": "url", "desc":            "URL link to the institution's website",             
                                      "type": __type2name(str),         "values": None}),
                        ("refdate",  {"name": "ref_date",               "desc": "The reference date of the data (DD/MM/YYYY)",        
                                      "type": __type2name(datetime),    "values": "%d/%m/%Y"}),
                        ("pubdate",  {"name": "pub_date",               "desc": "The date that the data was last published (DD/MM/YYYY)",        
                                      "type": __type2name(datetime),    "values": "%d/%m/%Y"})
                       ] ),
                    # notes: 
                    #  i. house_number should be string, not int.. .e.g. 221b Baker street
                    #  ii. we use an ordered dict to use the same column order when writing the output file
                },
        #"Edu": { 
        #       "CFGKEYS": []         
        #        }                        
            })
[v.update({"type": FACILITIES[k].copy()}) for (k,v) in __OCFGDATA.items()]

OCFGDATA        = deepcopy(__OCFGDATA)


#%%
#==============================================================================
# Class TypeFacility
#==============================================================================
      
class TypeFacility(MetaData):
    """
    """
    
    #/************************************************************************/
    def __init__(self, *args, **kwargs):
        facility = kwargs.pop('facility', None)
        if facility is None:
            pass
        elif not isinstance(facility, string_types):
            raise TypeError('wrong facility type %s - must be a string' % facility)
        elif not facility in FACILITIES.keys():
            raise IOError('unknown facility %s - must be any key in %s' % (facility,list(FACILITIES.keys())))
        super(TypeFacility, self).__init__(*args, **kwargs)
        self.__metakeys = [ ]
        try:
            self.__facility = FACILITIES[facility].copy()
        except:
            self.__facility = {}
            
    #/************************************************************************/
    def loads(self, src=None, **kwargs):
        """Reloading metadata from default config file into global configuration 
        variables.
        """
        if src is None:
            try:
                path = PACKPATH
                assert osp.exists(path) and osp.isdir(path)
            except:
                path = ''
            src = osp.join(path, "%s%s.json" % (self.__facility.get('code'), OCFGFILE))
        cfg = super(TypeFacility,self).loads(src=src, **kwargs)
        if 'type' not in cfg.keys():
            cfg.update({'type': self.__facility})
        return cfg
    
    #/************************************************************************/
    #def load(self, src=None, **kwargs):
    #same a super method
    #    super(TypeFacilty,self).load(self, src=src, **kwargs)
    
    #/************************************************************************/
    def dump(self, dest=None, **kwargs):
        """Saving global configuration variables as metadata into default config file.
        """
        if dest is None:
            try:
                path = PACKPATH
                assert osp.exists(path) and osp.isdir(path)
            except:
                path = ''
            dest = osp.join(path, "%s%s.json" % (self.__facility.get('code'), OCFGFILE))
        super(TypeFacility,self).dump(dest=dest, **kwargs)


#%%
#==============================================================================
# program run when loading the module
#==============================================================================

for __fac in list(FACILITIES.keys()):
    __ffac = FACILITIES[__fac]['code']
    # if the variable OCFGDATA is set already, we assume this doesnt need to be
    # reloaded. To force it, use the config.load function above.
    try:
        assert OCFGDATA is not None
    except: # NameError
        pass
    else:
        try:
            assert OCFGDATA.get(__fac) not in ({},None)
        except:
            pass
        else:
            continue
    # it has to be loaded/created then...
    try:
        __path = PACKPATH
        assert osp.exists(__path) and osp.isdir(__path)
    except:
        __path = ''
    __cfgfile = osp.join(__path, "%s%s.json" % (__ffac, OCFGFILE))
    try:
        __cfg = TypeFacility(facility=__fac)
        __cfgmeta = __cfg.loads(src=__cfgfile) 
    except:
        __cfgmeta = None
        try:
            assert OCFGDATA.get(__fac, None) not in ({},None)
        except:
            warnings.warn("\n! no config available for facility '%s' !" % __fac)
            continue
        try:
            __cfg = TypeFacility(OCFGDATA.get(__fac), facility=__fac)
            __cfg.dump(dest=__cfgfile)
        except:
            warnings.warn("\n! no config saved for facility '%s' !" % __fac)            
        else:
            warnings.warn("\n! config file for facility '%s' will be created !" % __fac)
    else:
        warnings.warn("\n! loading config data for facility '%s' !" % __fac)
        OCFGDATA[__fac] = __cfgmeta.copy()

del(__THISFILE, __OCFGDATA, __fac, __ffac)
try:
    del(__path, __cfg, __cfgfile)
except: pass