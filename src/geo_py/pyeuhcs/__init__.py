#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. __init__

Initialisation module of facility configuration programs.
    
*require*:      :mod:`os`

*call*:         :mod:`pyeudatnat`         

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Mon Apr  6 18:30:09 2020

#%%
from os import path as osp

try:
    from pyeudatnat import BASENAME as __BASENAME, COUNTRIES as __COUNTRIES
except:
    __BASENAME = ''
    __COUNTRIES = {}

__THISFILE          = __file__ # useles...
__THISDIR           = osp.dirname(__THISFILE)

# put here the services managed by this package
FACILITIES          = { 'HCS': 
                        {'code': "hcs", 'name': "Healthcare services"},
                        'Edu': 
                        {'code': "edu", 'name': "Educational facilities"} # 'edu' here for testing since it does not exist yet
                       } 
"""Type of services provided.
"""

#%%

__modules           = [] 
# __all__ = ['%s%s' % (cc,BASENAME) for cc in list(COUNTRIES.values())]
__all__             = ['config', 'harmonise', 'validate']#analysis:ignore

for __fac in FACILITIES.keys():
    __fac = FACILITIES[__fac]['code']
    __path = osp.join(__THISDIR, __fac)
    try:
        assert osp.exists(__path) and osp.isdir(__path)
    except:
        continue
    try:
        assert osp.exists(osp.join(__path,'__init__.py')) and osp.isfile(osp.join(__path,'__init__.py'))
    except:
        continue
    __all__.append(__fac)
    for __cc in __COUNTRIES.keys():
        __src = '%s%s%s' % (__BASENAME, __cc, __fac) 
        __fsrc = '%s.py' % __src 
        try:
            assert osp.exists(osp.join(__path, __fsrc)) and osp.isfile(osp.join(__path, __fsrc))
        except:     pass
        else:
            __modules.append(__src)   
            
try:
    del(__BASENAME, __COUNTRIES)
    del(__fac, __path)
    del(__cc, __src, __fsrc)
except: pass
