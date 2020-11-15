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

def prepare_data(self):
    """Prepare LT data.
    """
    def split_Adr(s):
        postcode, city, street, number = "", "", "", ""
        left, right = re.compile(r'\s*,\s').split(s)
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
            if r.isnumeric() or r[-1].isdigit():
                postcode = postcode.join(r)
            else:
                city = city.join(r)
        lefts = re.compile(r'\s+').split(left)
        for l in lefts:
            l = l.strip()
            if l.isnumeric() or l[0].isdigit():
                number = number.join(l)
            else:
                street = street.join(l)
        return postcode, city, street, number
    self.data[['postcode', 'city', 'street', 'number']] = self.data.apply(
            lambda row: pd.Series(split_Adr(row['Adress'])), axis=1)
    # add the columns as inputs (they were created)
    self.icolumns.extend([{'en':'street'}, {'en': 'number'}, {'en':'postcode'}, {'en': 'city'}])
    # add the data as outputs (they will be stored)
    self.oindex.update({'street': 'street', 'number': 'number', 'postcode': 'postcode', 'city': 'city'})
