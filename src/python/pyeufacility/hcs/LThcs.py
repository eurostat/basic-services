#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _LThcs

Module implementing integration of LT data on health care.

*require*:      :mod:`numpy`, :mod:`pandas`

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_
# *since*:        Sun Nov

#%%

import re

import numpy as np#analysis:ignore
import pandas as pd#analysis:ignore


#%%

CC              = 'LT'

# METADATNAT : will be read from the LThcs.json file


#%%

class prepare_data():
    """Prepare LT data.
    """
    def __init__(self):
        pass

    @classmethod
    def split_Adr(cls, s):
        street, number, postcode, city = "", "", "", ""
        mem = re.compile(r'\s*,\s*').split(s)
        left, right = mem[0], " ".join(mem[1:])
        while left == '' and len(right)>1:
            left = right[-1].strip()
            right = right[:-1]
        if len(right) == 1 and left == '':
            return "", right[0], "", ""
        elif len(left) == 1 and right == '':
            return "", "", left[0], ""
        rights = re.compile(r'\s+').split(right)
        for r in rights:
            r = r.strip()
            if r == '': continue
            if r.isnumeric() or r[-1].isdigit():
                postcode = " ".join([postcode,r])
            else:
                city = " ".join([city,r])
        lefts = re.compile(r'\s+').split(left)
        for l in lefts:
            l = l.strip()
            if l == '': continue
            if l.isnumeric() or l[0].isdigit():
                number = " ".join([number,l])
            else:
                street = " ".join([street,l])
        return street, number, postcode, city

    def set_address(self, data):
        cols = data.columns.tolist()
        new_cols = ['street', 'number', 'postcode', 'city']
        data.reindex(columns = [*cols, *new_cols], fill_value = "")
        data[new_cols] =  (
            data
            .apply(lambda row: pd.Series(self.split_Adr(row['Address'])), axis=1)
            )

    def set_pp(self, data):
        col_pp = 'Level: 1-national, 2-regional, 3-municipality, 4-nursing, 5-other public and specialized, 6-private'
        data['public_private'] = (
            data[col_pp]
            .apply(lambda x: 'private' if x==6 else 'public')
            )

    def __call__(self, facility):
        self.set_address(facility.data)
        # add the columns as inputs (they were created)
        facility.icolumns.extend([{'en':c} for c in new_cols])
        # add the data as outputs (they will be stored)
        facility.oindex.update({c:c for c in new_cols})
        # return facility
        self.set_pp(facility.data)
        facility.icolumns.extend([{'en': 'public_private'}])
        # add the data as outputs (they will be stored)
        facility.oindex.update({'public_private':'public_private'})
        # return facility
        return facility
