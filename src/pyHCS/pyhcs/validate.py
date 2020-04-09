#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _validate

Module data validation according to template.
    
**Dependencies**

*require*:      :mod:`os`, :mod:`sys`

*optional*:     :mod:`A`

*call*:         :mod:`pyhcs.config`, :mod:`pyhcs.base`         

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Thu Apr  2 16:30:50 2020

#%% 

from os import path as osp
import warnings#analysis:ignore

from collections import Mapping, Sequence#analysis:ignore
from six import string_types

from datetime import datetime

import numpy as np#analysis:ignore
import pandas as pd

try: 
    from optparse import OptionParser
except ImportError:
    warnings.warn('! inline command deactivated !')

from pyhcs import PACKNAME, COUNTRIES#analysis:ignore
from pyhcs.config import INDEX, PATH, FILE, FMT, DATE, ENC, SEP#analysis:ignore

__THISDIR = osp.dirname(__file__)

MINMAX_LL = {'lat': [-90., 90.], 'lon': [-180., 180.]} 


#%% 
#==============================================================================
# Function __validateData
#==============================================================================

def __validateData(df):
    index = [col.get('name') for col in INDEX.values()]
    try:
        columns = set(list(df.columns)).difference(set(index))
        assert columns == set()
    except AssertionError:
        raise IOError('unknown column present in the dataframe: %s' % list(columns))
    else:
        try:
            columns = set(list(index)).difference(set(df.columns))
            assert columns == set()
        except AssertionError:
            warnings.warn('! missing columns in source file: %s !' % list(columns))
    index = {col.get('name'): col for col in INDEX.values()}
    for col in df.columns:
        # check missing values
        try:
            assert df[col].isnull().any() is False
        except AssertionError:
            try:
                assert df[col].isnull().all() is False
            except AssertionError:
                warnings.warn('! column %s is filled with missing values only !' % col)
        else:
            warnings.warn('! no missing values in column %s !' % col)
        # check type
        dtype = index[col].get('type')
        if dtype is not None:
            try:
                assert df[col].dtype == dtype # and dtype != object
            except AssertionError:
                warnings.warn('! unexpected type %s for column %s !' % (df[col].dtype,col))
        # check values/format
        dfmt = values = index[col].get('values')
        if values is not None:
            # check values range
            if dtype != datetime:
                try:
                    values = [values,] if not isinstance(values, Sequence) else values
                    assert df[col].dropna().isin(values).all() is True
                except AssertionError:
                    raise IOError('wrong input values in column %s' % col)
            else:
                # check date format    
                try:
                    pd.to_datetime(df[col], format=dfmt, errors='coerce').notnull().all() is True
                except AssertionError:
                    warnings.warn('! unexpected date format for column %s !' % col)
    # check id uniquiness
    try: # note the use of INDEX here, not index, though the names end up being
        # the same
        assert df[INDEX['id']['name']].dropna().is_unique is True
    except AssertionError:
        raise IOError('duplicated identifier IDs')  
    # check geographical coordinates
    for lL in ['lat','lon']:
        col = INDEX[lL]['name']
        if col in df.columns:
            try:
                assert df[col].dropna().between(MINMAX_LL[lL][0],MINMAX_LL[lL][1]).all() is True
            except AssertionError:
                raise IOError('wrong input values for %s geographical coordinate %s' % lL)
    # something else to check?

def __validateFile(src):
    if not osp.exists(src):
        raise FileNotFoundError('input file %s not found - nothing to check' % src)
    try:
        df = pd.read_csv(src, encoding=ENC, sep=SEP)
    #except FileNotFoundError:      # we tested that already...      
    #    raise FileNotFoundError('input file %s not found - nothing to check' % src)
    except:
        try:
            df = pd.read_table(src, encoding=ENC, sep=SEP, compression='infer')
        except:
            raise IOError('impossible to load source data - format not recognised')
    __validateData(df)
    return  


#%% 
#==============================================================================
# Function validateCountry
#==============================================================================

def validateCountry(country=None, **kwargs):
    """Generic validation function.
    
        >>> validate.validateCountry(country, **kwargs)
    """
    if country is None:
        country = list(COUNTRIES.values())[0]
    if not isinstance(country, string_types) and isinstance(country, Sequence):
        for ctry in country:
            try:
                validateCountry(country=ctry, **kwargs) 
            except:
                continue
        return
    elif not isinstance(country, string_types):
        raise TypeError('wrong type for input country code - must the ISO 2-letter string')
    elif not country in list(COUNTRIES.values())[0]:
        raise IOError('country code not recognised - must a code of the %s area' % list(COUNTRIES.keys())[0])
    fmt = 'csv'
    src = kwargs.pop('src', None)
    if src is None:
        src = osp.join(PATH, fmt, FILE % (country, FMT[fmt]))
    validate = __validateFile
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
        warnings.warn('!!!  ERROR: data file not validated !!!')
    else:
        warnings.warn('!  OK: data file correctly validated !')

if __name__ == '__main__':
    __main()
