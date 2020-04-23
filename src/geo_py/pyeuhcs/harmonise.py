#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _harmonise

Module implementing the systematic formatting of data about healthcare services
from all member states. 
    
**Dependencies**

*require*:      :mod:`os`, :mod:`sys`, :mod:`collections`, :mod:`json`, :mod:`sys`

*optional*:     :mod:`importlib`, :mod:`importlib`

*call*:         :mod:`pyeudatnat`, :mod:`pyeuhcs`, :mod:`pyeuhcs.config`         

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
    warnings.warn('\n! inline command deactivated !')
        
try:
    from importlib import import_module
except:
    warnings.warn('\n! module importlib missing !')
    # import_module = lambda mod: exec('from %s import %s' % mod.split('.'))
    import_module = lambda _mod, pack: exec('from %s import %s' % (pack, _mod.split('.')[1])) or None

from pyeudatnat import COUNTRIES
from pyeudatnat.io import Json

from pyeuhcs import PACKNAME, BASENAME, METANAME, HARMNAME, PREPNAME, FACILITIES
from pyeuhcs.config import MetaDatNatFacility, facilityFactory

__THISFACILITY  = 'HCS'
__THISDIR       = osp.dirname(__file__)
__METADIR       = FACILITIES[__THISFACILITY].get('code')
__fccname       = lambda cc: "%s%s" % (cc, BASENAME[__THISFACILITY])


#%% 
#==============================================================================
# Function __harmoniseData, __harmoniseMetaData
#==============================================================================

def __harmoniseData(metadata, **kwargs):
    try:
        assert isinstance(metadata,(Mapping, MetaDatNatFacility))  
    except:
        raise TypeError("Wrong input metadata for '%s' facility" % __THISFACILITY)
    #else:
    #    metadata = MetaDatNatFacility(metadata)
    on_disk = kwargs.pop('on_disk', True)
    try:
        assert isinstance(on_disk,bool)
    except:
        raise TypeError("Wrong ON_DISK flag")
    f_prep = kwargs.pop('met_prep')       
    try:
        assert f_prep is None or callable(f_prep) is True
    except:
        raise TypeError("Wrong option MET_PREP - 'prepare_data' method not recognised")
    opt_prep = kwargs.pop("opt_prep", {})        
    opt_load = kwargs.pop("opt_load", {})        
    opt_format = kwargs.pop("opt_format", {})        
    opt_save = kwargs.pop("opt_save", {'geojson': {}, 'csv': {}})        
    try:
        assert isinstance(opt_load,Mapping) and isinstance(opt_prep,Mapping) \
            and isinstance(opt_format,Mapping) and isinstance(opt_save,Mapping) 
    except:
        raise TypeError("Wrong additional options")
    try:
        Facility = facilityFactory(facility = __THISFACILITY, meta = metadata, **kwargs)
    except:
        raise IOError("Impossible to create specific country class")
    else:
        if callable(f_prep):     
            setattr(Facility, PREPNAME, f_prep) # Facility.prepare_data = f_prep
    try:
        facility = Facility()
    except:
        raise IOError("Impossible to create specific facility instance")
    facility.load_data(**opt_load)
    getattr(facility, PREPNAME)(**opt_prep) # facility.prepare_data(**opt_prep)
    facility.format_data(**opt_format)
    if on_disk is True:
        facility.dump_data(fmt='geojson', **opt_save.get('geojson',{}))
        facility.dump_data(fmt='csv',**opt_save.get('csv',{}))
    # facility.dump_meta(fmt='json', **opt_save.get('json',{})) 
    return facility


#%% 
#==============================================================================
# Function harmoniseOneCountry
#==============================================================================

