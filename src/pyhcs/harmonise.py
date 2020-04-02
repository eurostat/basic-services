#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _harmonise

Module implementing the systematic formatting of data about healthcare services
from all member states. 
    
**Dependencies**

*require*:      :mod:`os`, :mod:`sys`, :mod:`collections`, :mod:`json`, :mod:`sys`

*optional*:     :mod:`importlib`, :mod:`importlib`

*call*:         :mod:`pyhcs.config`, :mod:`pyhcs.base`         

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
    warnings.warn('module importlib missing')
    # import_module = lambda mod: exec('from %s import %s' % mod.split('.'))
    import_module = lambda _mod, pack: exec('from %s import %s' % (pack, _mod.split('.')[1])) or None

from pyhcs import PACKNAME, BASENAME, COUNTRIES#analysis:ignore
from pyhcs.config import OCONFIGNAME#analysis:ignore
from pyhcs.base import IMETANAME, MetaHCS, hcsFactory#analysis:ignore

__thisdir = osp.dirname(__file__)


#%% 
#==============================================================================
# Function __harmonise
#==============================================================================
def __harmonise(metadata, **kwargs):
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
    opt_load = kwargs.pop("opt_load", {})        
    hcs.load_source(**opt_load)
    opt_prep = kwargs.pop("opt_prep", {})        
    hcs.prepare_data(**opt_prep)
    opt_format = kwargs.pop("opt_format", {})        
    hcs.format_data(**opt_format)
    opt_save = kwargs.pop("opt_save", {'geojson': {}, 'csv': {}})        
    hcs.save_data(fmt='geojson', **opt_save.get('geojson',{}))
    hcs.save_data(fmt='csv',**opt_save.get('csv',{}))
    # hcs.save_meta(fmt='json')

#%% 
#==============================================================================
# Function harmoniseOneCountry
#==============================================================================

def harmoniseCountry(country=None, coder=None, **kwargs):
    """Generic harmonisation function.
    
        >>> harmonise.harmoniseCountry(country, coder, **kwargs)
    """
    if country is None:
        country = list(COUNTRIES.values())
    if isinstance(country, Sequence):
        for ctry in country:
            try:
                harmoniseCountry(country=ctry, coder=coder, **kwargs) 
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
        # import_module('%s.%s' % (PACKNAME,modname) )
        imp = import_module('.%s' % modname, PACKNAME)
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
        if imp is not None:
            # assert 'CC' in dir(imp)
            CC = getattr(imp, 'CC', None)
        else:
            exec('CC = %s.CC' % modname)
    except:
        warnings.warn('global variable CC not set - use default')
    try:
        if imp is not None:
            # assert 'METADATA' in dir(imp)
            METADATA = getattr(imp, 'METADATA', None)
        else:
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
        kwargs.update({'coder': coder, 'country' : {'code': CC or country}})
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

