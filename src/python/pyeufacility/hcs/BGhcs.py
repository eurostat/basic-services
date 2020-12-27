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

# METADATNAT : will be read from the BGhcs.json file

#METADATNAT        =  { 'country':     {'code': 'BG', 'name': 'Bulgaria'},
#                     'lang':        {'code': 'bg', 'name': 'bulgarian'},
#                     'proj':        None,
#                     'file':        'HE_HOSP_12_13_EN.xls',
#                     'path':        '../../../data/raw/',
#                     'enc':         'latin1',
#                     'sep':         ';',
#                     'date':        None, #'%d-%m-%Y %H:%M',
#                     'columns':     [
#                             {'en': 'OBJECTID',          'bg': '', 'fr': '', 'de': ''},
#                             {'en': 'NUTS3',             'bg': '', 'fr': '', 'de': ''},
#                             {'en': 'area_code',         'bg': '', 'fr': '', 'de': ''},
#                             {'en': 'OBSTINA',           'bg': '', 'fr': '', 'de': ''},
#                             {'en': 'EKATTE',            'bg': '', 'fr': '', 'de': ''},
#                             {'en': 'SETTLEMENT_NAME',   'bg': '', 'fr': '', 'de': ''},
#                             {'en': 'address',           'bg': '', 'fr': '', 'de': ''},
#                             {'en': 'EIK',               'bg': '', 'fr': '', 'de': ''},
#                             {'en': 'EIK_EKATTE',        'bg': '', 'fr': '', 'de': ''},
#                             {'en': 'INSTITUTION_NAME',  'bg': '', 'fr': '', 'de': ''},
#                             {'en': 'TYPE_NAT',          'bg': '', 'fr': '', 'de': ''},
#                             {'en': 'ICHA_HP_11',        'bg': '', 'fr': '', 'de': ''},
#                             {'en': 'H_T',               'bg': '', 'fr': '', 'de': ''},
#                             {'en': 'YEAR_',             'bg': '', 'fr': '', 'de': ''},
#                             {'en': 'LONG',              'bg': '', 'fr': '', 'de': ''},
#                             {'en': 'LAT',               'bg': '', 'fr': '', 'de': ''},
#                             ],
#                     'index':       {
#                             'id':          'OBJECTID',
#                             'name':        'INSTITUTION_NAME',
#                             'site':        None,
#                             'lat':         'LAT',
#                             'lon':         'LONG',
#                             'geo_qual':    None,
#                             'street':      None,
#                             'number':      None,
#                             'postcode':    None,
#                             'city':        'SETTLEMENT_NAME',
#                             'cc':          None,
#                             'country':     None,
#                             'ER':          None,
#                             'beds':        'H_T',
#                             'prac':        None,
#                             'rooms':       None,
#                             'type':        None,
#                             'PP':          None,
#                             'specs':       None,
#                             'tel':         None,
#                             'email':       None,
#                             'url':         None,
#                             'refdate':     'YEAR_',
#                             'pubdate':     None
#                             }
#                     }


#%%

class prepare_data():
    # nope, this wouldn't work:

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
        facility.icolumns.extend([{'en':c} for c in new_cols])
        # add the data as outputs (they will be stored)
        facility.oindex.update({c:c for c in new_cols})


