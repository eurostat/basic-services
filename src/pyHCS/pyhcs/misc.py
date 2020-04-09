#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _misc

.. Links

.. _happygisco: https://github.com/geopy/geopy
.. |happygisco| replace:: `happygisco <happygisco_>`_
.. _geopy: https://github.com/geopy/geopy
.. |geopy| replace:: `geopy <geopy_>`_
.. _geojson: https://github.com/jazzband/geojson
.. |geojson| replace:: `geojson <geojson_>`_
.. _pyproj: https://github.com/pyproj4/pyproj)
.. |pyproj| replace:: `pyproj <pyproj_>`_
.. _googletrans: https://github.com/ssut/py-googletrans
.. |googletrans| replace:: `googletrans <googletrans_>`_

Module implementing miscenalleous useful methods, including translation and text 
processing.
    
**Dependencies**

*require*:      :mod:`os`, :mod:`six`, :mod:`collections`, :mod:`numpy`, :mod:`pandas`

*optional*:     :mod:`geopy`, :mod:`happygisco`, :mod:`geojson`, :mod:`pyproj`, :mod:`googletrans`

*call*:         :mod:`pyhcs`         

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Thu Apr  9 09:56:45 2020

#%%                

from os import path as osp
import warnings#analysis:ignore

from collections import Mapping, Sequence#analysis:ignore
from six import string_types

from datetime import datetime

import numpy as np#analysis:ignore
import pandas as pd#analysis:ignore

try:                          
    import simplejson as json
except ImportError:
    try:                          
        import json
    except ImportError:
        class json:
            def dump(arg):  
                return '%s' % arg
            def load(arg):  
                with open(arg,'r') as f:
                    return f.read()

try:
    assert False
    import happygisco#analysis:ignore
except (AssertionError,ImportError):
    _is_happy_installed = False
    warnings.warn('! missing happygisco package (https://github.com/eurostat/happyGISCO) - GISCO web services not available !')
else:
    # warnings.warn('! happygisco help: hhttp://happygisco.readthedocs.io/ !')
    _is_happy_installed = True
    from happygisco import services

try:
    import geopy#analysis:ignore 
except ImportError: 
    _is_geopy_installed = False
    warnings.warn('! missing geopy package (https://github.com/geopy/geopy) !')   
else:
    # warnings.warn('! geopy help: http://geopy.readthedocs.io/en/latest/ !')
    _is_geopy_installed = True
    # from geopy import geocoders
    
try:
    assert _is_happy_installed is True or _is_geopy_installed is True
except AssertionError:
    # raise IOError('no geocoding module available')   
    warnings.warn('! no geocoding module available !')   
            
try:
    import pyproj#analysis:ignore 
except ImportError:
    #warnings.warn('! missing pyproj package (https://github.com/pyproj4/pyproj) !')
    _is_pyproj_installed = False
else:
    # warnings.warn('! pyproj help: https://pyproj4.github.io/pyproj/latest/ !')
    _is_pyproj_installed = True
    from pyproj import CRS as crs, Transformer

try:
    import geojson#analysis:ignore 
except ImportError: 
    #warnings.warn('! missing geosjon package (https://github.com/jazzband/geojson) !')   
    _is_geojson_installed = False
else:
    #warnings.warn('! geojson help: https://github.com/jazzband/geojson !')
    _is_geojson_installed = True
    from geojson import Feature, Point, FeatureCollection

try:
    assert True
    import googletrans as gtrans
except (AssertionError,ImportError):
    #warnings.warn('! missing googletrans package (https://github.com/ssut/py-googletrans) - Translations not available !')
    _is_googletrans_installed = False
else:
    # warnings.warn('! googletrans help: https://py-googletrans.readthedocs.io/en/latest !')
    _is_googletrans_installed = True

try:
    assert False # not used: ignore 
    import Levenshtein
except (AssertionError,ImportError):
    _is_levenshtein_installed = False
    # warnings.warn('! missing python-Levenshtein package (http://github.com/ztane/python-Levenshtein) - Text matching not available !')
