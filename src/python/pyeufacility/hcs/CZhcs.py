#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _CZhcs

Dumb module implementing integration of CZ data on health care.
    
**Dependencies**

*require*:      :mod:`base`

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Sat Mar 28 17:19:58 2020

#%% 

CC              = 'CZ'

# METADATNAT will be loaded from the CZhcs.json metadata file
#METADATNAT        =  { 'country':     {'code': CC, 'name': 'Czech Republic'},
#                     'lang':        {'code': 'cs', 'name': 'czech'}, 
#                     'proj':        None,
#                     'file':        'export-2020-02.csv',
#                     'path':        '../../../data/raw/',
#                     'enc':         'latin1',
#                     'sep':         ';', 
#                     'date':        '%d-%m-%Y %H:%M',
#                     'columns':     [ 
#                             {'cs': 'ZdravotnickeZarizeniId',        'en': 'Medical devices Id',                'fr': '', 'de': ''},
#                             {'cs': 'PCZ',                           'en': 'PCZ',                               'fr': '', 'de': ''},
#                             {'cs': 'PCDP',                          'en': 'PCDP',                              'fr': '', 'de': ''},
#                             {'cs': 'NazevCely',                     'en': 'Title Cely',                        'fr': '', 'de': ''},
#                             {'cs': 'DruhZarizeni',                  'en': 'Type of device',                    'fr': '', 'de': ''},
#                             {'cs': 'Obec',                          'en': 'Village',                           'fr': '', 'de': ''},
#                             {'cs': 'Psc',                           'en': 'Zip code',                          'fr': '', 'de': ''},
#                             {'cs': 'Ulice',                         'en': 'Street',                            'fr': '', 'de': ''},
#                             {'cs': 'CisloDomovniOrientacni',        'en': 'Indicative house number',           'fr': '', 'de': ''},
#                             {'cs': 'Kraj',                          'en': 'Region',                            'fr': '', 'de': ''},
#                             {'cs': 'KrajCode',                      'en': 'Region Code',                       'fr': '', 'de': ''},
#                             {'cs': 'Okres',                         'en': 'District',                          'fr': '', 'de': ''},
#                             {'cs': 'OkresCode',                     'en': 'District Code',                     'fr': '', 'de': ''},
#                             {'cs': 'SpravniObvod',                  'en': 'Administrative District',           'fr': '', 'de': ''},
#                             {'cs': 'PoskytovatelTelefon',           'en': 'Phone provider',                    'fr': '', 'de': ''},
#                             {'cs': 'PoskytovatelFax',               'en': 'Fax provider',                      'fr': '', 'de': ''},
#                             {'cs': 'DatumZahajeniCinnosti',         'en': 'Launch Date',                       'fr': '', 'de': ''},
#                             {'cs': 'IdentifikatorDatoveSchranky',   'en': 'Identifier data boxes',             'fr': '', 'de': ''},
#                             {'cs': 'PoskytovatelEmail',             'en': 'Email provider',                    'fr': '', 'de': ''},
#                             {'cs': 'PoskytovatelWeb',               'en': 'Web provider',                      'fr': '', 'de': ''},
#                             {'cs': 'PoskytovatelNazev',             'en': 'Title provider',                    'fr': '', 'de': ''},
#                             {'cs': 'Ico',                           'en': 'Ico',                               'fr': '', 'de': ''},
#                             {'cs': 'TypOsoby',                      'en': 'Type Persons',                      'fr': '', 'de': ''},
#                             {'cs': 'PravniFormaKod',                'en': 'Legal form Ko',                     'fr': '', 'de': ''},
#                             {'cs': 'KrajCodeSidlo',                 'en': 'County Seat of Code',               'fr': '', 'de': ''},
#                             {'cs': 'KrajSidlo',                     'en': 'Region of the seat',                'fr': '', 'de': ''},
#                             {'cs': 'OkresCodeSidlo',                'en': 'Seat of District Code',             'fr': '', 'de': ''},
#                             {'cs': 'OkresSidlo',                    'en': 'Seat of district',                  'fr': '', 'de': ''},
#                             {'cs': 'PscSidlo',                      'en': 'Seat of psc',                       'fr': '', 'de': ''},
#                             {'cs': 'ObecSidlo',                     'en': 'Seat of the municipality',          'fr': '', 'de': ''},
#                             {'cs': 'UliceSidlo',                    'en': 'Street seat',                       'fr': '', 'de': ''},
#                             {'cs': 'CisloDomovniOrientacniSidlo',   'en': 'Indicative Seat of House numbers',  'fr': '', 'de': ''},
#                             {'cs': 'OborPece',                      'en': 'Furnace Branch',                    'fr': '', 'de': ''},
#                             {'cs': 'FormaPece',                     'en': 'form Furnaces',                     'fr': '', 'de': ''},
#                             {'cs': 'DruhPece',                      'en': 'Type Furnaces',                     'fr': '', 'de': ''},
#                             {'cs': 'OdbornyZastupce',               'en': 'Professional representative',       'fr': '', 'de': ''},
#                             {'cs': 'GPS',                           'en': 'GPS',                               'fr': '', 'de': ''},
#                             {'cs': 'LastModified',                  'en': 'Last Modified',                     'fr': '', 'de': ''} 
#                             ],
#                     'index':       {
#                             'id':          'Medical devices Id',
#                             'name':        'Medical devices Id',
#                             'site':        'Title Cely',
#                             'lat':         'GPS',
#                             'lon':         'GPS',
#                             'geo_qual':    None,
#                             'street':      'Street',
#                             'number':      'Indicative house number',
#                             'postcode':    'Zip code',
#                             'city':        'Village',
#                             'cc':          'cc',
#                             'country':     'country',
#                             'ER':          None,
#                             'beds':        None,
#                             'prac':        None,
#                             'rooms':       None,
#                             'type':        None,
#                             'PP':          None,
#                             'specs':       None,
#                             'tel':         None,
#                             'email':       None,
#                             'url':         None,
#                             'refdate':     None,
#                             'pubdate':     'Last Modified'
#                             }
#               }    
                 

