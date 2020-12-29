#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _config

.. Links

.. _services: https://github.com/eurostat/basic-services
.. |services| replace:: `facility services data <services_>`_
.. _GISCO: https://github.com/eurostat/happyGISCO
.. |GISCO| replace:: `GISCO <GISCO_>`_

Configuration module providing with the formatting template for the output
integrated data on national facilities.

**Dependencies**

*require*:      :mod:`os`, :mod:`warnings`, :mod:`collections`, :mod:`datetime`

*optional*:     :mod:`json`

*call*:         :mod:`pyeudatnat`, :mod:`pyeudatnat.meta`, :mod:`pyeudatnat.base`

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_
# *since*:        Tue Mar 31 22:51:37 2020

#%% Settings

from os import path as osp
import logging

from collections import OrderedDict, Mapping
from six import string_types
from copy import deepcopy

from datetime import datetime

try:
    from importlib import import_module
except:
    # import_module = lambda mod: exec('from %s import %s' % mod.split('.'))
    import_module = lambda _mod, pack: exec('from %s import %s' % (pack, _mod.split('.')[1])) or None

from pyeudatnat import COUNTRIES
from pyeudatnat.meta import MetaDat, MetaDatNat
from pyeudatnat.base import datnatFactory

from . import FACILITIES, PACKNAME, PACKPATH#analysis:ignore


#%% Global var

FACMETADATA         = {__fac:{} for __fac in FACILITIES.keys() if __fac!='Oth'}
# dict.fromkeys(list(FACILITIES.keys()), {})


#==============================================================================
#%% Class MetaDatEUFacility

class MetaDatEUFacility(MetaDat):
    """Class used to represent metadata for harmonised dataset at EU level.

        >>> EUmeta = MetaDatEUFacility(cat = facility, **kwargs)
    """

    # CATEGORY = 'HCS' # if only HCS...
    # PROPERTIES = [meta['name'] for meta in FACMETADATA[CATEGORY].values()]

    #/************************************************************************/
    def __init__(self, *args, **kwargs):
        facility = kwargs.pop('cat', None)
        if isinstance(facility, string_types) and facility in FACILITIES:
            kwargs.update({'category': FACILITIES.get(facility)})
        elif facility is not None:
            kwargs.update({'category': facility})
        super(MetaDatEUFacility, self).__init__(*args, **kwargs)

    #/************************************************************************/
    @property
    def facility(self):
        try:
            assert hasattr(self.category, 'code')
            return self.category.get('code')
        except:
            return self.category

    #/************************************************************************/
    def load(self, src=None, **kwargs):
        """Reloading metadata from default config file into global configuration
        variables.
        """
        if src is None:
            try:
                path = CONFIGDIR
                assert osp.exists(path) and osp.isdir(path) # useless...just in case we change the def
            except:
                path = ''
            src = osp.join(path, "%s%s.json" % (self.facility, FACMETADATA))
            logging.warning("\n! Input data file '%s' will be loaded" % src)
        return super(MetaDatEUFacility,self).load(src = src, **kwargs)

    #/************************************************************************/
    def dump(self, dest=None, **kwargs):
        """Saving global configuration variables as metadata into default config file.
        """
        if dest is None:
            try:
                path = CONFIGDIR
                assert osp.exists(path) and osp.isdir(path)
            except:
                path = ''
            dest = osp.join(path, "%s%s.json" % (self.facility, FACMETADATA))
            logging.warning("\n! Output data file '%s' will be created" % dest)
        super(MetaDatEUFacility,self).dump(dest = dest, **kwargs)


#==============================================================================
#%% Class MetaDatNatFacility

class MetaDatNatFacility(MetaDatNat):
    """Generic class used to represent metadata for datasets at national (country)
    level as dictionary-like instances.

        >>> CCmeta = MetaDatNatFacility(**metadata)
    """

    PROPERTIES = ['provider', 'country', 'lang', 'proj', 'file', 'path',
                  'columns', 'index', 'options', 'category', 'date']
    #          {'country':{}, 'lang':{}, 'proj':None, 'file':'', 'path':'', 'columns':{}, 'index':[], 'options':{}}

    #/************************************************************************/
    @classmethod
    def template(cls, cat = None, country = None, **kwargs):
        """"Create a template country metadata file as a JSON file

            >>> MetaFacility.template(cat = None, country = None, **kwargs)
        """
        if country is None:
            country = ''
        elif not isinstance(country, string_types):
            raise TypeError("Wrong type for country code '%s' - must be a string" % country)
        if cat is None:
            cat = ''
        elif isinstance(cat, string_types) and cat in FACILITIES:
            cat = FACILITIES.get(cat)
        else:
            raise TypeError("Wrong type for facility type '%s' - must be a string" % cat)
        as_file = kwargs.pop('as_file', True)
        # dumb initialisation
        temp = dict.fromkeys(cls.PROPERTIES)
        temp.update({ 'country':    {'code': country.upper() or 'CC', 'name': ''},
                      'lang':       {'code': country.lower() or 'cc', 'name': ''},
                      'file':       '%s.csv' % country or 'CC' ,
                      'proj':       None,
                      'path':       '../../data/raw/',
                      'columns':    [ ],
                      'index':      { },
                      'options':    {
                          'fetch': {},
                          'load': {
                              'enc':        'latin1',
                              'sep':        ';',
                              'dtfmt':      '%d-%m-%Y'
                              },
                          'clean': {},
                          'prepare': {},
                          'locate': {},
                          'format': {},
                          'save': {}
                          }
                      #'provider':   None,
                      #'date':       None
                      })
        temp['columns'].extend([{country.lower() or 'cc': 'icol1', 'en': 'icol1', 'fr': 'icol1', 'de': 'iSpal1'},
                             {country.lower() or 'cc': 'icol2', 'en': 'icol1', 'fr': 'icol2', 'de': 'iSpal2'}])
        [temp['index'].update({'ocol%s': 'icol%s' % str(i+1)}) for i in [0,1]]
        # create the metadata structure with this dumb template
        template = cls(temp)
        try:
            assert as_file is True
            # save it...somewhere
            dest = osp.join(PACKPATH, cat, "%s%s.json" % (country.upper() or 'temp', cat))
            template.save(dest, **kwargs)
        except AssertionError:
            return template
        except:
            raise IOError("Impossible saving template metadata as a file")


