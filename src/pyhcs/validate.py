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

# *credits*:      `gjacopo <gjacopo@ec.europa.eu>`_ 
# *since*:        Thu Apr  2 16:30:50 2020

from os import path as osp
import warnings#analysis:ignore

from collections import Mapping, Sequence
from six import string_types

from datetime import datetime

import numpy as np#analysis:ignore
import pandas as pd

from pyhcs import COUNTRIES
from pyhcs.config import INDEX, PATH, FILE, FMT, DATE, ENC, SEP

__thisdir = osp.dirname(__file__)

MINMAX_LL = {'lat': [-90., 90.], 'lon': [-180., 180.]} 


#%% 
#==============================================================================
# Function validateCountry
#==============================================================================

def validateCountry(country=None, **kwargs):
    """Generic validation function.
    
        >>> validate.validateCountry(country, **kwargs)
    """
    if country is None:
        country = list(COUNTRIES.values())
    if isinstance(country, Sequence):
        for ctry in country:
            try:
                validateCountry(country=ctry, **kwargs) 
            except:
                continue
        return
    elif not isinstance(country, string_types):
        raise TypeError('wrong type for input country code - must the ISO 2-letter string')
    elif not country in COUNTRIES.values():
        raise IOError('country code not recognised - must a code of the %s area' % list(COUNTRIES.keys())[0])
    fmt = 'csv'
    src = kwargs.pop('src', None)
    if src is None:
        src = osp.join(PATH, fmt, FILE % (country, FMT[fmt]))
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
            warnings.warn('missing columns in source file: %s' % list(columns))
    index = {col.get('name'): col for col in INDEX.values()}
    for col in df.columns:
        # check missing values
        try:
            assert df[col].isnull().any() is False
        except AssertionError:
            try:
                assert df[col].isnull().all() is False
            except AssertionError:
                warnings.warn('column %s is filled with missing values only' % col)
        else:
            warnings.warn('no missing values in column %s' % col)
        # check tyoe
        dtype = index[col].get('type')
        if dtype is not None:
            try:
                assert df[col].dtype == dtype # and dtype != object
            except AssertionError:
                warnings.warn('unexpected type %s for column %s' % (df[col].dtype,col))
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
                    warnings.warn('unexpected date format for column %s' % col)
    # check geographical coordinates
    for lL in ['lat','lon']:
        if lL in df.columns:
            try:
                assert df[col].dropna().between(MINMAX_LL[lL][0],MINMAX_LL[lL][1]).all() is True
            except AssertionError:
                raise IOError('wrong input values for %s geographical coordinate %s' % lL)
    # else?
    return


#%% 
#==============================================================================
# Function run
#==============================================================================

run = validateCountry
    

#%% 
#==============================================================================
# Main function
#==============================================================================

if __name__ == '__main__':
    run()
