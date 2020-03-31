#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. _base

.. Links

.. _Eurostat: http://ec.europa.eu/eurostat/web/main
.. |Eurostat| replace:: `Eurostat <Eurostat_>`_
.. _healthcare: https://github.com/eurostat/healthcare-services
.. |healthcare| replace:: `healthcare services data <healthcare_>`_
.. _GISCO: https://github.com/eurostat/happyGISCO
.. |GISCO| replace:: `GISCO <GISCO_>`_
.. _happygisco: https://github.com/geopy/geopy
.. |happygisco| replace:: `happygisco <happygisco_>`_
.. _geopy: https://github.com/geopy/geopy
.. |geopy| replace:: `geopy <geopy_>`_
.. _geojson: https://github.com/jazzband/geojson
.. |geojson| replace:: `geojson <geojson_>`_

Module enabling the integration of data on Health Care Services (e.g., facilities
like hospitals or clinics) collected from Member States into pan-European harmonised 
format.

**Dependencies**

*require*:      :mod:`os`, :mod:`six`, :mod:`collections`, :mod:`functools`, :mod:`copy`, 
                :mod`datetime`, :mod:`numpy`, :mod:`pandas`

*optional*:     :mod:`geopy`, :mod:`happygisco`, :mod:`geojson`

**Contents**
"""

# *credits*:      `gjacopo <jacopo.grazzini@ec.europa.eu>`_ 
# *since*:        Tue Fri 20 23:14:24 2020

#%%                

from os import path as osp
import warnings#analysis:ignore

from collections import Mapping, Sequence
from six import string_types

from functools import reduce
from copy import deepcopy
# import itertools

from datetime import datetime

import numpy as np#analysis:ignore
import pandas as pd

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
    warnings.warn('missing happygisco package (https://github.com/eurostat/happyGISCO) - GISCO web services not available')
else:
    # warnings.warn('happygisco help: hhttp://happygisco.readthedocs.io/')
    _is_happy_installed = True
    from happygisco import services

try:
    import geopy#analysis:ignore 
except ImportError: 
    _is_geopy_installed = False
    warnings.warn('missing geopy package (https://github.com/geopy/geopy)')   
else:
    # warnings.warn('geopy help: http://geopy.readthedocs.io/en/latest/')
    _is_geopy_installed = True
    # from geopy import geocoders
    
try:
    assert _is_happy_installed is True or _is_geopy_installed is True
except AssertionError:
    # raise IOError('no geocoding module available')   
    warnings.warn('no geocoding module available')   
else:
    CODERS = {'GISCO':          None,              
                'osm':          None, # note: osm and GISCO) are actually... Nominatim on GISCO servers
                'GoogleV3':     None,           
                'Bing':         'api_key',          
                'GeoNames':     'username', 
                'Yandex':       'api_key',   
                'MapQuest':     'key',          
                'Nominatim':    None,
                'OpenMapQuest': 'api_key' 
             }      
    if _is_happy_installed is True:
        if _is_geopy_installed is False:
            CODERS.pop('GoogleV3'); CODERS.pop('Bing')         
            CODERS.pop('GeoNames'); CODERS.pop('Yandex')         
            CODERS.pop('MapQuest'); CODERS.pop('Nominatim')         
            CODERS.pop('OpenMapQuest')               
        pass
    else:
        CODERS.pop('GISCO'); CODERS.pop('osm')         
        class _GEOCODER(object):
            def __init__(self, **kwargs):
                self._gc = None
                coder = kwargs.pop('coder', 'GeoNames')
                if coder not in CODERS.keys():
                    raise IOError('geocoder %s not recognised' % coder)
                try:        gc = getattr(geopy.geocoders, coder)   
                except:     raise IOError('module geopy not available')
                key = CODERS[coder]
                if key is not None:          
                    self.client_key = kwargs.pop(key,None)
                    kwargs.update({key: self.client_key})
                else:   
                    self.client_key = None                
                try:    self._gc = gc(**kwargs)  
                except: raise IOError('geocoder not available')
            def __getattr__(self, method):
                if method in ('im_class','__objclass__'): 
                    return getattr(self._gc, '__class__')
                elif method.startswith('__'):  # to avoid some bug of the pylint editor
                    try:        return object.__getattribute__(self, method) 
                    except:     pass 
                try:        return getattr(self._gc, method)
                except:     raise IOError('method %s not implemented' % method)
            def place2coord(self, *args, **kwargs):
                return self.geocode(*args, **kwargs) # self._gc.geocode(*args, **kwargs)

try:
    import pyproj#analysis:ignore 
except ImportError:
    #warnings.warn('missing pyproj package (https://github.com/pyproj4/pyproj)')
    _is_pyproj_installed = False
else:
    # warnings.warn('pyproj help: https://pyproj4.github.io/pyproj/latest/')
    _is_pyproj_installed = True
    from pyproj import CRS, Transformer

try:
    import geojson
except ImportError: 
    #warnings.warn('missing geosjon package (https://github.com/jazzband/geojson)')   
    _is_geojson_installed = False
else:
    #warnings.warn('geojson help: https://github.com/jazzband/geojson')
    _is_geojson_installed = True
    from geojson import Feature, Point, FeatureCollection

try:
    assert True
    import googletrans as gtrans
except (AssertionError,ImportError):
    #warnings.warn('missing googletrans package (https://github.com/ssut/py-googletrans) - Translations not available')
    _is_googletrans_installed = False
else:
    # warnings.warn('googletrans help: https://py-googletrans.readthedocs.io/en/latest')
    _is_googletrans_installed = True

try:
    assert False # not used: ignore 
    import Levenshtein
except (AssertionError,ImportError):
    _is_levenshtein_installed = False
    # warnings.warn('missing python-Levenshtein package (http://github.com/ztane/python-Levenshtein) - Text matching not available')
else:
    # warnings.warn('Levenshtein help: https://rawgit.com/ztane/python-Levenshtein/master/docs/Levenshtein.html')
    _is_levenshtein_installed = True

from .config import IPATH, OINDEX, ODATE, OLANG, OSEP, OENC, \
                    OPATH, OFILE, OFMT, OPROJ, IPLACE

try:
    assert _is_pyproj_installed is True
    OCRS = CRS.from_epsg(OPROJ or 4326)
except:
    OCRS = None

#%%
#==============================================================================
# Class MetaHCS
#==============================================================================

class MetaHCS(dict):
    """Generic class used to represent metadata instances as dictionary.
    
        >>> meta = MetaHCS(**metadata)
    """

    #/************************************************************************/
    def __init__(self, *args, **kwargs):
        if not args in ((),(None,)):
            try:
                meta = deepcopy(args[0]) # deepcopy to avoid updating the default variables!!!
            except AttributeError:
                meta = args[0]
        else:       
            meta = {}
        if isinstance(meta, string_types):
            if not osp.exists(meta):
                raise IOError('input metadata filename %s not recognised' % meta)
            try:
                with open(meta, 'rt') as f:
                    meta = json.load(f)#analysis:ignore
            except:
                raise TypeError('input metadata file %s must be in JSON format' % meta)
        elif not isinstance(meta, Mapping):
            raise TypeError('input metadata format not recognised - must be a mapping dictionary or a string')
        if not kwargs is {}:
            meta.update(deepcopy(kwargs))            
        super(MetaHCS,self).__init__(self, **meta)
        self.__dict__ = self

    #/************************************************************************/
    def copy(self, *args, **kwargs): # actually new object, like a deepcopy...
        return self.__class__(**self.__dict__)

    #/************************************************************************/
    def __repr__(self):
        return "<{} metadata instance at {}>".format(self.__class__.__name__, id(self))
    def __str__(self):    
        keys = list(self.keys())
        l = max([len(k) for k in keys])
        return reduce(lambda x,y:x+y, ["{} : {}\n".format(k.ljust(l),getattr(self,k))
            for k in keys if self.get(k) not in ('',None)])    

    #/************************************************************************/
    def __getattr__(self, attr):
        if attr.startswith('__'):
            try:        nattr = attr[2:-2]
            except:     nattr = None
        else:
            nattr = attr
        if nattr in self.keys():  
            r = self.get(nattr)
        else:
            try:        object.__getattribute__(self, attr) 
            except:     pass
            r = None
        return r

    
#%%
#==============================================================================
# Class BaseHCS
#==============================================================================

class BaseHCS(object):
    """Base class used to represent health care data sources.
    
        >>> hcs = BaseHCS(**metadata)
    """
    
    METAKEYS        = ['country', 'lang', 'proj', 'file', 'path', 'enc', 'sep', 
                       'columns', 'index'] # default metadata fields

    # default geocoder... but this can be reset when declaring a subclass
    CODER           = 'Bing' # 'GISCO', 'Nominatim', 'GoogleV3', 'GMaps', 'GPlace', 'GeoNames'
    CODERKEY        = None # enter your key here...
        
    try:
        assert _is_happy_installed is True
        OSMSERV = services.OSMService()
        GISCOSERV = services.GISCOService()
    except:     pass

    try:
        assert _is_happy_installed is True
        GEOSERV = services.APIService(**{'coder': CODER, CODERS[CODER]: CODERKEY})
    except:     
        try:
            assert _is_geopy_installed is True
        except:     pass
        else:
            GEOSERV = _GEOCODER(**{'coder': CODER, CODERS[CODER]: CODERKEY})

    try:
        assert _is_googletrans_installed is True
        UTRANSLATOR = gtrans.Translator()
    except:     pass
            
    #/************************************************************************/
    @classmethod
    def locate(cls, *place, **kwargs):
        """Geocoding method.
        """
        try:
            assert _is_happy_installed is True or _is_geopy_installed is True
        except:
            raise ImportError('locate method not available')
        coder = kwargs.pop('coder', None) or cls.CODER
        if not isinstance(coder, string_types):     
             raise TypeError('wrong format for geocoder - must be a string')
        elif not coder in CODERS:
            raise IOError('geocoder %s not available' % coder)
        if 'place' in kwargs:
            place = (kwargs.pop('place', ''),)
        if _is_happy_installed and coder in ('osm','GISCO'): 
            kwargs.update({'order': 'lL', 'unique': True})
            if coder == 'osm':  s = cls.OSMSERV
            else:               s = cls.GISCOSERV
        else:
            kwargs.update({'exactly_one': True})
            s = cls.GEOSERV
        return s.place2coord(place, **kwargs)
        
    #/************************************************************************/
    @classmethod
    def project(cls, *coord, **kwargs):
        """Projection method. 
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
        iproj = kwargs.pop('iproj', None) or 'WGS84'
        if not isinstance(iproj, (string_types, int)):
            raise TypeError("projection not recognised - must be a string (e.g., 'WGS84' or 'EPSG:4326') or an integer (e.g., 4326)")
        oproj = OPROJ or 'WGS84'
        if iproj == oproj:
            return coord
        if _is_happy_installed is True: 
            return cls.GISCOSERV.coordproject(coord, iproj=iproj, oproj=oproj)
        else:
            return Transformer.from_crs(CRS.from_epsg(iproj), OCRS).transform(*coord)
    
    #/************************************************************************/
    @classmethod
    def translate(cls, *text, **kwargs):
        """Translation method.
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
        ilang, olang = kwargs.pop('ilang', None), kwargs.pop('olang', OLANG)
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
    @classmethod
    def detect(cls, *text, **kwargs):
        """Language detection method.
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
    @staticmethod
    def textmatch(t1, t2, dist='jaro_winkler'):
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
    def textsplit(s, contiguous=True):
        """Text splitting method.
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
    @staticmethod
    def to_cast(df, column, cast, ifmt='%d-%m-%Y %H:%M', ofmt='%d/%m/%Y'):
        """Cast the column of a dataframe into special format, including datetime.
        """
        try:
            assert column in df.columns
        except:
            raise IOError('wrong input column - most be in the dataframe')
        try:
            assert isinstance(cast, type)
        except:
            raise TypeError('wrong format for input cast type')
        try:
            assert isinstance(ifmt, string_types) and isinstance(ofmt, string_types)
        except:
            raise TypeError('wrong format for input date templates')
        if cast == df[column].dtype:
            return df[column]
        elif cast == datetime:
            try:
                f = lambda s: datetime.strptime(s, ifmt).strftime(ofmt)
                return df[column].apply(f)
            except:
                return df[column]                
        else:
            try:
                return df[column].astype(cast)
            except:
                return df[column].astype(object)
                
    #/************************************************************************/
    @staticmethod
    def to_json(df, columns):
        """JSON output formatting.
        """
        try:
            assert isinstance(columns, Sequence) and all([isinstance(c,string_types) for c in columns])
        except:
            raise IOError('wrong format for input columns')
        if columns == []:
            columns = df.columns
        columns = list(set(columns).intersection(df.columns))
        return df[columns].to_dict('records') 

    #/************************************************************************/
    @staticmethod
    def to_geojson(df, columns, latlon=['lat', 'lon']):
        """GEOsJSON output formatting.
        """
        if not (isinstance(columns, Sequence) and all([isinstance(c,string_types) for c in columns])):
            raise TypeError('wrong format for input columns')
        try:
            lat, lon = latlon
            assert isinstance(lat, string_types) and isinstance(lon, string_types)
        except:
            raise TypeError('wrong format for input lat/lon columns')
        if columns == []:
            columns = list(set(df.columns)).difference(set([lat,lon]))
        columns = list(set(columns).intersection(df.columns))
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
    def to_gpkg(df, columns):
        """
        """
        warnings.warn('method for gpkg not implemented')
        pass
    
    #/************************************************************************/
    def __init__(self, **kwargs):
        self.__data = None                # data
        self.__place = ''                 # key field to store a place                              
        self.__latlon = ['', '']          # key fields for lat/lon coordinates
        try:
            # meta should be initialised in the derived class
            assert getattr(self, 'meta', None) not in ({},None)
        except AssertionError:
            self.meta = dict(zip(self.METAKEYS, [{}, {}, None, '', '', None, ',', [], {}]))
        country, lang = self.meta.get('country',None), self.meta.get('lang',None)
        self.cc = kwargs.pop('cc', country.get('code', '') if country is not None else None)
        self.country = kwargs.pop('country', country.get('name', '') if country is not None else None)
        self.lang = kwargs.pop('lang', lang.get('code', None) if lang is not None else None) 
        self.enc, self.sep = self.meta.get('enc',None), self.meta.get('sep',None)
        path, fname = self.meta.get('path',IPATH), self.meta.get('file','')
        self.src = kwargs.pop('src', 
                              None if fname=='' else osp.join(path, fname) if path!='' else fname) # source file
        self.proj = kwargs.pop('proj', self.meta.get('proj',None)) # projection system
        self.date = kwargs.pop('date', self.meta.get('date','%d-%m-%Y %H:%M')) # input date format
        columns = kwargs.pop('columns', None) # [col[self.lang] for col in COLUMNS]
        self.icolumns = columns or self.meta.get('columns',[])     # header columns
        index = kwargs.pop('index', None)   # index
        self.oindex = index or self.meta.get('index',{}) or OINDEX.keys()

    #/************************************************************************/
    def __repr__(self):
        return "<{} data instance at {}>".format(self.__class__.__name__, id(self))
    def __str__(self):    
        keys = ['cc', 'country', 'file']
        l = max([len(k) for k in keys])
        return reduce(lambda x,y:x+y, ["{} : {}\n".format(k.ljust(l),getattr(self,k))
            for k in keys if self.get(k) not in ('',None)])    

    #/************************************************************************/
    def __getattr__(self, attr):
            try:        return object.__getattribute__(self, attr) 
            except AttributeError: 
                try:
                    # assert attr in self.meta
                    return object.__getattribute__(self, '__' + attr)
                except (AttributeError,AssertionError): 
                    try:
                        assert False
                        # return getattr(self.__class__, attr)
                    except AssertionError:
                        raise AttributeError ("'%s' object has no attribute %s" % (type(self),attr))

    #/************************************************************************/
    @property
    def meta(self):
        return self.__metadata # or {}
    @meta.setter#analysis:ignore
    def meta(self, meta):
        if not (meta is None or isinstance(meta, Mapping)):         
            raise TypeError('wrong format for country code %s - must be a string' % meta)
        self.__metadata = meta

    @property
    def cc(self):
        return self.__cc
    @cc.setter#analysis:ignore
    def cc(self, cc):
        if not (cc is None or isinstance(cc, string_types)):         
            raise TypeError('wrong format for country code %s - must be a string' % cc)
        # self.meta['country'].update({'code': cc})
        self.__cc = cc

    @property
    def country(self):
        return self.__country
    @country.setter#analysis:ignore
    def country(self, ctry):
        if not (ctry is None or isinstance(ctry, string_types)):         
            raise TypeError('wrong format for country %s - must be a string' % ctry)
        # self.meta['country'].update({'name': ctry})
        self.__country = ctry

    @property
    def lang(self):
        return self.__lang
    @lang.setter#analysis:ignore
    def lang(self, lang):
        if not (lang is None or isinstance(lang, string_types)):         
            raise TypeError('wrong format for language type %s - must be a string' % lang)
        # self.meta.update({'lang': lang})
        self.__lang = lang

    @property
    def src(self):
        return self.__src
    @src.setter#analysis:ignore
    def src(self, src):
        if not (src is None or isinstance(src, string_types)):         
            raise TypeError('wrong format for source filename %s - must be a string' % src)
        # self.meta.update({'src': src})
        self.__src = src

    @property
    def proj(self):
        return self.__proj
    @proj.setter#analysis:ignore
    def proj(self, proj):
        if not (proj is None or isinstance(proj, string_types)):         
            raise TypeError('wrong format for projection type %s - must be a string' % proj)
        # self.meta.update({'proj': proj})
        self.__proj = proj

    @property
    def icolumns(self):
        return self.__columns  # self.meta.get('columns')
    @icolumns.setter#analysis:ignore
    def icolumns(self, cols):
        if cols is None:                        
            pass # nothing yet
        elif isinstance(cols, Mapping):
            cols = [cols,]
        elif isinstance(cols, Sequence) and all([isinstance(col, string_types) for col in cols]):
            cols = [{self.lang: col} for col in cols]
        elif not(isinstance(cols, Sequence) and all([isinstance(col, Mapping) for col in cols])): 
            raise TypeError('wrong input column headers type %s - must be a sequence of dictionaries' % cols)
        # self.meta.update({'columns': cols})
        self.__columns = cols

    @property
    def oindex(self):
        return self.__index  # self.meta.get('index')
    @oindex.setter#analysis:ignore
    def oindex(self, ind):
        if ind is None:                        
            pass # nothing yet
        elif isinstance(ind, Sequence):
            ind = dict.fromkeys(ind)
        elif not isinstance(ind, Mapping):
            raise TypeError('wrong output index type %s - must be a dictionary' % ind)
        # self.meta.update({'index': ind})
        self.__index = ind

    @property
    def sep(self):
        return self.__sep
    @sep.setter#analysis:ignore
    def sep(self, sep):
        if not (sep is None or isinstance(sep, string_types)):         
            raise TypeError('wrong format for separator %s - must be a string' % sep)
        # self.meta.update({'sep': sep})
        self.__sep = sep

    @property
    def enc(self):
        return self.__encoding
    @enc.setter#analysis:ignore
    def enc(self, enc):
        if not (enc is None or isinstance(enc, string_types)):         
            raise TypeError('wrong format for file encoding %s - must be a string' % enc)
        # self.meta.update({'enc': enc})
        self.__encoding = enc

    @property
    def place(self):
        return self.__place
    @place.setter#analysis:ignore
    def place(self, place):
        if place is None:                        
            pass # nothing yet
        elif isinstance(place, string_types):
            pass # place = [place,]
        elif not(isinstance(place, Sequence) and all([isinstance(p, string_types) for p in place])):
            raise TypeError('wrong input format for place - must be a (list of) string(s) or a mapping dictionary')            
        self.__place = place

    #/************************************************************************/
    def load_data(self, *src, **kwargs):
        """Load data source file.
        
                >>> hcs.load_data(src='filename')
        """
        src = (src not in ((None,),()) and src[0])                  or \
             kwargs.pop('src', None)                                or \
             self.src                                               
        if src in (None,''):     
             raise IOError("no source filename provided - set 'src' attribute or parameter")
        elif not isinstance(src, string_types):     
             raise TypeError('wrong format for source filename - must be a string')
        encoding = kwargs.pop('enc', self.enc) # self.meta.get('enc')
        sep = kwargs.pop('sep', self.sep) # self.meta.get('sep')
        kwargs.update({'dtype': object})
        #try:
        #    kwargs.update(self.load_data.__dict__)
        #except:         pass
        try:
            kwargs.update({'encoding': encoding, 'sep': sep})
            self.data = pd.read_csv(src, **kwargs)
        except FileNotFoundError:            
            raise FileNotFoundError('impossible to load source data - file %s not found' % self.src)
        except:
            kwargs.pop('encoding'); kwargs.pop('sep')
            try:
                self.data = pd.read_excel(src, **kwargs)
            except:
                #try:
                #    self.data = pd.read_json(src, **kwargs)
                #except:
                try:
                    kwargs.update({'encoding': encoding, 'sep': sep, 'compression': 'infer'})
                    self.data = pd.read_table(src, **kwargs)
                except:
                    raise IOError('impossible to load source data - format not recognised')
            else:
                self.enc, self.sep = encoding, sep
        else:
            self.enc, self.sep = encoding, sep
        # initialise the column header in case it was not passed in the metadata
        try:
            assert self.columns not in (None,[],[{}])
        except: 
            self.columns = [{self.lang:col} for col in self.data.columns]
        #if set([col[self.lang] for col in self.icolumns]).difference(set(self.data.columns)) != set():
        #    warnings.warn('mismatched data columns and header fields')
        if self.src != src:            self.src = src
        
    #/************************************************************************/
    def get_column(self, *columns, **kwargs):
        """Retrieve the name of the column associated to a given field (e.g., manually
        defined), depending on the language.
        
                >>> hcs.get_column(columns=['col1', 'col2'])
        """
        columns = (columns not in ((None,),()) and columns[0])      or \
                    kwargs.pop('columns', None)                                 
        if columns in (None, ()):
            pass # will actually return all columns in that case
        elif isinstance(columns, string_types):     
            columns = (columns,)
        if not (isinstance(columns, Sequence) and all([isinstance(col, string_types) for col in columns])):   
             raise TypeError('wrong input format for columns - must be a (list of) string(s)')
        langs = self.icolumns[0].keys()
        langs = list(dict.fromkeys([OLANG, *langs])) # trick to reorder with OLANG first default... 
        ilang = kwargs.pop('ilang', None) # OLANG
        if ilang is None and not columns in (None, ('',), ()):
            # try to guess the language in the index
            #for ilang in langs:
            #    try:
            #        assert set(columns).difference([col[ilang] for col in self.icolumns]) == set()
            #    except:    continue
            #    else:      break
            f = lambda text : self.detect(text)
            try:                        assert False and f(-1)
            except TypeError:
                ilang = self.detect((' ').join(columns.values()))
            else:
                ilang = OLANG
        try:
            assert ilang in langs
        except AssertionError:
            raise IOError('input column(s) not recognised')            
        olang = kwargs.pop('olang', self.lang)
        try:
            assert olang in langs
        except AssertionError:
            f = lambda cols: self.translate(cols, ilang=self.lang, olang=olang)
            try:                    f(-1)#analysis:ignore
            except TypeError:
                tcols = f([col[self.lang] for col in self.icolumns])
                [col.update({olang: t}) for (col,t) in zip(self.icolumns, tcols)]
            except ImportError:     
                pass
        except KeyError:
             pass # raise IOError('no columns available')
        if columns in (None, ('',), ()): # return all translations
            return [col[olang] for col in self.icolumns]
        ncolumns = {}
        [ncolumns.update({col[ilang]: col.pop(ilang) and col})    \
                         for col in [col.copy() for col in self.icolumns]]
        res = [ncolumns[col][olang] if col in ncolumns.keys() else None for col in columns]
        return res if len(res)>1 else res[0]

    #/************************************************************************/
    def set_column(self, *columns, **kwargs):
        """Rename (and cast) the column associated to a given field (e.g., as identified
        in the index), depending on the language.
        
                >>> hcs.set_column(columns={'newcol': 'oldcol'})
        """
        columns = (columns not in ((None,),()) and columns[0])        or \
                    kwargs.pop('columns', None)                     
        if columns in (None, ()):
            columns = {}  # will actually set all columns in that case
        elif not isinstance(columns, Mapping):
            raise TypeError('wrong input format for columns - must be a mapping dictionary')
        force_rename = kwargs.pop('force', False)
        lang = kwargs.pop('lang', self.lang)
        idate = kwargs.pop('date', self.date)
        # dumb renaming from one language to the other
        if columns=={} and lang!=self.lang:
            try:
                self.data.rename(columns={col[self.lang]: col[lang] for col in self.icolumns}, inplace=True)
            except:     pass
            # self.lang = lang
        if lang != self.lang:
            # columns = {k: self.get_column(v, ilang=lang, olang=self.lang) for (k,v) in columns.items() if v not in (None,'')}
            columns = {k:col[self.lang] for col in self.icolumns      \
                       for (k,v) in columns.items() if (col[lang]==v and v not in ('',None))}
        fields = {}
        for (ind, field) in columns.items():
            if field is None:
                if force_rename is False:       continue
                else:                           field = ind 
            ofield = OINDEX[ind]['name'] if ind in OINDEX.keys() and force_rename is False else ind
            if ind in self.oindex: # update the index: this will inform us about which renamings were successful
                self.oindex.update({ind: ofield})
            if field == ofield:
                continue
            if not field in fields:
                self.data.rename(columns={field: ofield}, inplace=True)
                # deal with duplicated columns
                fields.update({field: ofield}) # add it the first time it appears
                cast = OINDEX[ind]['type']               
                if cast == self.data[ofield].dtype:
                    continue
                self.data[ofield] = self.to_cast(self.data, ofield, cast, ifmt=idate, ofmt=ODATE)
            else: # dumb copy
                self.data[field] = self.data[fields[field]]
        return columns

    #/************************************************************************/
    def clean_column(self, *columns, **kwargs):
        """Filter the dataframe
        """
        columns = (columns not in ((None,),()) and columns[0])        or \
                    kwargs.pop('drop', [])
        if isinstance(columns, string_types):
            columns = [columns,]
        elif not(columns in (None, ())                                  or \
                 (isinstance(columns, Sequence) and all([isinstance(col,string_types) for col in columns]))):
            raise TypeError('wrong input format for drop columns - must be a (list of) string(s)')
        index = kwargs.pop('keep', [])                     
        if isinstance(index, string_types):
            index = [index,]
        elif not(isinstance(index, Sequence) and all([isinstance(ind,string_types) for ind in index])):
            raise TypeError('wrong input format for keep columns - must be a (list of) string(s)')
        force_keep = kwargs.pop('force', False)                     
        # lang = kwargs.pop('lang', None) # OLANG
        for i, col in enumerate(columns):
            try:        assert col in self.data.columns
            except:
                try:        assert col in self.oindex
                            # assert col in [col_[lang] for col_ in self.icolumns]
                except:     continue
                else:
                    # col = [col_[self.lang] for col_ in self.icolumns if col_[lang]==col][0]
                    columns.pop(i)
                    columns.insert(i, self.oindex[col])
            else:       continue
        for i, ind in enumerate(index):
            try:        assert ind in self.data.columns
            except:
                try:        assert ind in self.oindex and self.oindex[ind] is not None
                except:     continue
                else:
                    index.pop(i)
                    index.insert(i, self.oindex[ind])
            else:       continue
        # refine the set of columns to actually drop
        columns = list(set(columns).difference(set(index)))
        # drop the columns
        #try:
        #    self.data.drop(columns=columns, axis=1, inplace=True)
        #except:     pass
        for col in columns:
            try: # we make a try per column...
                self.data.drop(columns=col, axis=1, inplace=True)
            except:     pass
        # say it in a more Pythonic way:
        # [self.data.drop(col, axis=1) for col in columns if col in self.data.columns]
        if force_keep is False:
            return
        # 'keep' the others, i.e. when they dont exist create with NaN                
        for ind in index:
            if ind in self.data.columns:
                continue
            cast = OINDEX[ind]['type'] if ind in OINDEX else object    
            if cast == datetime:    cast = str
            try:
                self.data[ind] = pd.Series(dtype=cast)
            except:     pass
    
    #/************************************************************************/
    def define_place(self, *place, **kwargs):
        """Build the place field as a concatenation of existing columns.
        
                >>> hcs.define_place(place=['street', 'no', 'city', 'zip', 'country'])
        """
        lang = kwargs.pop('lang', OLANG)  
        place = (place not in ((None,),()) and place[0])            or \
                kwargs.pop('place', None)                           or \
                self.place
        try:
            assert place in ([],None,'')
            # assert _is_googletrans_installed is True
            tplace = self.translate(IPLACE, ilang='en', olang=lang)
        except (AssertionError,IOError,OSError):
            pass
        else:
            place = tplace
        #force_match = kwargs.pop('force_match', False)
        if isinstance(place, Mapping):
            kwargs.update(place)
            place = list(place.keys())
        self.place = place if isinstance(place, string_types) else 'place' 
        if 'place' in self.oindex: self.oindex.update({'place': 'place'})
        try:
            assert self.place in self.data.columns
        except:
            pass
        else:
            return
        for i in range(len(place)):
            field = place.pop(i)
            if field in kwargs:
                self.set_column(columns={field: kwargs.pop(field), 'lang': lang})
            if field in self.oindex:
                ofield = self.oindex[field] or field
            else:         
                ofield = field
            place.insert(i, ofield)
        if not set(place).issubset(self.data.columns):
            place = list(set(place).intersection(self.data.columns))
        self.data[self.place] = self.data[place].astype(str).apply(', '.join, axis=1)
                
    #/************************************************************************/
    def find_location(self, *latlon, **kwargs):
        """Retrieve the geographical coordinates, may that be from existing lat/lon
        columns in the source file, or by geocoding the location name. 
        
            >>> hcs.find_location(latlon=['lat', 'lon'])
        """
        latlon = (latlon not in ((None,),()) and latlon)            or \
                kwargs.pop('latlon', None)                        
        if isinstance(latlon, Sequence):
            if isinstance(latlon, Sequence) and len(latlon) == 1:
                latlon = latlon[0]
        if isinstance(latlon, string_types):
            lat = lon = latlon
        elif isinstance(latlon, Sequence):
            lat, lon = latlon
        elif not latlon in ([],None):
            raise TypeError('wrong lat/lon fields - must be a single or a pair of string(s)')
        order = kwargs.pop('order', 'lL')
        place = kwargs.pop('place', self.place)
        # lang = kwargs.pop('lang', self.lang)
        if latlon in ([],None):
            lat, lon = self.oindex.get('lat', 'lat'), self.oindex.get('lon', 'lon')
            order = 'lL'
        olat, olon = OINDEX['lat']['name'], OINDEX['lon']['name']
        if lat == lon and lat in self.data.columns: #self.icolumns[lang]
            latlon = lat
            if order == 'lL':           lat, lon = olat, olon
            elif order == 'Ll':         lat, lon = olon, olat
            else:
                raise IOError("unknown order keyword - must be 'lL' or 'Ll'")
            self.data[[lat, lon]] = self.data[latlon].str.split(pat=" +", n=1, expand=True) #.astype(float)
            geo_qual = 3
        elif lat in self.data.columns and lon in self.data.columns: 
        # elif lat in self.icolumns[lang] and lon in self.icolumns[lang]: 
            if lat != olat:
                self.data.rename(columns={lat: olat})
            if lon != olon:                
                self.data.rename(columns={lon: olon})
            geo_qual =3 
        else:
            if not(isinstance(place, string_types) and place in self.data.columns):
                self.define_place(**kwargs)
            #elif set(self.place).difference(set(self.data.columns)) == {}: 
            #    self.set_column(**kwargs)         
            f = lambda place : self.locate(place)
            try:                        f(coder=-1)
            except TypeError:
                self.data[olat], self.data[olon] = zip(*self.data[self.place].apply(f))                                     
                self.proj = None
            except ImportError:
                raise IOError('no geocoder available')
            geo_qual = None # TBD
        if OPROJ is not None and self.proj not in (None,'') and self.proj != OPROJ:
            f = lambda lat, lon : self.project([lat, lon], iproj=self.proj, oproj=OPROJ)
            try:                        f('-1')
            except TypeError:
                self.data[olat], self.data[olon] = zip(*self.data[[olat, olon]].apply(f))
            except ImportError:
                raise IOError('no projection transformer available')
        if 'geo_qual' in OINDEX.keys(): # in self.oindex
            ind = OINDEX['geo_qual']['name']
            self.data[ind] = geo_qual 
            self.oindex.update({'geo_qual': ind})
        if 'lat' in self.oindex and 'lon' in self.oindex:
            self.oindex.update({'lat': olat, 'lon': olon})
        # cast
        # self.data[olat], self.data[olon] = pd.to_numeric(self.data[olat]), pd.to_numeric(self.data[olon])
        self.data[olat], self.data[olon] =                              \
            self.data[olat].astype(OINDEX['lat']['type']), self.data[olon].astype(OINDEX['lon']['type'])
        
    #/************************************************************************/
    def prepare_data(self, *args, **kwargs):
        """Abstract method for data preparation.
        
            >>> hcs.prepare_data(*args, **kwargs)
        """
        pass
    
    #/************************************************************************/
    def format_data(self, **kwargs):
        """Run the formatting of the input data according to the harmonised template
        as provided by the index metadata.
        
            >>> hcs.format_data(**index)
        """
        _index = kwargs.pop('index', {})
        if isinstance(_index, Sequence):
            _index = dict(zip(_index,_index))
        elif not isinstance(_index, Mapping):
            raise TypeError('wrong format for input index - must a mapping dictionary')
        lang = kwargs.pop('lang', OLANG)
        if not isinstance(lang, string_types):
            raise TypeError('wrong format for language - must a string')
        try:
            index = self.oindex.copy()
            index.update(_index) # index overwrites whatever is in oindex
        except:
            raise IOError
        try:
            assert lang == self.lang
        except:            
            index = {k: self.get_column(v, ilang=lang, olang=self.lang)     \
                     for (k,v) in index.items() if v not in (None,'')}
        try:
            assert index != {}
        except: # not vey happy with this, but ok... it's a default!
            index = {col[OLANG]: col[self.lang] for col in self.icolumns}
        # check for country-related columns - special case
        for cc in ['country', 'cc']:
            if cc in index:
                _index = index[cc] or cc
                if not _index in self.data.columns:   
                    self.data[_index] = getattr(self, cc, None) 
                    self.oindex.update({cc: _index})
            else:       pass
        ## define the place: we actually skip this (see 'assert False' below), and 
        ## do it only if needed when running find_location later
        #try:
        #    assert False # 
        #    place = [key for key in index.keys() if key in IPLACE]
        #    self.define_place(place = place)
        #except:
        #    pass
        #finally:
        #     index.pop('place',None) # just in case it was created and was present in the list
        # find the locations associated to the data
        try:
            latlon = [index.get(l, l) for l in ['lat', 'lon']]
            self.find_location(latlon = latlon)
        except:
            warnings.warn('location not assigned for data')            
        finally:
            [index.pop(l,None) for l in ['lat', 'lon']]
        ## update oindex with index (which has been modified by get_column and
        ## does not contain ['lat','lon'])
        # self.oindex.update(index)
        # reset the columns with the right exptected names 
        try:
            self.set_column(columns = index)
        except:
            pass
        # clean the data so that it matches the template; keep even those fields
        # from index which have no corresponding column
        index = [v if v is not None else OINDEX[k]['name'] for (k,v) in self.oindex.items()]
        try:
            self.clean_column(list(self.data.columns), keep = index)
        except:
            pass
            
    #/************************************************************************/
    def save_data(self, *dest, **kwargs):
        """Store transformed data in GEOJSON or CSV formats.
        
            >>> hcs.save_data(dest=filename, fmt='csv')
            >>> hcs.save_data(dest=filename, fmt='geojson')
        """
        dest = (dest not in ((None,),()) and dest[0])               or \
             kwargs.pop('dest', None)                               or \
             self.dest        
        fmt = kwargs.pop('fmt', None)
        if not isinstance(fmt, string_types):
            raise TypeError('wrong input format - must be a string key')
        else:
            fmt = fmt.lower()
        encoding = kwargs.pop('enc', OENC)
        sep = kwargs.pop('sep', OSEP)
        date = kwargs.pop('date', ODATE)#analysis:ignore
        if not fmt in OFMT.keys():
            raise TypeError('wrong input format - must be any string among %s' % list(OFMT.keys()))
        if dest in (None,''):
            dest = osp.join(OPATH, fmt, OFILE % (self.cc, OFMT[fmt]))
        #try:
        #    kwargs.update(self.save_data.__dict__)
        #except:         pass
        columns = [col for col in [ind['name'] for ind in OINDEX.values()]  \
                                   if col in self.data.columns]     # self.oindex.copy()
        # reorder the columns - note this is useful for csv and json data only
        # but ok, not critical...
        self.data.reindex(columns = columns)
        if fmt == 'csv':
            kwargs.update({'header': True, 'index': False, 
                           'encoding': encoding, 'sep': sep})
            self.data.to_csv(dest, columns=columns, **kwargs) 
            #                date_format=date
        elif fmt == 'geojson':
            geom = self.to_geojson(self.data, columns, lat=self.lat, lon=self.lon)
            with open(dest, 'w', encoding=encoding) as f:
                geojson.dump(geom, f, ensure_ascii=False)
        elif  fmt == 'json':
            records = self.to_json(self.data, columns)
            with open(dest, 'w', encoding=encoding) as f:
                json.dump(records, f, ensure_ascii=False)
        elif fmt == 'gpkg':
            results = self.to_gpkg(self.data, columns, lat=self.lat, lon=self.lon)#analysis:ignore
        return
        
    #/************************************************************************/
    def save_meta(self, *dest, **kwargs):
        """Save metadata into a JSON file.
        
            >>> hcs.save_meta(dest=metaname)
        """
        dest = (dest not in ((None,),()) and dest[0])               or \
             kwargs.pop('dest', None)   
        if dest is None:   
            dest = '%smeta.json' % self.cc  
        try:
            with open(dest, 'w', encoding=self.enc) as f:
                json.dump(self.meta.__dict__, f, ensure_ascii=False)
        except:
            raise IOError('impossible saving metadata')
            
            
#%% 
#==============================================================================
# Function hcsFactory
#==============================================================================
        
def hcsFactory(*args, **kwargs):
    """Generic function to derive a class from the base class :class:`BaseHCS`
    depending on specific metadata and a given geocoder.
    
        >>>  NewHCS = hcsFactory(country=CC1, coder={'Bing', yourkey})
        >>>  NewHCS = hcsFactory(country=CC2, coder='GISCO')
    """
    base = BaseHCS # kwargs.pop('base', BaseHCS)
    if args in ((),(None,)):        metadata = None
    else:                           metadata = args[0]
    if not metadata is None:
        if isinstance(metadata,string_types) or isinstance(metadata,Mapping):
            meta = MetaHCS(metadata)
        elif not isinstance(metadata,MetaHCS):
            raise TypeError('metadata type not recognised - must be a filename, dictionary or %s' % MetaHCS.__name__)
    else:
        meta = None # {}
    attributes = {}
    country = meta.get('country') if 'country' in meta else kwargs.pop('country', None)
    try:
        assert country is None or isinstance(country,Mapping) or isinstance(country,string_types)
    except AssertionError:
        raise TypeError('country type not recognised - must be a dictionary')
    if country not in (None,{}):
        if isinstance(country,string_types): 
            country = {'code': country, 'name': None}
        try:
            assert set(country.keys()) == set(['name', 'code'])
        except AssertionError:
            raise IOError('country format not recognised')
        CC = country.get('code')
        COUNTRY = country.get('name')
        attributes.update({"COUNTRY": {'code': CC, 'name': COUNTRY}})
        name = CC + base.__name__
    else:
        name = 'NewHCS'
    coder = kwargs.pop('coder', None)
    try:
        assert coder is None or isinstance(coder,string_types) or isinstance(coder,Mapping)
    except AssertionError:
        raise TypeError('coder type not recognised - must be a dictionary or a single string')
    else:
        if isinstance(coder,string_types):  coder = {coder: None}
    if coder not in (None,{}):
        try:
            assert len(coder) == 1
        except AssertionError:
            raise IOError('coder format not recognised')
        CODER, CODERKEY = list(coder.items())[0]
        try:
            assert CODER in CODERS.keys() and CODERKEY in CODERS.values()
        except AssertionError:
            raise IOError('coder not supported')
        attributes.update({"CODER": CODER, "CODERKEY": CODERKEY})
    def __init__(self, *args, **kwargs):
        try:
            self.meta = meta.copy() 
        except:
            pass
        #for key, value in kwargs.items():
        #    # here, the argnames variable is the one passed to the
        #    # ClassFactory call
        #    if key not in argnames:
        #        raise TypeError("Argument %s not valid for %s" 
        #            % (key, self.__class__.__name__))
        #    setattr(self, key, value)
        base.__init__(self, *args, **kwargs)
    attributes.update({"__init__": __init__})
    return type(name, (base,), attributes)
 