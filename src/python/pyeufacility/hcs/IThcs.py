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

# METADATNAT : will be read from the IThcs.json file


#%%

def prepare_data(facility): # facility is self when used as a method
    """Prepare IT data.
    """
    facility.data['id'] = facility.data[["Codice Azienda", "Codice struttura", "Subcodice"]].apply(lambda x: '-'.join(x.strip()), axis=1)
    # note: we rename it here, bypassing the JSON file since this is necessary
    # for the next calculation
    facility.data.rename(columns={"Totale posti letto": "beds"}, inplace=True)
    facility.data.join(facility.data.groupby('id')['beds'].sum(), on='id', rsuffix='_r')
    facility.data.rename(columns={"beds_r": "beds"}, inplace=True)
    facility.oindex.update({'id': 'id', 'beds': 'beds'})
