#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _validate

Module data validation according to template.

**Dependencies**

*require*:      :mod:`os`, :mod:`sys`

*optional*:     :mod:`A`

*call*:         :mod:`pyeudatnat`, :mod:`pyeufacility.config`

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_
# *since*:        Thu Apr  2 16:30:50 2020

#%%

from os import path as osp
import logging

from collections import Mapping, Sequence#analysis:ignore
from six import string_types

import numpy as np#analysis:ignore
import pandas as pd

try:
    from optparse import OptionParser
except ImportError:
    logging.warning('\n! inline command deactivated !')

from pyeudatnat import COUNTRIES, AREAS
from pyeudatnat.misc import Type
from pyeufacility.config import FACMETADATA
from pyeudatnat.io import DEF_ENCODING, DEF_SEP

from pyeufacility import PACKNAME, VALIDATE, FACILITIES

__THISDIR       = osp.dirname(__file__)

MINMAX_LL = {'lat': [-90., 90.], 'lon': [-180., 180.]}


#%%
#==============================================================================
# Function __validateData
#==============================================================================

def __validateData(facility, src):
    ocfg = FACMETADATA[facility]
    oopts = ocfg.get('options', {})
    enc, sep = oopts.get('enc', DEF_ENCODING), oopts.get('sep', DEF_SEP)
    #if not osp.exists(src):
    #    raise FileNotFoundError('input file %s not found - nothing to check' % src)
    try:
        df = pd.read_csv(src, encoding = enc, sep = sep)
    #except FileNotFoundError:      # we tested that already...
    #    raise FileNotFoundError('input file %s not found - nothing to check' % src)
    except:
        try:
            df = pd.read_table(src, encoding = enc, sep = sep, compression = 'infer')
        except:     raise IOError("Impossible to load source data - format not recognised")
    oindex = ocfg.get('index',{}).copy()
    nindex = [col.get('name') for col in oindex.values()]
    try:
        columns = set(list(df.columns)).difference(set(nindex))
        assert columns == set()
    except AssertionError:
        raise IOError("Unknown column present in the dataframe: '%s'" % list(columns))
    else:
        try:
            columns = set(list(nindex)).difference(set(df.columns))
            assert columns == set()
        except AssertionError:
            logging.warning("\n! Missing columns in source file: '%s' !" % list(columns))
    nindex = {col.get('name'): col for col in oindex.values()}
    for col in df.columns:
        # check missing values
        try:
            assert df[col].isnull().any() is np.bool_(False)
        except AssertionError:
            try:
                assert df[col].isnull().all() is np.bool_(False)
            except AssertionError:
                logging.warning("\n! Column '%s' empty - missing values only !" % col)
                continue
        else:
            # logging.warning("\n! No missing values in column '%s' !" % col)
            pass
        # check type
        dtype = nindex[col].get('type')
        if dtype == 'str':
            pass #
        elif dtype is not None:
            try:
                assert df[col].dtype==object or df[col].dtype in Type.pytname2npt(dtype) # and dtype != object
            except AssertionError:
                logging.warning("\n! Unexpected type '%s' for column '%s' !" % (df[col].dtype,col))
        # check values/format
        dfmt = values = nindex[col].get('values')
        if values is not None:
            # check values range
            if dtype == "datetime":
                # check date format
                try:
                    pd.to_datetime(df[col], format=dfmt, errors='coerce').notnull().all() is True
                except AssertionError:
                    logging.warning("\n! Unexpected date format for column '%s' !" % col)
            else:
                try:
                    values = [values,] if not isinstance(values, Sequence) else values
                    assert df[col].dropna().isin(values).all()
                except AssertionError:
                    raise IOError("Wrong input values in column '%s'" % col)
    # check id uniquiness
    try: # note the use of INDEX here, not nindex, though the names end up being
        # the same
        assert df[oindex.get('id',{})['name']].dropna().is_unique is True
    except AssertionError:
        raise IOError("Duplicated identifier IDs")
    # check geographical coordinates
    for lL in ['lat','lon']:
        col = oindex.get(lL,{})['name']
        if col in df.columns:
            try:
                assert (df[col]
                        .dropna()
                        .between(MINMAX_LL[lL][0],MINMAX_LL[lL][1])
                        .all()) is np.bool_(True)
            except AssertionError:
                raise IOError("Wrong input values for %s geographical coordinate '%s'" % lL)
    # something else to check?


#%%
#==============================================================================
# Function validateCountryService
#==============================================================================

def validateCountryService(facility, country = None, **kwargs):
    """Generic validation function.

        >>> validate.validateCountry(country, **kwargs)
    """
    if not isinstance(facility, string_types):
        raise TypeError("Wrong type for input service - must be the facility type")
    elif not facility in FACILITIES.keys():
        raise IOError("Service type not recognised - must be a string in the list '%s'" % list(FACILITIES.keys()))
    if country is None:
        country = list(COUNTRIES.keys())
    if not isinstance(country, string_types) and isinstance(country, Sequence):
        for ctry in country:
            try:
                validateCountry(country=ctry, **kwargs)
            except:
                continue
        return
    elif not isinstance(country, string_types):
        raise TypeError('wrong type for input country code - must the ISO 2-letter string')
    elif not country in COUNTRIES.keys():
        raise IOError('country code not recognised - must a code of the %s area' % list(COUNTRIES.keys()))
    cfg = FACMETADATA[facility]
    fmt = 'csv'
    src = kwargs.pop('src', None)
    if src is None:
        src = osp.join(cfg.get('path'), fmt, cfg.get('file') % (country, cfg.get('fmt',{})[fmt]))
        logging.warning("\n! Input data file '%s' will be controlled for validation" % src)
    try:
        assert osp.exists(src)
    except:
        raise FileNotFoundError("Input file '%s' not found" % src)
    validate = __validateData
    try:
        validate(facility, src)
    except:
        raise IOError("Data error detected - See warning/error reports")
    else:
        print("! Data passed validation (see warning reports) !")
    return


#%%
#==============================================================================
# Main functions
#==============================================================================

run = validateCountryService

def __main():
    """Parse and check the command line with default arguments.
    """
    parser = OptionParser(                                                  \
        description=                                                        \
    """Validate output harmonised data on health care services.""",
        usage=                                                              \
    """usage:         validate facility <code>
    facility :        Type of service.
    <code> :          country code."""                                      \
                        )

    parser.add_option("-c", "--cc", action="store", dest="country",
                      help="Country.",
                      default=None)
    (opts, args) = parser.parse_args()

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

    # run the generator
    try:
        run(facility, country)
    except IOError:
        logging.warning('\n!!!  ERROR: data file not validated !!!')
    else:
        logging.warning('\n!  OK: data file correctly validated !')

if __name__ == '__main__':
    __main()