#==============================================================================
#%% Function facilityFactory

def facilityFactory(*args, **kwargs):
    """Generic function to derive a class from the base class :class:`BaseFacility`
    depending on specific metadata and a given geocoder.

        >>>  NewFacility = facilityFactory(cat = facility, meta = None,
                                           country = None, coder = None)

    Examples
    --------

        >>>  NewHCS = facilityFactory(HCS, cc = CC1, coder = {'Bing', yourkey})
        >>>  NewFacility = facilityFactory(cc = CC2, coder = 'GISCO')

    See also
    --------
    :meth:`~pyeudatnat.base.datnatFactory`.
    """
    # check facility to define output data configuration format
    if args in ((),(None,)):        facility = None
    else:                           facility = args[0]
    facility = facility or kwargs.pop('cat', None)
    try:
        assert facility is None or isinstance(facility, (string_types, Mapping, MetaDat))
    except AssertionError:
        raise TypeError("Facility type '%s' not recognised - must be a string" % type(facility))
    if facility is None:
        config = {}
    elif isinstance(facility, string_types):
        try:
            config = FACMETADATA[facility]
        except AttributeError:
            raise TypeError("Facility string '%s' not recognised - must be in '%s'" % (facility, list(FACILITIES.keys())))
        else:
            config = MetaDatEUFacility(deepcopy(config), cat = facility)
    elif isinstance(facility, Mapping):
        config = MetaDatEUFacility(facility)
    elif isinstance(facility, MetaDatEUFacility):
        config = facility.copy()
    return datnatFactory(config = config, **kwargs)


#==============================================================================
#%% Program run when loading the module

# The code below is run when importing/loading the module config. It is used to
# automatically:
#   * load the facility configuration file(s) listed in FACMETADATA whenever
#     it(they) exist(s), e.g. hcs.json is a file in the package directory
#   * generate this(ese) file(s) in the opposite scenario.

for __fac in FACMETADATA.keys():
    # for a given facility
    __cfac = FACILITIES[__fac]['code']

    # check facility's configuration file
    __path = PACKPATH
    try:
        __fcfg = osp.join(__path, "%s.json" % __cfac)
        assert osp.exists(__fcfg) and osp.isfile(__fcfg)
    except AssertionError:
        try:
            __ccfg = osp.join(__path, "%s" % __cfac, "__init__.py")
            # __ccfg = osp.join(__path, "%s.py" % __cfac)
            assert osp.exists(__ccfg) and osp.isfile(__ccfg)
        except AssertionError:
            logging.warning("\n! No config file available for facility '%s' !" % __fac)
            continue
        else:
            try:
                imp = import_module('.%s' % __cfac, '%s' % PACKNAME)
                assert __fac in dir(imp)
                __info = getattr(imp, __fac, None)
            except ImportError:
                logging.warning("\n! Error with py-module for facility '%s' - will proceed without !" % __fac)
                continue
            else:
                logging.warning("\n! Configuration file for facility '%s' will be created !" % __fac)
                # with open(__fcfg, 'w') as __fp: Json.dump(__info, __fp)
                __cfg = MetaDatEUFacility(__info, cat = __fac)
                __cfg.dump(dest = __fcfg, indent = 4) #, sort_keys=True)
    else:
        # with open(__fcfg, 'r') as __fp: __info = Json.load(__fp)
        __cfg = MetaDatEUFacility(cat = __fac)
        __info = __cfg.load(src = __fcfg)
    finally:
        # logging.warning("\n! Loading configuration data for facility '%s' !" % __fac)
        FACMETADATA[__fac] = deepcopy(__info) # __info.copy()
        FACMETADATA[__fac].update({"category": FACILITIES[__fac]})


try:
    del(__fac, __cfac, __path)
    del(__cfg, __info, __fcfg, __ccfg)
except: pass