else:
    # warnings.warn('! Levenshtein help: https://rawgit.com/ztane/python-Levenshtein/master/docs/Levenshtein.html !')
    _is_levenshtein_installed = True

# LATLON        = ['lat', 'lon'] # 'coord' # 'latlon'
# ORDER         = 'lL' # first lat, second Lon 

from pyhcs import EUCOUNTRIES

THISDIR         = osp.dirname(__file__)


#%%
#==============================================================================
# Class GeoProcess
#==============================================================================
    
class GeoProcess(object):
    """Instantiation class for geoprocessing module.
    
        >>> geoproc = GeoProcess()
    """

    __CODERS = {}
    CODERS = __CODERS                                                           \
        .update({'GISCO':           None,  # osm and GISCO) are actually... Nominatim on GISCO servers
                 'osm':             None} if _is_happy_installed else {})           \
        or __CODERS                                                             \
        .update({'GoogleV3':        'api_key', # since July 2018 Google requires each request to have an API key     
                 'Bing':            'api_key', 
                 'GeoNames':        'username', 
                 'Yandex':          'api_key',   
                 'MapQuest':        'key',          
                 'Nominatim':       None, # using Nominatim with the default geopy is strongly discouraged
                 'OpenMapQuest':    'api_key'} if _is_geopy_installed else {})      \
        or __CODERS # at the end, CODERS will be equal to __CODERS after its updates

    # default geocoder... but this can be reset when declaring a subclass
    DEFCODER = {'Bing' : None} # 'GISCO', 'Nominatim', 'GoogleV3', 'GMaps', 'GPlace', 'GeoNames'
    
    PLACE = ['street', 'number', 'postcode', 'city', 'country']
    """Fields used to defined a toponomy (location/place).
    """
            
    #/************************************************************************/
    @classmethod
    def selectCoder(cls, arg):
        """Define geocoder.
        
            >>> coder = GeoProcess.selectCoder(arg)
        """
        #if arg is None:
        #    arg = cls.DEFCODER.copy()
        if not isinstance(arg, (string_types,Mapping)):
            raise TypeError('wrong format for geocoder %s - must be a string or a dictionary' % arg)
        elif isinstance(arg, string_types):
            coder, key = arg, None
        elif isinstance(arg, Mapping):
            coder, key = list(arg.items())
        try:
            assert coder in cls.CODERS 
        except:
            raise IOError('geocoder %s not available/recognised' % coder)
        try:
            assert _is_happy_installed is True or coder.lower() not in ('osm','gisco')
        except:
            try:
                assert _is_geopy_installed is True
            except:     
                raise IOError('no geocoder available')
            else:
                coder, key = 'Bing', None
        return {'coder': coder, cls.CODERS[coder]: key}
    
    #/************************************************************************/
    @classmethod
    def isoCountry(cls, arg):
        """Given a country name or an ISO 3166 code, return the pair {name,code}.
        
            >>> country = GeoProcess.isoCountry(country_or_cc)
                
        Examples
        --------
        
            >>> GeoProcess.isoCountry('CZ')
                {'code': 'CZ', 'country': 'Czechia'}
            >>> GeoProcess.isoCountry('Greece')
                {'code': 'EL', 'country': 'Greece'}
        """
        if not (arg is None or isinstance(arg, (string_types,Mapping))):
            raise TypeError('wrong format for country/code %s - must be a string or a dictionary' % arg)
        elif isinstance(arg, string_types):
            if arg in EUCOUNTRIES.keys():     
                cc, country = arg, None
            elif arg in EUCOUNTRIES.values():
                cc, country = None, arg
            else:
                raise IOError('country/code %s not recognised' % arg)    
        elif isinstance(arg, Mapping):
            cc, country = arg.get('cc', None), arg.get('country', None)
        else:
            country, cc = None, None
        if cc in ('', None) and country in ('', {}, None):
            raise IOError('missing parameters to define country/code')
        elif cc in ('', None): # and NOT country in ('', {}, None)
            try:
                cc = dict(map(reversed, EUCOUNTRIES.items())).get(country)
            except:     
                #cc = country.split()
                #if len(cc) >1:              cc = ''.join([c[0].upper() for c in country.split()])
                #else:                       cc = country # cc[0]
                cc = None
        elif country in ('', {}, None): # and NOT cc in ('', None)
            try:
                country = EUCOUNTRIES.get(cc) 
            except:     country = None
        return {'code': cc, 'name': country}
                    
    #/************************************************************************/
    def __init__(self, *args,  **kwargs):
        try:
            assert _is_happy_installed is True or _is_geopy_installed is True
        except:
            raise ImportError('no instance of %s available' % self.__class__)
        if not args in ((),(None,)):
            coder = args[0]
        else:       
            coder = kwargs.pop('coder', self.DEFCODER) # None
        self.geocoder = self.selectCoder(coder) 
        coder = self.geocoder['coder']
        key = self.CODERS[coder]
        try:
            assert _is_happy_installed is True 
        except: # _is_geopy_installed is True and, hopefully, coder not in ('osm','GISCO')
            if coder.lower() in ('osm','gisco'): 
                raise IOError('geocoder %s not available' % coder)
            try:        
                gc = getattr(geopy.geocoders, coder)   
            except:     
                raise IOError('coder not available')
            else:    
                self.geoserv = gc(**{key: self.geocoder[key]})            
        else:
            if coder.lower() == 'osm':  
                kwargs.pop('exactly_one')
                self.geoserv = services.OSMService()
            elif coder.lower() == 'gisco':  
                kwargs.pop('exactly_one')
                self.geoserv = services.GISCOService()
            else:
                kwargs.pop('exactly_one')
                self.geoserv = services.APIService(**self.geocoder)
        self.crs, self.proj = None, None # no use
    
    #/************************************************************************/
    def __getattr__(self, attr):
        if attr in ('im_class','__objclass__'): 
            return getattr(self.geoserv, '__class__')
        elif attr.startswith('__'):  # to avoid some bug of the pylint editor
            try:        return object.__getattribute__(self, attr) 
            except:     pass 
        try:        return getattr(self.geoserv._gc, attr)
        except:     
            try:        return getattr(self.geoserv._gc, attr)
            except:     raise IOError('attribute %s not available' % attr)

    #/************************************************************************/
    @property
    def geocoder(self):
        return self.__geocoder # or {}
    @geocoder.setter#analysis:ignore
    def geocoder(self, coder):
        if not (coder is None or isinstance(coder, Mapping)):         
            raise TypeError('wrong format for geocoder %s - must be a string' % coder)
        self.__geocoder = coder

    #/************************************************************************/
    def locate(self, *place, **kwargs):
        """Geocoding method.
        
            >>> coord = geoproc.locate(*place, **kwargs)
        """
        try:
            assert _is_happy_installed is True or _is_geopy_installed is True
        except:
            raise ImportError('locate method not available')
        if 'place' in kwargs:
            place = (kwargs.pop('place', ''),)
        kwargs.update({'order': 'lL', 'unique': True, 
                      'exactly_one': True})
        if _is_happy_installed is True:
            if self.geocoder['coder'] in ('osm','GISCO'): 
                kwargs.pop('exactly_one')
            else:
                kwargs.pop('exactly_one')
            return self.geoserv.place2coord(place, **kwargs)
        else: # _is_geopy_installed is True
            kwargs.pop('unique', None) # just drop the key
            order = kwargs.pop('order', 'lL')
            loc = self.geoserv.geocode(place, **kwargs) # self.geoserv._gc.geocode(place, **kwargs)
            lat, lon = loc.get('latitude'), loc.get('longitude')
            return [lat,lon] if order == 'lL' else [lon, lat] 
        
    #/************************************************************************/
    def project(self, *coord, **kwargs):
        """Projection method. 
        
            >>> ncoord = geoproc.project(coord, iproj='WGS84', oproj='WGS84')
        """
        try:
            assert _is_happy_installed is True or _is_pyproj_installed is True
        except:
            raise ImportError('project method not available')
        if 'lat' in kwargs and 'lon' in kwargs:
            coord = ([kwargs.pop('lat', None), kwargs.pop('lon', None)],)
        if coord  in ((),(None,)):
            raise IOError('no lat/lon coordinates parsed')
        elif not all([isinstance(c, Sequence) for c in coord]):
            raise TypeError('wrong lat/lon coordinates parsed')
        iproj = kwargs.pop('iproj', 'WGS84')
        if not isinstance(iproj, (string_types, int)):
            raise TypeError("input projection %s not recognised - must be a string (e.g., 'WGS84' or 'EPSG:4326') or an integer (e.g., 4326)" % iproj)
        oproj = kwargs.pop('oproj', 'WGS84')
        if not isinstance(oproj, (string_types, int)):
            raise TypeError("output projection %s not recognised - must be a string (e.g., 'WGS84' or 'EPSG:4326') or an integer (e.g., 4326)" % oproj)
        if iproj == oproj:
            return coord
        try:
            # assert _is_happy_installed is True
            return self.geoserv.coordproject(coord, iproj=iproj, oproj=oproj)
        except:
            try:
                # assert _is_pyproj_installed is True
                CRS = crs.from_epsg(oproj)
                return Transformer.from_crs(CRS.from_epsg(iproj), CRS).transform(*coord)
            except:
                raise IOError('projection of coordinates failed...')

