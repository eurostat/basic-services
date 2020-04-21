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

from pyhcs import PACKNAME, BASENAME, COUNTRIES#analysis:ignore
from pyhcs.config import OCONFIGNAME#analysis:ignore
from pyhcs.base import IMETANAME, MetaHCS, hcsFactory#analysis:ignore

import numpy as np
import pandas as pd


#%%
    
CC              = 'BG'

# METADATA : will be read from the BGhcs.json file

#METADATA        =  { 'country':     {'code': 'BG', 'name': 'Bulgaria'},
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
        
def prepare_data(self):
    # nope, this wouldn't work:
    # self.data[['street', 'number']] = self.data['address'].str.split(pat=',', n=2, expand=True)
    def split_address(s):
        ss, last = re.compile(r'\s*,\s').split(s), ''
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
    self.data[['street', 'number']] = self.data.apply(
            lambda row: pd.Series(split_address(row['address'])), axis=1)
    # add the columns as inputs (they were created)
    self.icolumns.extend([{'en':'street'}, {'en': 'number'}])
    # add the data as outputs (they will be stored)
    self.oindex.update({'street': 'street', 'number': 'number'})


#def harmoniseBG(metadata, **kwargs):
#    try:
#        assert isinstance(metadata,(MetaHCS,Mapping))  
#    except:
#        raise TypeError('wrong input metadata')
#    try:
#        BGHCS = hcsFactory(metadata, **kwargs)
#    except:
#        raise IOError('impossible create BG country class')
#    else:
#        BGHCS.prepare_data = prepare_data
#    try:
#        bg = BGHCS()
#    except:
#        raise IOError('impossible create specific country instance')
#    opt_load = kwargs.pop("opt_load", {})        
#    bg.load_source(**opt_load)
#    opt_prep = kwargs.pop("opt_prep", {})        
#    bg.prepare_data(**opt_prep)
#    opt_format = kwargs.pop("opt_format", {})        
#    bg.format_data(**opt_format)
#    opt_save = kwargs.pop("opt_save", {'geojson': {}, 'csv': {}})        
#    bg.save_data(fmt='geojson', **opt_save.get('geojson',{}))
#    bg.save_data(fmt='csv',**opt_save.get('csv',{}))
#    # hcs.save_meta(fmt='json')

