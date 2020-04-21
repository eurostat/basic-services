#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _config

.. Links

.. _healthcare: https://github.com/eurostat/healthcare-services
.. |healthcare| replace:: `healthcare services data <healthcare_>`_
.. _GISCO: https://github.com/eurostat/happyGISCO
.. |GISCO| replace:: `GISCO <GISCO_>`_

Configuration module providing with the formatting template for the output 
integrated data on healthcare facilities.

**Dependencies**

*require*:      :mod:`os`, :mod:`warnings`, :mod:`collections`, :mod:`datetime`

*optional*:     :mod:`json`

*call*:         :mod:`pyeudatnat`, :mod:`pyeudatnat.meta`, :mod:`pyeudatnat.base`         

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

from pyeudatnat import COUNTRIES
from pyeudatnat.meta import MetaDat, MetaDatNat
from pyeudatnat.base import datnatFactory

from . import FACILITIES


#%%

__THISFILE      = __file__ 
CONFIGDIR       = osp.dirname(__THISFILE)
CONFIGFILE      = osp.basename(__THISFILE).split('.')[0] # "config"

#%%

__type2name     = lambda t: t.__name__  # lambda t: {v:k for (k,v) in BASETYPE.items()}[t]    


__CONFIGINFO    = dict.fromkeys(list(FACILITIES.keys()), {})
__CONFIGINFO.update( { 
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
[v.update({"category": FACILITIES[k].copy()}) for (k,v) in __CONFIGINFO.items()]

CONFIGINFO         = deepcopy(__CONFIGINFO)


#%%
#==============================================================================
# Class ConfigFacility
#==============================================================================
      
class ConfigFacility(MetaDat):
    """
    """
    
    # CATEGORY = 'HCS' # if only HCS...
    # PROPERTIES = [info['name'] for info in CONFIGINFO[CATEGORY].values()]
    
    #/************************************************************************/
    def __init__(self, *args, **kwargs):
        facility = kwargs.pop('facility', None)
        if isinstance(facility, string_types) and facility in FACILITIES:
            kwargs.update({'category': FACILITIES.get(facility)})
        elif facility is not None:
            kwargs.update({'category': facility})
        super(ConfigFacility, self).__init__(*args, **kwargs)
            
    #/************************************************************************/
    @property
    def facility(self):
        try:
            assert hasattr(self.category, 'code')
            return self.category.get('code') 
        except:
            return self.category
            
    #/************************************************************************/
    def load(self, src=None, **kwargs):
        """Reloading metadata from default config file into global configuration 
        variables.
        """
        if src is None:
            try:
                path = CONFIGDIR
                assert osp.exists(path) and osp.isdir(path) # useless...just in case we change the def
            except:
                path = ''
            src = osp.join(path, "%s%s.json" % (self.facility, CONFIGFILE))
        return super(ConfigFacility,self).load(src = src, **kwargs)
    
    #/************************************************************************/
    def dump(self, dest=None, **kwargs):
        """Saving global configuration variables as metadata into default config file.
        """
        if dest is None:
            try:
                path = CONFIGDIR
                assert osp.exists(path) and osp.isdir(path)
            except:
                path = ''
            dest = osp.join(path, "%s%s.json" % (self.facility, CONFIGFILE))
        super(ConfigFacility,self).dump(dest = dest, **kwargs)


#%%
#==============================================================================
# Class MetaDatNatFacility
#==============================================================================

class MetaDatNatFacility(MetaDatNat):
    """Generic class used to represent country metadata instances as dictionary.
    
        >>> meta = MetaDatNatFacility(**metadata)
    """
    
    PROPERTIES = ['country', 'lang', 'proj', 'file', 'path', 'enc', 'sep', 'columns', 'index']
    #          {'country':{}, 'lang':{}, 'proj':None, 'file':'', 'path':'', 'enc':None, 'sep':',', 'columns':{}, 'index':[]}
    
    #/************************************************************************/
    @classmethod
    def template(cls, facility=None, country=None, **kwargs):
        """"Create a template country metadata file as a JSON file
        
            >>> MetaFacility.template()
        """
        if country is None:
            country = ''
        elif not isinstance(country, string_types):
            raise TypeError("Wrong type for country code '%s' - must be a string" % country)
        if facility is None:
            facility = ''
        elif isinstance(facility, string_types) and facility in FACILITIES:
            facility = FACILITIES.get(facility)
        else:
            raise TypeError("Wrong type for facility type - must be a string" % country)
        as_file = kwargs.pop('as_file', True)
        # dumb initialisation
        temp = dict.fromkeys(cls.PROPERTIES)
        temp.update({ 'country':     {'code': country.upper() or 'CC', 'name': ''},
                      'lang':        {'code': country.lower() or 'cc', 'name': ''},
                      'file':        '%s.csv' % country or 'CC' ,
                      # 'proj':        None,
                      'path':        '../../data/raw/',
                      'enc':         'latin1',
                      'sep':         ';', 
                      'date':        '%d-%m-%Y', 
                      'columns':     [ ],
                      'index':       { }
                      })
        temp['columns'].extend([{country.lower() or 'cc': 'icol1', 'en': 'icol1', 'fr': 'icol1', 'de': 'iSpal1'},
                             {country.lower() or 'cc': 'icol2', 'en': 'icol1', 'fr': 'icol2', 'de': 'iSpal2'}])
        [temp['index'].update({'ocol%s': 'icol%s' % str(i+1)}) for i in [0,1]]
        # create the metadata structure with this dumb template
        template = cls(temp)
        try:
            assert as_file is True
            # save it...somewhere
            dest = osp.join(CONFIGDIR, facility, "%s%s.json" % (country.upper() or 'temp', facility))
            template.save(dest, **kwargs)
        except AssertionError:
            return template
        except:
            raise IOError("Impossible saving template metadata as a file")


#%% 
#==============================================================================
# Function facilityFactory
#==============================================================================
    
def facilityFactory(*args, **kwargs):
    """Generic function to derive a class from the base class :class:`BaseFacility`
    depending on specific metadata and a given geocoder.
    
        >>>  NewFacility = facilityFactory(facility, metadata=None, country=None, coder=None)
        
    Examples
    --------
    
        >>>  NewHCS = facilityFactory(HCS, country=CC1, coder={'Bing', yourkey})
        >>>  NewFacility = facilityFactory(country=CC2, coder='GISCO')
    """    
    # check facility to define output data configuration format
    if args in ((),(None,)):        facility = None
    else:                           facility = args[0]
    facility = facility or kwargs.pop('facility', None)
    try:
        assert facility is None or isinstance(facility, (string_types,Mapping,MetaDat))  
    except AssertionError:
        raise TypeError("Facility type '%s' not recognised - must be a string" % type(facility))
    if facility is None:
        config = {}
    elif isinstance(facility, string_types):
        try:
            config = CONFIGINFO[facility] 
        except AttributeError:
            raise TypeError("Facility string '%s' not recognised - must be in '%s'" % (facility, list(FACILITIES.keys())))
        else:
            config = ConfigFacility(deepcopy(config), facility = facility)
    elif isinstance(facility, Mapping):
        config = ConfigFacility(facility)  
    elif isinstance(facility,ConfigFacility):
        config = facility.copy()
    # kwargs.update({'config': cfgmeta})
    return datnatFactory(config, **kwargs)


#%%
#==============================================================================
# program run when loading the module
#==============================================================================

for __fac in list(FACILITIES.keys()):
    __ffac = FACILITIES[__fac]['code']
    # if the variable OCFGDATA is set already, we assume this doesnt need to be
    # reloaded. To force it, use the config.load function above.
    try:
        assert CONFIGINFO is not None
    except: # NameError
        pass
    else:
        try:
            assert CONFIGINFO.get(__fac) not in ({},None)
        except:
            pass
        else:
            continue
    # it has to be loaded/created then...
    try:
        __path = CONFIGDIR
        assert osp.exists(__path) and osp.isdir(__path)
    except:
        __path = ''
    __cfgfile = osp.join(__path, "%s%s.json" % (__ffac, CONFIGFILE))
    try:
        __cfg = ConfigFacility(facility=__fac)
        __config = __cfg.loads(src=__cfgfile) 
    except:
        __config = None
        try:
            assert CONFIGINFO.get(__fac, None) not in ({},None)
        except:
            warnings.warn("\n! No config available for facility '%s' !" % __fac)
            continue
        try:
            __cfg = ConfigFacility(CONFIGINFO.get(__fac), facility=__fac)
            __cfg.dump(dest=__cfgfile)
        except:
            warnings.warn("\n! No config saved for facility '%s' !" % __fac)            
        else:
            warnings.warn("\n! Configuration file for facility '%s' will be created !" % __fac)
    else:
        warnings.warn("\n! Loading configuration data for facility '%s' !" % __fac)
        CONFIGINFO[__fac] = __config.copy()

del(__THISFILE, __CONFIGINFO, __fac, __ffac)
try:
    del(__path, __cfg, __config, __cfgfile)
except: pass