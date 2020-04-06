#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _meta__init

Initialisation module of country metadata configuration programmes.
    
*require*:      :mod:`os`, :mod:`sys`

*optional*:     :mod:`A`

*call*:         :mod:`A`         

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Mon Apr  6 18:30:09 2020

from pyhcs import BASENAME, COUNTRIES#analysis:ignore

# __all__ = ['%s%s' % (cc,BASENAME) for cc in list(COUNTRIES.values())]
__all__ = ['%s%s' % (cc,BASENAME) for cc in ['AT', 'BG', 'CH', 'CZ']]#analysis:ignore