def harmoniseCountry(country=None, coder=None, **kwargs):
    """Generic harmonisation function.
    
        >>> harmonise.harmoniseCountry(country=None, coder=None, **kwargs)
    """
    if country is None:
        country = list(COUNTRIES.keys())
    if not isinstance(country, string_types) and isinstance(country, Sequence):
        for ctry in country:
            try:
                harmoniseCountry(country=ctry, coder=coder, **kwargs) 
            except:
                continue
        return
    elif not isinstance(country, string_types):
        raise TypeError("Wrong type for input country code - must be the ISO 2-letter string")
    elif not country in COUNTRIES.keys():
        raise IOError("Country code not recognised - must be a code of the '%s' area(s)" % list(COUNTRIES.keys()))
    if not(coder is None or isinstance(coder,string_types) or isinstance(coder,Mapping)):
        raise TypeError("Coder type not recognised - must be a dictionary or a single string")
    CC, METADATNAT = None, {}
    # generic name
    ccname = __fccname(country) # '%s%s' % (country,BASENAME.get(__THISFACILITY)) 
    # load country-dedicated module wmmhen available 
    modname = ccname
    fname = '%s.py' % ccname 
    try:
        assert osp.exists(osp.join(__THISDIR, __METADIR, fname))
        # import_module('%s.%s' % (PACKNAME,modname) )
        imp = import_module('.%s' % modname, '%s.%s' % (PACKNAME,__METADIR))
    except AssertionError:
        warnings.warn("\n! No country py-file '%s' found - will proceed without !" % fname)
    except ImportError:
        warnings.warn("\n! No country py-module '%s' found - will proceed without !" % modname)
    except:
        raise ImportError("No country py-module '%s' loaded" % modname)
    else:
        warnings.warn("\n! Country py-module '%s' found !" % imp.__name__)
        try:
            assert imp in sysmod.values()
        except:
            raise ImportError("Country py-module '%s' not loaded correctly" % imp.__name__)
    try:
        # assert 'CC' in dir(imp)
        CC = getattr(imp, 'CC', None)
    except:
        warnings.warn("\n! Global variable 'CC' not set - use default !")
    try:
        # assert METANAME in dir(imp)
        METADATNAT = getattr(imp, METANAME, None)
        assert METADATNAT is not None
    except:
        warnings.warn("\n! No default metadata dictionary '%s' available !" % METANAME)
    else:
        warnings.warn("\n! Default hard-coded metadata dictionary '%s' found !" % METANAME)
    try:
        # assert 'harmonise' in dir(imp)
        harmonise = getattr(imp, HARMNAME, None)
        assert harmonise is not None
    except:
        warnings.warn('\n! Generic formatting/harmonisation methods used !')
        harmonise = __harmoniseData
    else:
        warnings.warn('\n! Country-specific formatting/harmonisation methods used !')
    try:
        # assert 'prepare_data' in dir(imp)
        prepare_data = getattr(imp, PREPNAME, None) # getattr(imp, 'prepare_data', None)
        assert prepare_data is not None
    except:
        # warnings.warn('! no data preparation method used !')
        prepare_data = None # anyway...
    else:
        warnings.warn('\n! country-specific data preparation method loaded !')
    # load country-dedicated metadata when available 
    metadata = None
    metafname = '%s.json' % ccname 
    try:
        metafname = osp.join(__THISDIR, __METADIR, metafname)
        assert osp.exists(metafname)
        with open(metafname, 'r') as fp: 
            metadata = Json.load(fp)
    except (AssertionError,FileNotFoundError):
        warnings.warn("\n! No metadata JSON-file '%s' found - will proceed without !" % metafname)
    else:
        warnings.warn("! Ad-hoc metadata found - JSON-file '%s' loaded !" % metafname)
    # define the actual metadata: the one loaded, or the default
    metadata = metadata or METADATNAT
    if metadata in (None,{}):
        raise IOError('No metadata parsed - this cannot end up well')
    try:
        kwargs.update({'coder': coder, 'country' : {'code': CC or country},
                       'met_prep': prepare_data})
                        # 'opt_load': {}, 'opt_fmt': {}, 'opt_save': {}
        res = harmonise(metadata, **kwargs) 
    except:
        raise IOError("Harmonisation process for country '%s' failed..." % country)
    else:
        warnings.warn("\n! Harmonised data for country '%s' generated !" % country)
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
        warnings.warn('\n!!!  ERROR: data file not created !!!')
    else:
        warnings.warn('\n!  OK: data file correctly created !')

#try:
#    del(__THISFACILITY, __THISDIR, __METADIR, __fccname)
#except:
#    pass

if __name__ == '__main__':
    __main()

