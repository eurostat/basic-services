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
    from optparse import OptionParser
except ImportError:
    warnings.warn('! inline command deactivated !')

try:
    import simplejson as json
except:
    try:
        import json#analysis:ignore
    except ImportError:
        class json:
            def dump(arg):  
                return '%s' % arg
            def load(arg):  
                with open(arg,'r') as f:
                    return f.read()
        
try:
    from importlib import import_module
except:
    warnings.warn('! module importlib missing !')
    # import_module = lambda mod: exec('from %s import %s' % mod.split('.'))
    import_module = lambda _mod, pack: exec('from %s import %s' % (pack, _mod.split('.')[1])) or None

from pyhcs import PACKNAME, BASENAME, METABASE, COUNTRIES#analysis:ignore
from pyhcs.config import OCFGNAME#analysis:ignore
from pyhcs.base import IMETANAME, MetaHCS, BaseHCS, hcsFactory#analysis:ignore

__THISDIR       = osp.dirname(__file__)
__CCNAME        = lambda cc: "%s%s" % (cc,BASENAME)


#%% 
#==============================================================================
# Function __harmoniseData, __harmoniseMetaData
#==============================================================================

def __harmoniseData(hcs, **kwargs):
    as_file = kwargs.pop('as_file', True)
    try:
        assert isinstance(hcs, BaseHCS)
    except:
        raise TypeError('wrong input HCS data')
    opt_load = kwargs.pop("opt_load", {})        
    hcs.load_data(**opt_load)
    opt_prep = kwargs.pop("opt_prep", {})        
    hcs.prepare_data(**opt_prep)
    opt_format = kwargs.pop("opt_format", {})        
    hcs.format_data(**opt_format)
    if as_file is False:
        return
    opt_save = kwargs.pop("opt_save", {'geojson': {}, 'csv': {}})        
    hcs.save_data(fmt='geojson', **opt_save.get('geojson',{}))
    hcs.save_data(fmt='csv',**opt_save.get('csv',{}))
    # hcs.save_meta(fmt='json', **opt_save.get('json',{})) 
    return 

def __harmoniseMetaData(metadata, **kwargs):
    try:
        assert isinstance(metadata,(MetaHCS,Mapping))  
    except:
        raise TypeError('wrong input metadata')
    else:
        metadata = MetaHCS(metadata)
    try:
        HCS = hcsFactory(metadata, **kwargs)
    except:
        raise IOError('impossible create specific country class')
    fprep = kwargs.pop('met_prep')
    try:
        assert fprep is None or callable(fprep) is True
    except:
        raise IOError('prepare method not recognised')
    else:
        if callable(fprep):     
            HCS.prepare_data = fprep
    try:
        hcs = HCS()
    except:
        raise IOError('impossible create specific country instance')
    __harmoniseData(hcs, **kwargs)
    return hcs


#%% 
#==============================================================================
# Function harmoniseOneCountry
#==============================================================================

