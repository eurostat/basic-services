#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _HUhcs

Module implementing integration of HU data on health care.

*require*:      :mod:`numpy`, :mod:`pandas`

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_
# *since*:        Wed Apr 15 00:15:13 2020

#%%

import numpy as np#analysis:ignore
import pandas as pd#analysis:ignore


#%%

CC              = 'HU'

# METADATNAT : will be read from the HUhcs.json file


#%%

def prepare_data(facility): # facility is self when used as a method
    """Prepare HU data.
    * Tel.körzet + Telefonszám => tel
    * droping all empty
    """
    facility.data.dropna(how='all',
                         subset=["Aktív fekvőbeteg-szakellátás",
                                 "Fekvőbeteg-szakellátás",
                                 "Járó és - vagy fekvőbeteg-szakellátás",
                                 # "Járóbeteg-szakellátás"
                                 ], inplace = True)
    facility.data['tel'] = (facility
                            .data[["Tel.körzet", "Telefonszám"]]
                            .apply(lambda x: '-'.join(x), axis=1)
                            )
    facility.oindex.update({'tel': 'tel'})
