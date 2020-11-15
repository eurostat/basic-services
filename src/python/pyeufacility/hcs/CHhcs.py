#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _CHhcs

Module implementing integration of CH data on health care.

*require*:      :mod:`numpy`, :mod:`pandas`

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_
# *since*:        Mon Apr  6 10:00:28 2020

#%%

import re

import numpy as np#analysis:ignore
import pandas as pd#analysis:ignore


#%%

CC              = 'CH'

# METADATNAT : will be read from the CHhcs.json file


#%%

def prepare_data(self):
    """Prepare CH data.

    * Ort => postcode city
    * Adr => street house_number
    """
    #self.data['Ort'].replace('\s+',' ',regex=True,inplace=True)
    #df = self.data['Ort'].str.split(pat=",", n=1, expand=True)
    #self.data[['postcode', 'city']] = df[1].str.split(pat=' ', n=2, expand=True)
    #self.data['Adr'].replace('\s+',' ',regex=True,inplace=True)
    #self.data[['street', 'number']] = self.data['Adr'].str.split(pat=" ", n=2, expand=True)
    def split_ort(s):
        left, right = re.compile(r'\s*,\s').split(s)
        while left == '' and len(right)>1:
            left = right[-1].strip()
            right = right[:-1]
        if len(right) == 1 and left == '':
            return "", right[0]
        rights = re.compile(r'\s+').split(right)
        postcode = rights[0].strip()
        if postcode.isnumeric():
            city = " ".join(rights[1:])
        else:
            city, postcode = right, "" # np.nan
        return postcode, city
    def split_adr(s):
        left, right = re.compile(r'\s*,\s').split(s)
        while right == '' and len(left)>1:
            right = left[-1].strip()
            left = left[:-1]
        if len(left) == 1 and right == '':
            return left[0], "" #np.nan
        lefts = re.compile(r'\s+').split(left)
        number = lefts[-1].strip()
        if number[0].isdigit():
            street = " ".join(lefts[:-1])
        else:
            street, number = left, "" # np.nan
        return street, number
    self.data[['street', 'number']] = self.data.apply(
            lambda row: pd.Series(split_adr(row['Adr'])), axis=1)
    self.data[['postcode', 'city']] = self.data.apply(
            lambda row: pd.Series(split_ort(row['Ort'])), axis=1)
    # add the columns as inputs (they were created)
    self.icolumns.extend([{'en':'street'}, {'en': 'number'}, {'en':'postcode'}, {'en': 'city'}])
    # add the data as outputs (they will be stored)
    self.oindex.update({'street': 'street', 'number': 'number', 'postcode': 'postcode', 'city': 'city'})
