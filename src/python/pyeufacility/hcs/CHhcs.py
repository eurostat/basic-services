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

# metadata will be read from the CHhcs.json file


#%%

class Prepare_data():
    """Class of methods to prepare CH data.
    """

    def __init__(self):
        pass

    @classmethod
    def split_ort(cls, s):
        # * Ort => postcode city
        postcode, city = "", ""
        mem = re.compile(r'\s*,\s*').split(s)
        left, right = mem[0], " ".join(mem[1:])
        while left == '' and len(right)>1:
            left = right[-1].strip()
            right = right[:-1]
        if len(right) == 1 and left == '':
            return "", right[0]
        rights = re.compile(r'\s+').split(right)
        postcode = rights[0].strip()
        if postcode.isnumeric(): # or postcode[-1].isdigit()
            city = " ".join(rights[1:])
        else:
            city, postcode = right, "" # np.nan
        return postcode, city

    @classmethod
    def split_adr(cls, s):
        # * Adr => street house_number
        street, number = "", ""
        mem = re.compile(r'\s*,\s*').split(s)
        left, right = mem[0], " ".join(mem[1:])
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

    def __call__(self, facility):
        cols = facility.data.columns.tolist()
        ort_cols = ['postcode', 'city']
        adr_cols = ['street', 'number']
        facility.data.reindex(columns = [*cols, *ort_cols, *adr_cols], fill_value = "")
        #facility.data['Ort'].replace('\s+',' ',regex=True,inplace=True)
        #df = facility.data['Ort'].str.split(pat=",", n=1, expand=True)
        #facility.data[['postcode', 'city']] = df[1].str.split(pat=' ', n=2, expand=True)
        #facility.data['Adr'].replace('\s+',' ',regex=True,inplace=True)
        #facility.data[['street', 'number']] = facility.data['Adr'].str.split(pat=" ", n=2, expand=True)
        facility.data[adr_cols] = (
            facility.data
            .apply(lambda row: pd.Series(self.split_adr(row['Adr'])), axis=1)
            )
        facility.data[ort_cols] = (
            facility.data
            .apply(lambda row: pd.Series(self.split_ort(row['Ort'])), axis=1)
            )
        # add the columns as inputs (they were created)
        adr_cols.extend(ort_cols)
        facility.cols.extend([{'en':c} for c in adr_cols])
        # add the data as outputs (they will be stored)
        facility.idx.update({c:c for c in adr_cols})


def prepare_data(self):
    """Overriding prepare_data method for LT data.
    """
    preparator = Prepare_data()
    preparator(self)
    return
