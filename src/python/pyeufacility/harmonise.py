#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _harmonise

Module implementing the systematic formatting of data about healthcare services
from all member states.

**Dependencies**

*require*:      :mod:`os`, :mod:`sys`, :mod:`collections`, :mod:`json`, :mod:`sys`

*optional*:     :mod:`importlib`, :mod:`importlib`

*call*:         :mod:`pyeudatnat`, :mod:`pyeufacility`, :mod:`pyeufacility.config`

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_
# *since*:        Tue Mar 31 22:11:38 2020

#%%

from os import path as osp
import inspect
from sys import modules as sysmod#analysis:ignore
import logging

from collections import Mapping, Sequence
from six import string_types

try:
    from optparse import OptionParser
except ImportError:
    logging.warning('\n! inline command deactivated !')

try:
    from importlib import import_module
except:
    logging.warning('\n! module importlib missing !')
    # import_module = lambda mod: exec('from %s import %s' % mod.split('.'))
    import_module = lambda _mod, pack: exec('from %s import %s' % (pack, _mod.split('.')[1])) or None

from pyeudatnat import COUNTRIES, AREAS
from pyeudatnat.io import Json
from pyeudatnat.base import PROCESSES

from pyeufacility import PACKNAME, BASENAME, HARMONISE, FACILITIES
from pyeufacility.config import MetaDatNatFacility, facilityFactory

__THISDIR       = osp.dirname(__file__)


#%%
#==============================================================================
# Function __harmoniseData
#==============================================================================

def __harmoniseData(facility, metadata, **kwargs):
    try:
        assert isinstance(metadata,(Mapping, MetaDatNatFacility))
    except:
        raise TypeError("Wrong input metadata for '%s' facility" % facility)
    #else:
    #    metadata = MetaDatNatFacility(metadata)
    dest = kwargs.pop("dest", None)
    try:
        assert dest is None or isinstance(dest, string_types)
    except:
        raise TypeError("Wrong DEST file name")
    on_disk = kwargs.pop('on_disk', None)
    try:
        assert on_disk is None or isinstance(on_disk, bool)
    except:
        raise TypeError("Wrong ON_DISK flag")
    # check dictionary of options
    options = kwargs.pop('options', {})
    try:
        assert isinstance(options, Mapping)
        assert all(o is None or isinstance(o,Mapping) for o in options.values())
    except:
        raise TypeError("Wrong format for OPTIONS - must be a dictionary (of dictionaries)")
    else:
        try:
            assert set(list(options.keys())).difference(PROCESSES) == set()
        except:
            raise IOError("Wrong keys for OPTIONS - must be any from the list '%s'" % PROCESSES)
    # check dictionary of methods
    methods = kwargs.pop('methods', {})
    try:
        assert isinstance(methods, Mapping)
        # assert all(callable(m) for m in methods.values())
    except:
        raise TypeError("Wrong format for METHODS - must be a dictionary (of callables)")
    else:
        try:
            assert set(list(methods.keys())).difference(PROCESSES) == set()
        except:
            raise IOError("Wrong keys for METHODS - must be any from the list '%s'" % PROCESSES)
    # create facility
    try:
        Facility = facilityFactory(cat = facility,
                                   meta = metadata,
                                   **kwargs)
    except:
        raise IOError("Impossible to create specific country class")
    # check wether some processes have been parsed
    for proc, proc_data in methods.items():
        try:
            assert callable(proc_data)
        except:
            raise TypeError("Wrong option '%s': '%s_data' method not recognised" % (proc,proc))
        else:
            # for instance = Facility.prepare_data = prepare_data
            setattr(Facility, '%s_data' % proc, proc_data)
    # create an country instance
    try:
        natFacility = Facility()
    except:
        raise IOError("Impossible to create specific facility instance")
    # process...
    # fetch the data
    try:
        natFacility.fetch_data(**options.get('fetch',{}))
    except:     pass
    # load the actual data
    natFacility.load_data(**options.get('load',{}))
    # prepare/update the data
    if inspect.isclass(natFacility.prepare_data):
        natFacility.prepare_data()(natFacility, **options.get('prepare',{}))
    elif callable(natFacility.prepare_data): # inspect.ismethod(natFacility.prepare_data)
        natFacility.prepare_data(**options.get('prepare',{}))
    # geolocalise the data
    natFacility.locate_data(**options.get('locate',{}))
    # format/harmonise the data
    natFacility.format_data(**options.get('format',{}))
    # save the data
    if on_disk is None:
        return natFacility
    elif on_disk is False:
        return natFacility.dump_data(**options.get('dump',{}))
    else:
        natFacility.save_data(dest = dest, **options.get('save',{}))
        return natFacility


#%%
#==============================================================================
# Function harmoniseCountryService
#==============================================================================

