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

from pyeudatnat import COUNTRIES


PACKNAME            = 'pyeufacility' # this package...
"""Name of this package.
"""

PACKPATH            = osp.dirname(__file__)
"""Path to this package.
"""

# put here the services managed by this package
FACILITIES          = {
    'HCS':  {'code': "hcs", 'name': "Healthcare services"},
    'EDU':  {'code': "edu", 'name': "Educational facilities"},
    'Oth':  {'code': "other", 'name': "Other basic services TBD"}

                       }
"""Type of services provided.
"""

BASENAME            = {k:v['code'] for (k,v) in FACILITIES.items()}

HARMONISE           = 'harmonise'
VALIDATE            = 'validate'

#%%

__all__             = ['config', HARMONISE, VALIDATE]#analysis:ignore


#%%

FACACCESS           = []
CCACCESS            = {__fac:[] for __fac in FACILITIES.keys() if __fac!='Oth'}

for __fac in FACILITIES.keys():
    if __fac=='Oth':    continue
    # for a given facility
    __cfac = FACILITIES[__fac]['code']
    # check facilities' metadata
    __path = PACKPATH
    for __fmt in ['json', 'py']:
        __fsrc = osp.join(__path, '%s.%s' % (__cfac, __fmt))
        try:
            assert osp.exists(__fsrc) and osp.isfile(__fsrc)
        except AssertionError:     pass
        else:
            FACACCESS.append(__fac)
            break
    # check countries' metadata
    __path = osp.join(PACKPATH, __fac)
    try:
        assert osp.exists(__path) and osp.isdir(__path)
    except AssertionError:
        continue
    try:
        __finit = osp.join(__path,'__init__.py')
        assert osp.exists(__finit) and osp.isfile(__finit)
    except AssertionError:
        continue
    __all__.append(__cfac)
    # add metadata files to module
    for __cc in COUNTRIES.keys():
        __src = '%s%s' % (__cc, __cfac)
        for __fmt in ['json', 'py']:
            __fsrc = osp.join(__path, '%s.%s' % (__src, __fmt))
            try:
                assert osp.exists(__fsrc) and osp.isfile(__fsrc)
            except AssertionError:     pass
            else:
                CCACCESS[__fac].append(__cc)
                break

try:
    del(__fac, __cfac, __path)
    del(__cc, __src, __fmt, __fsrc, __finit)
except: pass
