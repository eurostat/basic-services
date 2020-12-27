#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _AThcs

Module implementing integration of AT data on health care.

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

CC              = 'AT'

# METADATNAT : will be read from the AThcs.json file


#%%

class prepare_data():
    """Prepare AT data.
    """

    @classmethod
    def split_address(cls, s):
        # Adresse => street house_number postcode city
        street, number, postcode, city = "", "", "", ""
        mem = re.compile(r'\s*,\s*').split(s)
        left, right = mem[0], " ".join(mem[1:])
        while right == '' and len(left)>1:
            right = left[-1].strip()
            left = left[:-1]
        if len(left) == 1 and right == '':
            return left[0], "", "", "" #np.nan, np.nan, np.nan
        lefts = re.compile(r'\s+').split(left)
        number = lefts[-1].strip()
        if number[0].isdigit():
            street = " ".join(lefts[:-1])
        else:
            street, number = left, "" # np.nan
        rights = re.compile(r'\s+').split(right)
        postcode = rights[0].strip() # strip actually not necessary...
        if postcode.isnumeric():
            city = " ".join(rights[1:])
        else:
            city, postcode = right, "" # np.nan
        return street, number, postcode, city

    def __call__(self, facility):
        cols = facility.data.columns.tolist()
        new_cols = ['street', 'number', 'postcode', 'city']
        facility.data.reindex(columns = [*cols, *new_cols], fill_value = "")
    	# example: St. Veiter-Straße 46, 5621 St. Veit im Pongau
        #df = facility.data['address'].str.split(pat=",", n=1, expand=True)
        #df.rename(columns={0: 'left', 1:'right'}, inplace=True) # not necessary, for the clarity of the code...
        ## note: rsplit does not work with regular expressions, including the regex '\s+'
        ## for multiple whitespaces, so we replace multiple
        ## blanks here...
        #[df[col].replace('\s+',' ',regex=True,inplace=True) for col in ['left','right']]
        #facility.data[['street', 'number']] = df['left'].str.rsplit(pat=' ', n=1, expand=True)
        #facility.data[['postcode', 'city']] = df['right'].str.split(pat=' ', n=2, expand=True)
        facility.data[new_cols] = facility.data.apply(
                lambda row: pd.Series(self.split_address(row['Adresse'])), axis = 1)
        # add the columns as inputs (they were created)
        facility.icolumns.extend([{'en':c} for c in new_cols])
        # add the data as outputs (they will be stored)
        facility.oindex.update({c:c for c in new_cols})

