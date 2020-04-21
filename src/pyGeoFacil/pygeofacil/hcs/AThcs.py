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

# METADATA : will be read from the AThcs.json file


#%%

def prepare_data(self):
    """Prepare AT data. 
    
    * Adresse => street house_number postcode city
    """
	# example: St. Veiter-Straße 46, 5621 St. Veit im Pongau    
    #df = self.data['address'].str.split(pat=",", n=1, expand=True)
    #df.rename(columns={0: 'left', 1:'right'}, inplace=True) # not necessary, for the clarity of the code...
    ## note: rsplit does not work with regular expressions, including the regex '\s+'
    ## for multiple whitespaces, so we replace multiple
    ## blanks here...
    #[df[col].replace('\s+',' ',regex=True,inplace=True) for col in ['left','right']]    
    #self.data[['street', 'number']] = df['left'].str.rsplit(pat=' ', n=1, expand=True)
    #self.data[['postcode', 'city']] = df['right'].str.split(pat=' ', n=2, expand=True)
    def split_address(s):
        left, right = re.compile(r'\s*,\s').split(s) # s.split(',')
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
    self.data[['street', 'number', 'postcode', 'city']] = self.data.apply(
            lambda row: pd.Series(split_address(row['Adresse'])), axis=1)
    # add the columns as inputs (they were created)
    self.icolumns.extend([{'en':'street'}, {'en': 'number'}, {'en':'postcode'}, {'en': 'city'}])
    # add the data as outputs (they will be stored)
    self.oindex.update({'street': 'street', 'number': 'number', 'postcode': 'postcode', 'city': 'city'})
