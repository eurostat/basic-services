#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. __start__

Dumb start of module `pygeofacil`. 
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Wed Apr  1 00:37:42 2020

from sys import path as sysp
from os import path as osp

sysp.insert(0, osp.abspath(__file__))

try:
    import pygeofacil#analysis:ignore
except ImportError:
    raise IOError("environment not set to import 'pygeofacil'")
