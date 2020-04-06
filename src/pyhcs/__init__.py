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

__packages          = ['numpy', 'pandas', 'json', 'datetime', 'geopy', 'geojson', 'happygisco', 'pyproj', 'googletrans']

__modules           = ['__start', 'config', 'base' , 'harmonise']

__all__             = ['%s%s' % (__,__basename) for __ in __modules]

__countries         =  {"EU27_2020": 
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
                             ] 
                        }    
__territories       = {}
__area              = "EU28"
COUNTRIES           = {__area: __countries[__area]}

__thisdir = osp.dirname(__file__)

for __cc in COUNTRIES[__area]:
    __basesrc = '%s%s' % (__cc, BASENAME) 
    __fsrc = '%s.py' % __basesrc 
    try:
        if osp.exists(osp.join(__thisdir, __fsrc)):
            __all__.append(__basesrc)   
    except:
        pass