#%%
#==============================================================================
# Class IOProcess
#==============================================================================
    
class IOProcess(object):
    """Static methods for Input/Output file and data processing, e.f. writing
    into a table.
    """

    #/************************************************************************/
    @staticmethod
    def to_date(df, column, ofmt, ifmt='%d-%m-%Y %H:%M'): # ofmt='%d/%m/%Y'
        """Cast the column of a dataframe into datetime.
        """
        try:
            assert column in df.columns
        except:
            raise IOError('wrong input column - most be in the dataframe')
        try:
            assert (ofmt is None or isinstance(ofmt, string_types)) and     \
                isinstance(ifmt, string_types) 
        except:
            raise TypeError('wrong format for input date templates')
        if ofmt in (None,'') or ofmt == '':
            return df[column].astype(str)    
        else:            
            try:
                f = lambda s: datetime.strptime(s, ifmt).strftime(ofmt)
                return df[column].astype(str).apply(f)
            except:
                return df[column].astype(str)    
                    
    #/************************************************************************/
    @staticmethod
    def to_cast(df, column, cast):
        """Cast the column of a dataframe into special format, excluding datetime.
        """
        try:
            assert column in df.columns
        except:
            raise IOError('wrong input column - most be in the dataframe')
        try:
            assert isinstance(cast, type)
        except:
            raise TypeError('wrong format for input cast type')
        if cast == df[column].dtype:
            return df[column]
        else:
            try:
                return df[column].astype(cast)
            except:
                return df[column].astype(object)
                
    #/************************************************************************/
    @staticmethod
    def to_json(df, columns=None):
        """JSON output formatting.
        """
        try:
            assert columns is None or isinstance(columns, string_types)     or \
                (isinstance(columns, Sequence) and all([isinstance(c,string_types) for c in columns]))
        except:
            raise IOError('wrong format for input columns')
        if isinstance(columns, string_types):
            columns == [columns,]
        if columns in (None,[]):
            columns = df.columns
        columns = list(set(columns).intersection(df.columns))
        return df[columns].to_dict('records') 

    #/************************************************************************/
    @staticmethod
    def to_geojson(df, columns=None, latlon=['lat', 'lon']):
        """GEOsJSON output formatting.
        """
        try:
            assert columns is None or isinstance(columns, string_types)     or \
                (isinstance(columns, Sequence) and all([isinstance(c,string_types) for c in columns]))
        except:
            raise IOError('wrong format for input columns')
        try:
            lat, lon = latlon
            assert isinstance(lat, string_types) and isinstance(lon, string_types)
        except:
            raise TypeError('wrong format for input lat/lon columns')
        if isinstance(columns, string_types):
            columns == [columns,]
        if columns in (None,[]):
            columns = list(set(df.columns))
        columns = list(set(columns).intersection(set(df.columns)).difference(set([lat,lon])))
        if _is_geojson_installed is True: 
            features = df.apply(
                    lambda row: Feature(geometry=Point((float(row[lon]), float(row[lat])))),
                    axis=1).tolist() 
            properties = df[columns].to_dict('records') # columns used as properties
            # properties = df.drop([lat, lon], axis=1).to_dict('records')
            geom = FeatureCollection(features=features, properties=properties)
        else:
            geom = {'type':'FeatureCollection', 'features':[]}
            for _, row in df.iterrows():
                feature = {'type':'Feature',
                           'properties':{},
                           'geometry':{'type':'Point',
                                       'coordinates':[]}}
                feature['geometry']['coordinates'] = [float(row[lon]), float(row[lat])]
                for col in columns:
                    feature['properties'][col] = row[col]
                geom['features'].append(feature)
        return geom
    
    #/************************************************************************/
    @staticmethod
    def to_gpkg(df, columns=None):
        """
        """
        warnings.warn('! method for gpkg not implemented !')
        pass
                    
    #/************************************************************************/
    def __init__(self,*args,  **kwargs):
        # no instance defined
        pass

    
