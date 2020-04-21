#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. __init__

Initialisation module of country programmes for HCS configuration loading.
    
**Dependencies**

*require*:      :mod:`os`

*call*:         :mod:`pyeudatnat`         

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Mon Apr 20 14:36:59 2020

#%%
from os import path as osp

__FAC = 'hcs'

try:
    from pyeudatnat import BASENAME as __BASENAME, COUNTRIES as __COUNTRIES
except:
    __BASENAME = ''
    __COUNTRIES = {}

# __all__ = ['%s%s' % (__BASENAME, __cc, __FAC) for cc in list(COUNTRIES.values())]
__all__ = [ ]#analysis:ignore

for __cc in __COUNTRIES.keys():
    __src = '%s%s%s' % (__BASENAME, __cc, __FAC) 
    __fsrc = '%s.py' % __src 
    try:
        assert osp.exists( __fsrc) and osp.isfile(__fsrc)
    except:     pass
    else:
        __all__.append(__src)   
          
try:
    del(__FAC,__BASENAME, __COUNTRIES)
    del(__cc, __src, __fsrc)
except: pass