def harmoniseCountry(country=None, coder=None, **kwargs):
    """Generic harmonisation function.
    
        >>> harmonise.harmoniseCountry(country, coder, **kwargs)
    """
    if country is None:
        country = list(COUNTRIES.values())[0]
    if not isinstance(country, string_types) and isinstance(country, Sequence):
        for ctry in country:
            try:
                harmoniseCountry(country=ctry, coder=coder, **kwargs) 
            except:
                continue
        return
    elif not isinstance(country, string_types):
        raise TypeError('wrong type for input country code - must be the ISO 2-letter string')
    elif not country in list(COUNTRIES.values())[0]:
        raise IOError('country code not recognised - must be a code of the %s area' % list(COUNTRIES.keys())[0])
    if not(coder is None or isinstance(coder,string_types) or isinstance(coder,Mapping)):
        raise TypeError('coder type not recognised - must be a dictionary or a single string')
    CC, METADATA = None, {}
    # generic name
    ccname = __CCNAME(country) # '%s%s' % (country, BASENAME) 
    # load country-dedicated module wmmhen available 
    modname = ccname
    fname = '%s.py' % ccname 
    try:
        assert osp.exists(osp.join(__THISDIR, METABASE, fname))
        # import_module('%s.%s' % (PACKNAME,modname) )
        imp = import_module('.%s' % modname, '%s.%s' % (PACKNAME,METABASE))
    except AssertionError:
        warnings.warn('! no country py-file %s found - will proceed without !' % fname)
    except ImportError:
        warnings.warn('! no country py-module %s found - will proceed without !' % modname)
    except:
        raise ImportError('no country py-module %s loaded' % modname)
    else:
        warnings.warn('! country py-module %s found !' % imp.__name__)
        try:
            assert imp in sysmod.values()
        except:
            raise ImportError('country py-module %s not loaded correctly' % imp.__name__)
    try:
        # assert 'CC' in dir(imp)
        CC = getattr(imp, 'CC', None)
    except:
        warnings.warn('! global variable CC not set - use default !')
    try:
        # assert 'METADATA' in dir(imp)
        METADATA = getattr(imp, 'METADATA', None)
        assert METADATA is not None
    except:
        warnings.warn('! no default metadata dictionary available !')
    else:
        warnings.warn('! default hard-coded metadata dictionary found !')
    try:
        # assert 'harmonise' in dir(imp)
        harmonise = getattr(imp, 'harmonise', None)
        assert harmonise is not None
    except:
        warnings.warn('! generic formatting/harmonisation methods used !')
        harmonise = __harmoniseMetaData
    else:
        warnings.warn('! country-specific formatting/harmonisation methods used !')
    try:
        # assert 'prepare_data' in dir(imp)
        prepare_data = getattr(imp, 'prepare_data', None)
        assert prepare_data is not None
    except:
        # warnings.warn('! no data preparation method used !')
        prepare_data = None # anyway...
    else:
        warnings.warn('! country-specific data preparation method loaded !')
    # load country-dedicated metadata when available 
    metadata = None
    metaname = '%s.json' % ccname 
    try:
        metaname = osp.join(__THISDIR, METABASE, metaname)
        assert osp.exists(metaname)
        with open(metaname, 'r') as fp: 
            metadata = json.load(fp)
    except (AssertionError,FileNotFoundError):
        warnings.warn('! no metadata JSON-file %s found - will proceed without !' % metaname)
    else:
        warnings.warn('! ad-hoc metadata found - JSON-file %s loaded ! ' % metaname)
    # define the actual metadata: the one loaded, or the default
    metadata = metadata or METADATA
    if metadata in (None,{}):
        raise IOError('no metadata parsed - this cannot end up well')
    kwargs.update({'coder': coder, 'country' : {'code': CC or country},
                   'met_prep': prepare_data})
                    # 'opt_load': {}, 'opt_fmt': {}, 'opt_save': {}        
    try:
        kwargs.update({'coder': coder, 'country' : {'code': CC or country},
                       'met_prep': prepare_data})
                        # 'opt_load': {}, 'opt_fmt': {}, 'opt_save': {}
        res = harmonise(metadata, **kwargs) 
    except:
        raise IOError('harmonisation process for country %s failed...' % country)
    else:
        warnings.warn('! harmonised data for country %s generated !' % country)
    return res
        

#%% 
#==============================================================================
# Main functions
#==============================================================================

run = harmoniseCountry

def __main():
    """Parse and check the command line with default arguments.
    """
    parser = OptionParser(                                                  \
        description=                                                        \
    """Harmonise input national data on health care services.""",
        usage=                                                              \
    """usage:         harmonise [options] <code> 
    <code> :          country code."""                                      \
                        )
    
    #parser.add_option("-c", "--cc", action="store", dest="cc",
    #                  help="country ISO-code.",
    #                  default=None)
    parser.add_option("-c", "--geocoder", action="store", dest="coder",
                      help="geocoder.",
                      default=None)
    parser.add_option("-k", "--geokey", action="store", dest="key",
                      help="geocoder key.",
                      default=None)
    #parser.add_option("-r", "--dry-run", action="store_true", dest="dryrun", 
    #                  help="run the script without creating the file")
    (opts, args) = parser.parse_args()

    opts.test=1
    
    # define the input metadata file (base)name
    if not args in (None,()):
        country = args[0]
    else:
        # parser.error("country name is required.")
        country = list(COUNTRIES.values())[0]
        
    coder = opts.coder
    if isinstance(coder, string_types): 
        coder = {coder: opts.key}
    elif coder is not None:
        parser.error("country name is required.")
    
    # run the generator
    try:
        run(country, coder)
    except IOError:
        warnings.warn('!!!  ERROR: data file not created !!!')
    else:
        warnings.warn('!  OK: data file correctly created !')

if __name__ == '__main__':
    __main()

