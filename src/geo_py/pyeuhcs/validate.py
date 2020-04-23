#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _validate

Module data validation according to template.
    
**Dependencies**

*require*:      :mod:`os`, :mod:`sys`

*optional*:     :mod:`A`

*call*:         :mod:`pyeudatnat`, :mod:`pyeuhcs.config`         

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Thu Apr  2 16:30:50 2020

#%% 

from os import path as osp
import warnings#analysis:ignore

from collections import Mapping, Sequence#analysis:ignore
from six import string_types

import numpy as np#analysis:ignore
import pandas as pd

try: 
    from optparse import OptionParser
except ImportError:
    warnings.warn('\n! inline command deactivated !')

from pyeudatnat import COUNTRIES
from pyeudatnat.misc import Type
from pyeuhcs.config import CONFIGINFO

__THISFACILITY  = 'HCS'
__THISDIR       = osp.dirname(__file__)
__CONFIG        = CONFIGINFO[__THISFACILITY]

MINMAX_LL = {'lat': [-90., 90.], 'lon': [-180., 180.]} 


#%% 
#==============================================================================
# Function __validateData
#==============================================================================

def __validateData(src):
    ENC, SEP = __CONFIG.get('enc'), __CONFIG.get('sep')
    #if not osp.exists(src):
    #    raise FileNotFoundError('input file %s not found - nothing to check' % src)
    try:
        df = pd.read_csv(src, encoding=ENC, sep=SEP)
    #except FileNotFoundError:      # we tested that already...      
    #    raise FileNotFoundError('input file %s not found - nothing to check' % src)
    except:
        try:
            df = pd.read_table(src, encoding=ENC, sep=SEP, compression='infer')
        except:
            raise IOError("Impossible to load source data - format not recognised")
    INDEX = __CONFIG.get('index',{}).copy()
    index = [col.get('name') for col in INDEX.values()]
    try:
        columns = set(list(df.columns)).difference(set(index))
        assert columns == set()
    except AssertionError:
        raise IOError("Unknown column present in the dataframe: '%s'" % list(columns))
    else:
        try:
            columns = set(list(index)).difference(set(df.columns))
            assert columns == set()
        except AssertionError:
            warnings.warn("\n! Missing columns in source file: '%s' !" % list(columns))
    index = {col.get('name'): col for col in INDEX.values()}
    for col in df.columns:
        # check missing values
        try:
            assert df[col].isnull().any() is np.bool_(False)
        except AssertionError:
            try:
                assert df[col].isnull().all() is np.bool_(False)
            except AssertionError:
                warnings.warn("\n! Column '%s' empty - missing values only !" % col)
                continue
        else:
            # warnings.warn("\n! No missing values in column '%s' !" % col)
            pass
        # check type
        dtype = index[col].get('type')
        if dtype == 'str':
            pass # 
        elif dtype is not None:
            try:
                assert df[col].dtype==object or df[col].dtype in Type.pytname2npt(dtype) # and dtype != object
            except AssertionError:
                warnings.warn("\n! Unexpected type '%s' for column '%s' !" % (df[col].dtype,col))
        # check values/format
        dfmt = values = index[col].get('values')
        if values is not None:
            # check values range
            if dtype == "datetime":
                # check date format    
                try:
                    pd.to_datetime(df[col], format=dfmt, errors='coerce').notnull().all() is True
                except AssertionError:
                    warnings.warn("\n! Unexpected date format for column '%s' !" % col)
            else:
                try:
                    values = [values,] if not isinstance(values, Sequence) else values
                    assert df[col].dropna().isin(values).all() is True
                except AssertionError:
                    raise IOError("Wrong input values in column '%s'" % col)
    # check id uniquiness
    try: # note the use of INDEX here, not index, though the names end up being
        # the same
        assert df[INDEX.get('id',{})['name']].dropna().is_unique is True
    except AssertionError:
        raise IOError("Duplicated identifier IDs")  
    # check geographical coordinates
    for lL in ['lat','lon']:
        col = INDEX.get(lL,{})['name']
        if col in df.columns:
            try:
                assert df[col].dropna().between(MINMAX_LL[lL][0],MINMAX_LL[lL][1]).all() is np.bool_(True)
            except AssertionError:
                raise IOError("Wrong input values for %s geographical coordinate '%s'" % lL)
    # something else to check?


#%% 
#==============================================================================
# Function validateCountry
#==============================================================================

def validateCountry(country=None, **kwargs):
    """Generic validation function.
    
        >>> validate.validateCountry(country, **kwargs)
    """
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
    fmt = 'csv'
    src = kwargs.pop('source', None)
    if src is None:
        src = osp.join(__CONFIG.get('path'), fmt, __CONFIG.get('file') % (country, __CONFIG.get('fmt',{})[fmt]))
        warnings.warn("\n! Input data file '%s' will be controlled for validation" % src)
    try:
        assert osp.exists(src)
    except:
        raise FileNotFoundError("Input file '%s' not found" % src)
    validate = __validateData
    validate(src)
    return  
  

#%% 
#==============================================================================
# Main functions
#==============================================================================

run = validateCountry

def __main():
    """Parse and check the command line with default arguments.
    """
    parser = OptionParser(                                                  \
        description=                                                        \
    """Validate output harmonised data on health care services.""",
        usage=                                                              \
    """usage:         harmonise [options] <code> 
    <code> :          country code."""                                      \
                        )
    
    #parser.add_option("-c", "--cc", action="store", dest="cc",
    #                  help="country ISO-code.",
    #                  default=None)
    (opts, args) = parser.parse_args()
    
    # define the input metadata file (base)name
    if not args in (None,()):
        country = args[0]
    else:
        # parser.error("country name is required.")
        country = list(COUNTRIES.values())[0]
    
    # run the generator
    try:
        run(country)
    except IOError:
        warnings.warn('\n!!!  ERROR: data file not validated !!!')
    else:
        warnings.warn('\n!  OK: data file correctly validated !')

if __name__ == '__main__':
    __main()
