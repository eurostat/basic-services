#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. __init__

Initiatlisation module for integration and formatting of data on health care
services
"""

# *credits*:      `gjacopo <gjacopo@ec.europa.eu>`_ 
# *since*:        Sun Mar 29 16:21:29 2020

from os import path as __osp

__basename          = 'hcs'

__packages          = ['numpy', 'pandas', 'json', 
                       'geopy', 'geojson', 'happygisco', 'pyproj', 
                       'googletrans']

__all__             = ['%s%s' % (a,__basename) for a in ['base' , 'all']]

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

__all_countries     = "EU28"
    
COUNTRIES           = __countries[__all_countries]

__thisdir = __osp.dirname(__file__)

for __cc in COUNTRIES:
    __basesrc = '%s%s' % (__cc, __basename) 
    __fsrc = '%s.py' % __basesrc 
    try:
        if __osp.exists(__osp.join(__thisdir, __fsrc)):
            __all__.append(__basesrc)   
    except:
        pass
    __fmeta = '%smeta.json' % __cc
    try:
        if __osp.exists(__osp.join(__thisdir, __fmeta)):
            pass
    except:
        pass
