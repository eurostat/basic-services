#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _BGhcs

Module implementing integration of BG data on health care.

*require*:      :mod:`numpy`, :mod:`pandas`

*call*:         :mod:`config`, :mod:`basehcs`

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_
# *since*:        Sun Mar 29 19:00:32 2020


#%%

import re
# from collections import Mapping, Sequence

import numpy as np
import pandas as pd


#%%

CC              = 'BG'


#%%

class Prepare_data():
    """Class of methods to prepare BG data.
    """

    def __init__(self):
        pass

    @classmethod
    def split_address(cls, s):
        street, number = "", ""
        mem = re.compile(r'\s*,\s*').split(s)
        ss, last = mem[0], " ".join(mem[1:])
        while last == '' and len(ss)>1:
            last = ss[-1].strip()
            ss = ss[:-1]
        if len(ss) == 1 and last == '':
            return ss[0], np.nan
        if last[0].isdigit():
            street, number = ', '.join(ss), last
        else:
            street, number = ss, np.nan
        return street, number

    def __call__(self, facility):
        cols = facility.data.columns.tolist()
        new_cols = ['street', 'number']
        facility.data.reindex(columns = [*cols, *new_cols], fill_value = "")
        # facility.data[['street', 'number']] = facility.data['address'].str.split(pat=',', n=2, expand=True)
        facility.data[new_cols] = (
            facility.data
            .apply(lambda row: pd.Series(self.split_address(row['address'])), axis=1)
            )
        # add the columns as inputs (they were created)
        facility.cols.extend([{'en':c} for c in new_cols])
        # add the data as outputs (they will be stored)
        facility.idx.update({c:c for c in new_cols})


def prepare_data(self):
    """Overriding prepare_data method for LT data.
    """
    preparator = Prepare_data()
    preparator(self)
    return

