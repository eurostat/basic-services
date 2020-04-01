#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _allhcs

Module implementing the systematic formatting of data about healthcare services
from all member states. 
    
**Dependencies**

*require*:      :mod:`os`, :mod:`sys`

*optional*:     :mod:`A`

*call*:         :mod:`A`         

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Tue Mar 31 22:11:38 2020

#%%                

from os import path as osp
from sys import modules as sysmod#analysis:ignore
import warnings#analysis:ignore

from collections import Mapping, Sequence
from six import string_types

try:
    import simplejson as json
except:
    import json#analysis:ignore
    
try:
    from importlib import import_module
except:
    import_module = None#analysis:ignore
    warnings.warn('module importlib missing')

try:    
    import modulefinder
except: 
    modulefinder = None#analysis:ignore
    warnings.warn('module modulefinder missing')

from pyhcs import PACKNAME, BASENAME, COUNTRIES#analysis:ignore
from pyhcs.base import IMETANAME, MetaHCS, hcsFactory#analysis:ignore
from pyhcs.config import OCONFIGNAME#analysis:ignore

__thisdir = osp.dirname(__file__)


#%% 
#==============================================================================
# Function __harmonise
#==============================================================================
def __harmonise(metadata, **kwargs):
    """Generic harmonisation function
    """
    try:
        assert isinstance(metadata,(MetaHCS,Mapping))  
    except:
        raise TypeError('wrong input metadata')
    try:
        HCS = hcsFactory(metadata, **kwargs)
    except:
        raise IOError('impossible create specific country class')
    try:
        hcs = HCS()
    except:
        raise IOError('impossible create specific country instance')
    else:
        hcs.load_source()
        hcs.prepare_data()
        hcs.format_data()
        hcs.save_data(fmt='geojson')
        hcs.save_data(fmt='csv')
        # hcs.save_meta(fmt='json')

#%% 
#==============================================================================
# Function harmoniseOneCountry
#==============================================================================

def harmoniseCountry(country=None, coder=None):
    if country is None:
        country = list(COUNTRIES.values())
    if isinstance(country, Sequence):
        for ctry in country:
            try:
                harmoniseCountry(country=ctry, coder=coder) 
            except:
                continue
        return
    elif not isinstance(country, string_types):
        raise TypeError('wrong type for input country code - must the ISO 2-letter string')
    elif not country in COUNTRIES.values():
        raise IOError('country code not recognised - must a code of the %s area' % list(COUNTRIES.keys())[0])
    if not(coder is None or isinstance(coder,string_types) or isinstance(coder,Mapping)):
        raise TypeError('coder type not recognised - must be a dictionary or a single string')
    CC, METADATA = None, {}
    # generic name
    ccname = '%s%s' % (country, BASENAME) 
    # load country-dedicated module wmmhen available 
    fname = '%s.py' % ccname 
    modname = ccname
    try:
        assert osp.exists(osp.join(__thisdir, fname))
        exec('from %s import %s' % (PACKNAME,modname))
    except AssertionError:
        warnings.warn('no country py-file %s found - will proceed without' % fname)
    except ImportError:
        warnings.warn('no country py-module %s found - will proceed without' % modname)
    except:
        raise ImportError('no country py-module %s loaded' % modname)
    else:
        warnings.warn('country py-module %s found' % modname)
        try:
            exec('assert %s in sysmod.values()' % modname)
        except:
            raise ImportError('country py-module %s not loaded correctly' % modname)
    try:
        exec('CC = %s.CC' % modname)
    except:
        warnings.warn('global variable CC not set - use default')
        CC = country
    try:
        exec('METADATA = %s.METADATA' % modname)
    except:
        warnings.warn('no default metadata dictionary available')
    else:
        warnings.warn('default hard-coded metadata dictionary found')
    try:
        exec('harmonise = %s.harmonise' % modname)
    except:
        warnings.warn('generic formatting/harmonisation methods used')
    else:
        warnings.warn('country-specific formatting/harmonisation methods used')
        harmonise = __harmonise
    # load country-dedicated metadata when available 
    metadata = None
    metaname = '%s.json' % ccname 
    try:
        assert osp.exists(osp.join(__thisdir, metaname))
        with open(metaname, 'r') as fp: 
            metadata = json.load(fp)
    except (AssertionError,FileNotFoundError):
        warnings.warn('no metadata JSON-file %s found - will proceed without' % metaname)
    else:
        warnings.warn('ad-hoc metadata found - JSON-file %s loaded' % metaname)
    # define the actual metadata: the one loaded, or the default
    metadata = metadata or METADATA
    if metadata in (None,{}):
        raise IOError('no metadata parsed - this cannot end up well')
    else:
        metadata = MetaHCS(metadata)
    try:
        kwargs = {'coder': coder, 'country' : {'code': CC}}
        harmonise(metadata, **kwargs)
    except:
        raise IOError('harmonisation process for country %s failed...' % country)
    else:
        warnings.warn('harmonised data for country %s generated' % country)
        

#%% 
#==============================================================================
# Function run
#==============================================================================

run = harmoniseCountry
    

#%% 
#==============================================================================
# Main function
#==============================================================================

if __name__ == '__main__':
    run()

