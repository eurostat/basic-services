#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. __init__

Initiatlisation module for integration and formatting of data on health care
services
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Sun Mar 29 16:21:29 2020

# 88""Yb Yb  dP 88  88   dP""b8  dP""b8  
# 88__dP  YbdP  88__88  dP   `"  Yb_
# 88"""   8P    88""88  Yb         "db
# 88     dP     88  88  YboodP   boodP

#%%

from os import path as osp


#%%

PACKNAME            = 'pyhcs' # this package...

BASENAME            = 'hcs'.lower() # whatever we choose, let's make it low...
__basename          = '' # __base

METABASE            = 'meta'

__packages          = ['numpy', 'pandas', 'json', 'datetime', 'geopy', 'geojson', 'happygisco', 'pyproj', 'googletrans']

__modules           = ['config', 'misc', 'base', 'harmonise', 'validate']

__all__             = ['%s%s' % (__,__basename) for __ in __modules]
__all__.extend(['__version__', '__start__', METABASE])

ISOCOUNTRIES        = { ## alpha-2/ISO 3166 codes
                        'BE': 'Belgium',                
                        'EL': 'Greece',                 
                        'LT': 'Lithuania',              
                        'PT': 'Portugal',               
                        'BG': 'Bulgaria',               
                        'ES': 'Spain',                  
                        'LU': 'Luxembourg',             
                        'RO': 'Romania',                
                        'CZ': 'Czechia',                
                        'FR': 'France',                 
                        'HU': 'Hungary',                
                        'SI': 'Slovenia',               
                        'DK': 'Denmark',                
                        'HR': 'Croatia',                
                        'MT': 'Malta',                  
                        'SK': 'Slovakia',               
                        'DE': 'Germany',                
                        'IT': 'Italy',                  
                        'NL': 'Netherlands',            
                        'FI': 'Finland',                
                        'EE': 'Estonia',                
                        'CY': 'Cyprus',                 
                        'AT': 'Austria',                
                        'SE': 'Sweden',                 
                        'IE': 'Ireland',                
                        'LV': 'Latvia',                 
                        'PL': 'Poland',                 
                        'UK': 'United Kingdom',         
                        'IS': 'Iceland',                
                        'NO': 'Norway',                 
                        'CH': 'Switzerland',            
                        'LI': 'Liechtenstein',          
                        'ME': 'Montenegro',             
                        'MK': 'North Macedonia',        
                        'AL': 'Albania',                
                        'RS': 'Serbia',                 
                        'TR': 'Turkey',                 
                        'XK': 'Kosovo',                 
                        'BA': 'Bosnia and Herzegovina', 
                        'MD': 'Moldova',                
                        'AM': 'Armenia',                
                        'BY': 'Belarus',                
                        'GE': 'Georgia',                
                        'AZ': 'Azerbaijan',             
                        'UA': 'Ukraine',                
                        }
# ISOCODECTRIES = dict(map(reversed, ISOCOUNTRIES.items())) # {v:k for (k,v) in ISOCOUNTRIES.items()}

__countries         = { "EU27_2020":
                            ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "EL", "ES", "FR", "HR", "IT", "CY", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "FI", "SE"
                             ],
                        "EU27_2019": 
                            ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "EL", "ES", "FR", "HR", "IT", "CY", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "FI", "SE"
                            ],
                        "EU28": 
                            ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "EL", "ES", "FR", "HR", "IT", "CY", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "FI", "SE", "UK"
                             ],
                        "EU27_2009": 
                            ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "EL", "ES", "FR", "IT", "CY", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "FI", "SE", "UK" 
                             ], 
                        "EFTA": 
                            ["CH", "IS", "NO", "LI"
                             ]
                        }    
__territories       = { }

__area              = ["EU28", "EFTA"]
__area.extend(__territories.keys())
#EUCOUNTRIES         = {a:__countries[a] for a in __area}
#EUCOUNTRIES.update({t:__territories[t] for t in __territories})
EUCOUNTRIES         = dict((k,v) for (k,v) in ISOCOUNTRIES.items() for a in __area if k in __countries[a])
EUCOUNTRIES.update(dict((k,v) for (k,v) in ISOCOUNTRIES.items() for t in __territories if k in __territories[t]))

__thisdir           = osp.dirname(__file__)

for __cc in EUCOUNTRIES:
    __basesrc = '%s%s' % (__cc, BASENAME) 
    __fsrc = '%s.py' % __basesrc 
    try:
        if osp.exists(osp.join(__thisdir, __fsrc)):
            __all__.append(__basesrc)   
    except:
        pass