#%%
#==============================================================================
# Class TextProcess
#==============================================================================
    
class TextProcess(object):
    """Static and class methods for text processing and translation.
    """
    
    LANGS = { ## alpha-3/ISO 639-2 codes
            'sq': 'albanian',
            'ar': 'arabic',
            'hy': 'armenian',
            'az': 'azerbaijani',
            'eu': 'basque',
            'be': 'belarusian',
            'bs': 'bosnian',
            'bg': 'bulgarian',
            'ca': 'catalan',
            'co': 'corsican',
            'hr': 'croatian',
            'cs': 'czech',
            'da': 'danish',
            'nl': 'dutch',
            'en': 'english',
            'eo': 'esperanto',
            'et': 'estonian',
            'fi': 'finnish',
            'fr': 'french',
            'fy': 'frisian',
            'gl': 'galician',
            'ka': 'georgian',
            'de': 'german',
            'el': 'greek',
            'hu': 'hungarian',
            'is': 'icelandic',
            'ga': 'irish',
            'it': 'italian',
            'la': 'latin',
            'lv': 'latvian',
            'lt': 'lithuanian',
            'lb': 'luxembourgish',
            'mk': 'macedonian',
            'mt': 'maltese',
            'no': 'norwegian',
            'pl': 'polish',
            'pt': 'portuguese',
            'ro': 'romanian',
            'ru': 'russian',
            'gd': 'scots gaelic',
            'sr': 'serbian',
            'sk': 'slovak',
            'sl': 'slovenian',
            'es': 'spanish',
            'sv': 'swedish',
            'tr': 'turkish',
            'uk': 'ukrainian',
            'cy': 'welsh'
            }
    # CODELANGS = dict(map(reversed, LANGS.items())) # {v:k for (k,v) in LANGS.items()}
    
    DEFLANG = 'en'

    try:
        assert _is_googletrans_installed is True
        UTRANSLATOR = gtrans.Translator() # parameter independent: we use a class variable
    except:     pass
   
    #/************************************************************************/
    @classmethod
    def isoLang(cls, arg):
        """Given a language or an ISO 639 locale code, return the pair {language,locale}.
        
            >>> TextProcess.isoLang(locale_or_language)
        """
        if not (arg is None or isinstance(arg, (string_types,Mapping))):
            raise TypeError('wrong format for language/locale %s - must be a string or a dictionary' % arg)
        elif isinstance(arg, string_types):
            if arg in cls.LANGS.keys(): 
                language, locale = None, arg 
            elif arg in cls.LANGS.values():
                language, locale = arg, None
            else:
                raise IOError('language/locale %s not recognised' % arg)    
        elif isinstance(arg, Mapping):
            locale, language = arg.get('code', None), arg.get('name', None)
        else: # lang is None
            language, locale = None, None
        if locale in ('', None) and language in ('', None):
            try:
                lang = {'code': cls.DEFLANG, 'name': cls.LANGS[cls.DEFLANG]} # not implemented
            except:     language, locale = None, None
            else:
                language, locale = lang.get('code',None), lang.get('name',None)
        elif locale in ('', None): # and NOT language in ('', None)
            try:
                locale = dict(map(reversed, cls.LANGS.items())).get(language)
            except:     locale = None
        elif language in ('', None): # and NOT locale in ('', None)
            try:
                language = cls.LANGS.get(locale)
            except:     language = None
        return {'code': locale, 'name': language}
    
    #/************************************************************************/
    @classmethod
    def detectLang(cls, *text, **kwargs):
        """Language detection method.
        
            >>> TextProcess.detect(*text, **kwargs)
        """
        try:
            assert _is_googletrans_installed is True
        except:
            raise ImportError('detect method not available')
        text = (text not in ((None,),()) and text[0])               or \
                kwargs.pop('text', '')                                
        if isinstance(text, string_types):
            text = [text,]
        if isinstance(text, Sequence) and all([isinstance(t, string_types) for t in text]):
            pass
        elif text in (None,(),''):
            return
        else:
            raise TypeError('wrong format for input text')
        return [r['lang'] for r in cls.UTRANSLATOR.detect(text)]
    
    #/************************************************************************/
    @classmethod
    def translate(cls, *text, **kwargs):
        """Translation method.
        
            >>> TextProcess.translate(*text, **kwargs)
        """
        try:
            assert _is_googletrans_installed is True
        except:
            raise ImportError('translate method not available')
        text = (text not in ((None,),()) and text[0])               or \
                kwargs.pop('text', '')                                
        if isinstance(text, string_types):
            text = [text,]
        if isinstance(text, Sequence) and all([isinstance(t, string_types) for t in text]):
            pass
        elif text in (None,(),''):
            return
        else:
            raise TypeError('wrong format for input text')
        ilang, olang = kwargs.pop('ilang', None), kwargs.pop('olang', cls.DEFLANG)
        if not (isinstance(ilang, string_types) and isinstance(olang, string_types)):
            raise TypeError('languages not recognised')
        if 'filt' in kwargs:
            f = kwargs.get('filt')
            try:                    assert callable(f)
            except AssertionError:  pass
            else:   
                text = [f(t) for t in text]
        if ilang == olang or text == '':
            return text
        return [t.text for t in cls.UTRANSLATOR.translate(text, src=ilang, dest=olang)]
            
    #/************************************************************************/
    @staticmethod
    def match_close(t1, t2, dist='jaro_winkler'):
        """Text matching method.
        """
        try:
            assert _is_levenshtein_installed is True
        except:
            raise ImportError('closest method not available')
        try:
            distance = getattr(Levenshtein,dist)
        except AttributeError:
            raise AttributeError('Levenshtein distance %s not recognised' % distance)
        else: 
            return distance(t1.str.upper().str, t2) 

    #/************************************************************************/
    @staticmethod
    def split_at_upper(s, contiguous=True):
        """Text splitting method.
        
        Description
        -----------
        Split a string at uppercase letters
        """
        strlen = len(s)
        lower_around = (lambda i: s[i-1].islower() or strlen > (i + 1) and s[i + 1].islower())
        start, parts = 0, []
        for i in range(1, strlen):
            if s[i].isupper() and (not contiguous or lower_around(i)):
                parts.append(s[start: i])
                start = i
        parts.append(s[start:])    
        return (" ").join(parts)
                    
    #/************************************************************************/
    def __init__(self,*args,  **kwargs):
        # no instance defined
        # self.translator = 
        pass

