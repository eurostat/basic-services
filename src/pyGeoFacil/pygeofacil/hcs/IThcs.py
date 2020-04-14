#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _IThcs

Module implementing integration of IT data on health care.

*require*:      :mod:`numpy`, :mod:`pandas`

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Wed Apr 15 00:37:13 2020

#%%

import numpy as np#analysis:ignore
import pandas as pd#analysis:ignore


#%%
    
CC              = 'IT'

# METADATA : will be read from the IThcs.json file


#%%

def prepare_data(self):
    """Prepare IT data. 
    """
	# 
    self.data['id'] = self.data[["Codice Azienda", "Codice struttura", "Subcodice"]].apply(lambda x: '-'.join(x.strip()), axis=1)
    # note: we rename it here, bypassing the JSON file since this is necessary
    # for the next calculation
    self.data.rename(columns={"Totale posti letto": "beds"}, inplace=True)          
    self.data.join(self.data.groupby('id')['beds'].sum(), on='id', rsuffix='_r')
    self.data.rename(columns={"beds_r": "beds"}, inplace=True)          
    self.oindex.update({'id': 'id', 'beds': 'beds'})