def harmoniseCountryService(facility, country = None, coder = None, **kwargs):
    """Generic harmonisation function.

        >>> harmonise.harmoniseCountryService(facility, country = None, coder = None, **kwargs)
    """
    #if facility is None:
    #    facility = list(FACILITIES.keys())
    if not isinstance(facility, string_types):
        raise TypeError("Wrong type for input service - must be the facility type")
    elif not facility in FACILITIES.keys():
        raise IOError("Service type not recognised - must be a string in the list '%s'" % list(FACILITIES.keys()))
    if country is None:
        country = list(COUNTRIES.keys())
    if not isinstance(country, string_types) and isinstance(country, Sequence):
        for ctry in country:
            try:
                harmoniseCountryService(facility, country=ctry, coder=coder, **kwargs)
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
    metadir = FACILITIES[facility].get('code')
    # generic name
    ccname = "%s%s" % (country, BASENAME.get(facility,''))
    # load country-dedicated module wmmhen available
    modname = ccname
    fname = '%s.py' % ccname
    try:
        assert osp.exists(osp.join(__THISDIR, metadir, fname))
        # import_module('%s.%s' % (PACKNAME,modname) )
        imp = import_module('.%s' % modname, '%s.%s' % (PACKNAME, metadir))
    except AssertionError:
        logging.warning("\n! No country py-file '%s' found - will proceed without !" % fname)
    except ImportError:
        logging.warning("\n! No country py-module '%s' found - will proceed without !" % modname)
    except:
        raise ImportError("No country py-module '%s' loaded" % modname)
    else:
        logging.warning("\n! Country py-module '%s' found !" % imp.__name__)
        try:
            assert imp in sysmod.values()
        except:
            raise ImportError("Country py-module '%s' not loaded correctly" % imp.__name__)
    try:
        # assert 'CC' in dir(imp)
        CC = getattr(imp, 'CC', None)
    except:
        logging.warning("\n! Global variable 'CC' not set - use default !")
    # try:
    #     # assert 'META' in dir(imp)
    #     METADATNAT = getattr(imp, 'META', None)
    #     assert METADATNAT is not None
    # except:
    #     logging.warning("\n! No default metadata dictionary 'META' available !")
    # else:
    #     logging.warning("\n! Default hard-coded metadata dictionary 'META' found !")
    try:
        # assert 'harmonise' in dir(imp)
        harmonise = getattr(imp, HARMONISE, None)
        assert harmonise is not None
    except:
        logging.warning('\n! Generic formatting/harmonisation methods used !')
        harmonise = __harmoniseData
    else:
        logging.warning('\n! Country-specific formatting/harmonisation methods used !')
    for proc in PROCESSES:
        try:
            # assert proc in dir(imp)
            proc_data = getattr(imp, proc, None)
            assert proc_data is not None
        except:
            # logging.warning("! no data '%s' method used !" % proc)
            pass # proc_data = None
        else:
            logging.warning("\n! country-specific '%s_data' method loaded !" % proc)
        finally:
            kwargs.update({proc: proc_data})
    # load country-dedicated metadata when available
    metadata = None
    metafname = '%s.json' % ccname
    try:
        metafname = osp.join(__THISDIR, metadir, metafname)
        assert osp.exists(metafname)
        with open(metafname, 'r') as fp:
            metadata = Json.load(fp)
    except (AssertionError,FileNotFoundError):
        logging.warning("\n! No metadata JSON-file '%s' found - will proceed without !" % metafname)
    else:
        logging.warning("! Ad-hoc metadata found - JSON-file '%s' loaded !" % metafname)
    # define the actual metadata: the one loaded, or the default
    # metadata = metadata or METADATNAT
    if metadata in (None,{}):
        raise IOError('No metadata parsed - this cannot end up well')
    try:
        kwargs.update({'coder': coder, 'country' : {'code': CC or country}})
                        # 'opt_load': {}, 'opt_format': {}, 'opt_save': {}
        res = harmonise(facility, metadata, **kwargs)
    except:
        raise IOError("Harmonisation process for country '%s' failed..." % country)
    else:
        logging.warning("\n! Harmonised data for country '%s' generated !" % country)
    return res


#%%
#==============================================================================
# Main functions
#==============================================================================

run = harmoniseCountryService

def __main():
    """Parse and check the command line with default arguments.
    """
    parser = OptionParser(                                                  \
        description=                                                        \
    """Harmonise input national data on facility services.""",
        usage=                                                              \
    """usage:         harmonise facility <code> <coder> <key>
    facility :        Type of service.
    <code> :          Country code.
    <coder> ;         Geocoder.
    <key> :           Geocoder key"""                                      \
                       )

    #parser.add_option("-s", "--service", action="store", dest="facility",
    #                  help="Facility/service type.",
    #                  default=None)
    parser.add_option("-c", "--cc", action="store", dest="country",
                      help="Country.",
                      default=None)
    parser.add_option("-g", "--geocoder", action="store", dest="coder",
                      help="geocoder.",
                      default=None)
    parser.add_option("-k", "--geokey", action="store", dest="key",
                      help="geocoder key.",
                      default=None)
    #parser.add_option("-r", "--dry-run", action="store_true", dest="dryrun",
    #                  help="run the script without creating the file")
    (opts, args) = parser.parse_args()

    opts.test=1

    if not args in (None,()):
        facility = args[0]
    #else:
    #    facility = list(FACILITIES.keys())[0]

    country = opts.country
    if isinstance(coder, string_types):
        if country.upper() == 'ALL':
            country = None
        elif country.upper() in AREAS:
            country = AREAS.get(country)
    elif country is not None:
        parser.error("country name is required.")
    if country in (None,[]) :
        # parser.error("country name is required.")
        country = list(COUNTRIES.values())[0]

    coder = opts.coder
    if isinstance(coder, string_types):
        coder = {coder: opts.key}
    elif coder is not None:
        parser.error("coder is required.")

    # run the generator
    try:
        run(facility, country, coder)
    except IOError:
        logging.warning('\n!!!  ERROR: data file not created !!!')
    else:
        logging.warning('\n!  OK: data file correctly created !')

#try:
#    del(__THISDIR)
#except:
#    pass

if __name__ == '__main__':
    __main()

