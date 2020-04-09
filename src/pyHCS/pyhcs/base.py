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

Module enabling the integration of data on Health Care Services (e.g., facilities
like hospitals or clinics) collected from Member States into pan-European harmonised 
format.

**Dependencies**

*require*:      :mod:`os`, :mod:`six`, :mod:`collections`, :mod:`functools`, :mod:`copy`, 
                :mod`datetime`, :mod:`numpy`, :mod:`pandas`

*optional*:     :mod:`requests`, :mod:`simplejson`

*call*:         :mod:`pyhcs.config`, :mod:`pyhcs.misc`         

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
    SERVICE_AVAILABLE = True                
    import requests # urllib2
except ImportError:                 
    _is_requests_installed = False
    warnings.warn('\n! missing requests package (https://pypi.python.org/pypi/requests/) - source data cannot be loaded remotely !')
else:
    # warnings.warn('\n! requests help: https://requests.readthedocs.io/en/master/ !')
    _is_requests_installed = True

from pyhcs import BASENAME, METABASE, EUCOUNTRIES
from pyhcs.config import BASETYPE, INDEX, DATE, LANG, SEP, ENC, \
                            PATH, FILE, FMT, PROJ, OCFGNAME 
from pyhcs.misc import IOProcess, TextProcess, GeoProcess

THISDIR         = osp.dirname(__file__)

_KEEP_INDEX_AS_ILANG = True # that's actually a debug...that is not a debug anymore!
_KEEP_META_UPDATED = True


#%%
#==============================================================================
# Class MetaHCS
#==============================================================================

class MetaHCS(dict):
    """Generic class used to represent metadata instances as dictionary.
    
        >>> meta = MetaHCS(**metadata)
    """
    
    METANAME = ['country', 'lang', 'proj', 'file', 'path', 'enc', 'sep', 
                'columns', 'index'] # default metadata fields
    """Metadata fields related to input country data.
    """

    #/************************************************************************/
    @classmethod
    def template(cls, country=None, **kwargs):
        """"Create a template country metadata file as a JSON file
        
            >>> MetaHCS.template()
        """
        if country is None:
            country = ''
        elif not isinstance(country, string_types):
            raise TypeError('wrong type for country code - must be a string')
        as_file = kwargs.pop('as_file', True)
        temp = dict.fromkeys(cls.METANAME)
        # dumb initialisation
        temp.update({ 'country':     {'code': country.upper() or 'CC', 'name': ''},
                      'lang':        {'code': country.lower() or 'cc', 'name': ''},
                      'file':        '%s.csv' % country or 'CC' ,
                      # 'proj':        None,
                      'path':        '../../data/raw/',
                      'enc':         'latin1',
                      'sep':         ';', 
                      'date':        '%d-%m-%Y', 
                      'columns':     [ ],
                      'index':       dict.fromkeys(INDEX.keys())
                      })
        temp['columns'].extend([{country.lower() or 'cc': 'column1', 'en': 'column1', 'fr': 'colonne1', 'de': 'Spalte1'},
                             {country.lower() or 'cc': 'column2', 'en': 'column1', 'fr': 'colonne2', 'de': 'Spalte2'}])
        [temp['index'].update({list(INDEX.keys())[i]: 'column%s' % str(i+1)}) for i in [0,1]]
        # create the metadata structure with this dumb template
        template = cls(temp)
        if as_file is False:
            return template
        # save it...somewhere
        dest = osp.join(THISDIR, METABASE, "%s%s.json" % (country.upper() or 'temp', BASENAME))
        template.save(dest, **kwargs)
                
    #/************************************************************************/
    def __init__(self, *args, **kwargs):
        if not args in ((),(None,)):
            try:
                meta = deepcopy(args[0]) # deepcopy to avoid updating the default variables!!!
            except:
                meta = args[0]
        else:       
            meta = {}
        if isinstance(meta, MetaHCS):
            meta = dict(meta).copy()
        elif isinstance(meta, string_types):
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
        if 'country' in meta:
            try:        self.__cc = getattr(meta['country'], 'code', None)
            except:     pass
        else:           self.__cc = None
            
    #/************************************************************************/
    def copy(self, *args, **kwargs): # actually new object, like a deepcopy...
        return self.__class__(**self.__dict__)

    #/************************************************************************/
    def __repr__(self):
        return "<{} metadata instance at {}>".format(self.__class__.__name__, id(self))
    def __str__(self):    
        keys = list(set(self.keys()).difference(set(['__cc'])))
        if keys == []:
            return ""
        l = max([len(k) for k in keys])
        return reduce(lambda x,y:x+y, ["{} : {}\n".format(k.ljust(l),getattr(self,k))
            for k in keys if self.get(k) not in ('',None)])    

    #/************************************************************************/
    def __getattr__(self, attr):
        if attr.startswith('__'):
            try:        nattr = attr[2:-2]
            except:     nattr = attr # for compatibility with the use of '__cc', else None
        else:
            nattr = attr
        if nattr in self.keys():  
            r = self.get(nattr)
        else:
            try:        object.__getattribute__(self, attr) 
            except:     pass
            r = None
        return r
    
    #/************************************************************************/
    def load(self, src=None, **kwargs):
        if src is None:
            try:
                src = osp.join(THISDIR, "%s%s.json" % (self.__cc, BASENAME))
            except:
                raise IOError('no source metadata file defined')
        elif not isinstance(src, string_types):
            raise TypeError('wrong source metadata file %s' % src)
        try:
            assert osp.exists(src)
            with open(src, 'r') as fp:
                meta = json.load(fp, **kwargs)#analysis:ignore
        except (AssertionError,ImportError):
            raise IOError('metadata file not available')
        else:
            # warnings.warn('\n! loading metadata file... !')
            pass
        if meta == {}:
            raise IOError('no metadata variable loaded')  
        self.update({var: meta.get(var) for var in self.METANAME if var in meta})
        return meta
    
    #/************************************************************************/
    def save(self, dest=None, **kwargs):
        if dest is None:
            try:
                dest = osp.join(THISDIR, "%s%s.json" % (self.__cc, BASENAME))
            except:
                raise IOError('no destination metadata file defined')
        elif not isinstance(dest, string_types):
            raise TypeError('wrong destination metadata file %s' % dest)
        try:
            assert osp.exists(dest)
        except AssertionError:
            warnings.warn('\n! destination metadata file will be created !')
        else:
            warnings.warn('\n! destination metadata file will be overwritten !')
        meta = {k:v for (k,v) in dict(self.copy()).items() if k in self.METANAME}
        if meta == {}:
            raise IOError('no metadata variable available')        
        with open(dest, 'w') as fp:
            json.dump(meta, fp, **kwargs)
        try:
            with open(dest, 'w') as fp:
                json.dump(meta, fp, **kwargs)
        except:
            raise IOError('error writing metadata file')
        else:
            # warnings.warn('\n! writing metadata file... !')
            pass
    
#%%
#==============================================================================
# Class BaseHCS
#==============================================================================

class BaseHCS(object):
    """Base class used to represent health care data sources.
    
        >>> hcs = BaseHCS(**metadata)
    """
    
    CC = None # class attribute... that should not be different from cc
    
    #/************************************************************************/
    def __init__(self, **kwargs):
        self.__data = None                # data
        self.__place = ''                 # key field to store a place                              
        self.__latlon = ['', '']          # key fields for lat/lon coordinates
        try:
            # meta should be initialised in the derived class
            assert getattr(self, 'meta', None) not in ({},None)
        except AssertionError:
            self.meta = dict(zip(MetaHCS.METANAME,          \
                                 [{},       # init country
                                  {},       # init lang
                                  None,     # init proj 
                                  '',       # init file
                                  '',       # init path
                                  None,     # init enc
                                  ',',      # init sep 
                                  [],       # init columns
                                  {}        # init index
                                  ]))
        # retrieve country name and code
        country = GeoProcess.isoCountry(self.meta.get('country',None) or self.CC)
        self.cc = kwargs.pop('cc', None if country in ({},None) else country.get('code'))
        # retrieve languge of the input data
        lang = TextProcess.isoLang(self.meta.get('lang',None))
        self.lang = kwargs.pop('lang', None if lang in ({},None) else lang.get('code'))
        # retrieve input data parameters, e.g. name, location, and format 
        self.enc = kwargs.pop('enc',self.meta.get('enc', None))
        self.sep = kwargs.pop('sep',self.meta.get('sep', None))
        path, fname = kwargs.pop('path',self.meta.get('path','')), kwargs.pop('file',self.meta.get('file',''))
        if osp.basename(fname) != fname:
            path, fname = osp.join(path, osp.dirname(fname)), osp.basename(fname)
        if not(path in (None,'') or osp.isabs(path)):
            path = osp.abspath(osp.join(THISDIR, path))
        self.src = kwargs.pop('src', 
                              None if fname=='' else osp.join(path, fname) if path not in (None,'') else fname) # source file
        # retrieve data year, if any
        self.year = kwargs.pop('year', None)
        # retrieve a default output name
        self.dest = kwargs.pop('dest', None)
        # retrieve the input data projection
        self.proj = kwargs.pop('proj', self.meta.get('proj', None)) # projection system
        # retrieve a default output name
        self.date = kwargs.pop('date', self.meta.get('date','%d-%m-%Y %H:%M')) # input date format
        # retrieve columns when already known
        columns = kwargs.pop('columns', None) # [col[self.lang] for col in COLUMNS]
        self.icolumns = columns or self.meta.get('columns',{})    # header columns
        [col.update({self.lang: col.get(self.lang,'')}) for col in self.icolumns] # ensure there are 'locale' column names
        # retrieve matching columns when known
        index = kwargs.pop('index', None)   # index
        self.oindex = index or self.meta.get('index',{}).copy() or list(INDEX.keys())

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
        if not (meta is None or isinstance(meta, (MetaHCS,Mapping))):         
            raise TypeError('wrong format for country code %s - must be a dictionary' % meta)
        self.__metadata = meta

    @property
    def cc(self):
        return self.__cc
    @cc.setter#analysis:ignore
    def cc(self, cc):
        if cc is None:                          pass
        elif not isinstance(cc, string_types):         
            raise TypeError('wrong format for country code %s - must be a string' % cc)
        elif not cc in EUCOUNTRIES: # EUCOUNTRIES.keys()
            raise IOError('wrong country code %s - must be any valid code from the EU area' % cc)   
        elif cc != self.CC:
            warnings.warn("\n! mismatch with class variable 'CC': %s !" % self.CC)
        if _KEEP_META_UPDATED is True:
            self.meta.update({'country': {'code': cc, 'name': EUCOUNTRIES[cc]}}) # GeoProcess.isoCountry
        self.__cc = cc

    @property
    def country(self):
        return EUCOUNTRIES[self.cc]

    @property
    def lang(self):
        return self.__lang
    @lang.setter#analysis:ignore
    def lang(self, lang):
        if not (lang is None or isinstance(lang, string_types)):         
            raise TypeError('wrong format for language type %s - must be a string' % lang)
        if _KEEP_META_UPDATED is True:
            self.meta.update({'lang': {'code': lang, 'name': TextProcess.LANGS[lang]}}) # TextProcess.isoLang
        self.__lang = lang

    @property
    def year(self):
        return self.__refdate
    @year.setter#analysis:ignore
    def year(self, year):
        if not (year is None or isinstance(year, int)):         
            raise TypeError('wrong format for year: %s - must be an integer' % year)
        if _KEEP_META_UPDATED is True:
            self.meta.update({'year': year})
        self.__refdate = year

    @property
    def src(self):
        return self.__src
    @src.setter#analysis:ignore
    def src(self, src):
        if not (src is None or isinstance(src, string_types)):         
            raise TypeError('wrong format for source filename %s - must be a string' % src)
        elif src is not None:
            try:
                assert osp.exists(src) is True
            except (OSError,AssertionError):
                warnings.warn("! source file '%s' not found on local disk !" % src)
                try:
                    assert _is_requests_installed is True
                    session = requests.Session()
                    response = session.head(src)
                    response.raise_for_status()
                except AssertionError:
                    pass
                except (requests.URLRequired,requests.HTTPError,requests.RequestException):
                    warnings.warn("\n! source file '%s' not available online !" % src)
                    raise IOError('no input source file found')
        if _KEEP_META_UPDATED is True:
            self.meta.update({'file': osp.basename(src), 'path': osp.dirname(src)})
        self.__src = src

    @property
    def proj(self):
        return self.__proj
    @proj.setter#analysis:ignore
    def proj(self, proj):
        if not (proj is None or isinstance(proj, string_types)):         
            raise TypeError('wrong format for projection type %s - must be a string' % proj)
        if _KEEP_META_UPDATED is True:
            self.meta.update({'proj': proj})
        self.__proj = proj

    @property
    def icolumns(self):
        return self.__columns  # self.meta.get('columns')
    @icolumns.setter#analysis:ignore
    def icolumns(self, cols):
        if cols is None:                        
            pass # nothing yet
        elif isinstance(cols, string_types):
            cols = [{self.lang: cols}]
        elif isinstance(cols, Mapping):
            cols = [cols,]
        elif isinstance(cols, Sequence) and all([isinstance(col, string_types) for col in cols]):
            cols = [{self.lang: col} for col in cols]
        elif not(isinstance(cols, Sequence) and all([isinstance(col, Mapping) for col in cols])): 
            raise TypeError('wrong input column headers type %s - must be a sequence of dictionaries' % cols)
        if _KEEP_META_UPDATED is True:
            self.meta.update({'columns': cols})
        self.__columns = cols

    @property
    def oindex(self):
        return self.__index  # self.meta.get('index')
    @oindex.setter#analysis:ignore
    def oindex(self, ind):
        if ind is None:                        
            pass # nothing yet
        elif isinstance(ind, string_types):
            ind = {ind: None}
        elif isinstance(ind, Sequence):
            ind = dict.fromkeys(ind)
        elif not isinstance(ind, Mapping):
            raise TypeError('wrong output index type %s - must be a dictionary' % ind)
        if _KEEP_META_UPDATED is True:
            self.meta.update({'index': ind})
        self.__index = ind

    @property
    def sep(self):
        return self.__sep
    @sep.setter#analysis:ignore
    def sep(self, sep):
        if not (sep is None or isinstance(sep, string_types)):         
            raise TypeError('wrong format for separator %s - must be a string' % sep)
        if _KEEP_META_UPDATED is True:
            self.meta.update({'sep': sep})
        self.__sep = sep

    @property
    def enc(self):
        return self.__encoding
    @enc.setter#analysis:ignore
    def enc(self, enc):
        if not (enc is None or isinstance(enc, string_types)):         
            raise TypeError('wrong format for file encoding %s - must be a string' % enc)
        if _KEEP_META_UPDATED is True:
            self.meta.update({'enc': enc})
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
             raise IOError("no source filename provided - set 'src' attribute/parameter")
        elif not isinstance(src, string_types):     
             raise TypeError('wrong format for source filename - must be a string')
        # ifmt = osp.splitext(src)[-1]
        encoding = kwargs.pop('enc', self.enc) # self.meta.get('enc')
        sep = kwargs.pop('sep', self.sep) # self.meta.get('sep')
        kwargs.update({'dtype': object})
        #try:
        #    kwargs.update(self.load_data.__dict__)
        #except:         pass
        kwargs.update({'encoding': encoding, 'sep': sep})
        self.data = pd.read_csv(src, **kwargs)
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
            assert self.icolumns not in (None,[],[{}])
        except: 
            self.icolumns = [{self.lang:col} for col in self.data.columns]
        #if set([col[self.lang] for col in self.icolumns]).difference(set(self.data.columns)) != set():
        #    warnings.warn('\n! mismatched data columns and header fields !')
        # if everything worked well, update the fields in case they differ
        if self.src != src:             self.src = src
        if self.enc != encoding:        self.enc = encoding 
        if self.sep != sep:             self.sep = sep 
        
    #/************************************************************************/
    def get_column(self, *columns, **kwargs):
        """Retrieve the name of the column associated to a given field (e.g., manually
        defined), depending on the language.
        
                >>> hcs.get_column(columns=['col1', 'col2'], ilang=None, olang=None)
        """
        columns = (columns not in ((None,),()) and columns[0])          or \
                    kwargs.pop('columns', None)                                 
        if columns in (None, ()):
            pass # will actually return all columns in that case
        elif isinstance(columns, string_types):     
            columns = (columns,)
        elif not (isinstance(columns, Sequence) and all([isinstance(col, string_types) for col in columns])):   
             raise TypeError('wrong input format for columns - must be a (list of) string(s)')
        try:
            langs = list(self.icolumns[0].keys())
        except:
            langs = []
        # langs = list(dict.fromkeys([LANG, *langs])) # reorder with LANG first default... 
        ilang = kwargs.pop('ilang', self.lang) # OLANG
        if ilang is None and not columns in (None, ('',), ()):
            # try to guess the language in the index
            #for ilang in langs:
            #    try:
            #        assert set(columns).difference([col[ilang] for col in self.icolumns]) == set()
            #    except:    continue
            #    else:      break
            f = lambda text : TextProcess.detect(text)
            try:                        assert False and f(-1)
            except TypeError:
                ilang = TextProcess.detect((' ').join(columns.values()))
            else:
                ilang = self.lang # None 
        try:
            assert ilang is not None and ilang in TextProcess.LANGS
        except AssertionError:
            raise IOError('input language not recognised')            
        olang = kwargs.pop('olang', LANG) # LANG
        try:
            assert olang is not None and olang in TextProcess.LANGS
        except AssertionError:
            raise IOError('output language not recognised')            
        try:
            assert ilang in langs or ilang == self.lang
        except AssertionError:
            f = lambda cols: TextProcess.translate(cols, ilang=self.lang, olang=ilang, **kwargs)
            try:                    f(-1)#analysis:ignore
            except TypeError:
                tcols = f([col[self.lang] for col in self.icolumns])
                [col.update({ilang: t}) for (col,t) in zip(self.icolumns, tcols)]
            except ImportError:     
                pass
        except KeyError:
             pass # raise IOError('no columns available')
        try:
            assert (olang in langs and 'filt' not in kwargs) or olang == self.lang
            # if you add a filter, translation is forced
        except AssertionError:
            f = lambda cols: TextProcess.translate(cols, ilang=self.lang, olang=olang, **kwargs)
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
        [ncolumns.update({col[ilang]: col}) for col in self.icolumns]
        #[ncolumns.update({col[ilang]: col.pop(ilang) and col})    \
        #                 for col in [col.copy() for col in self.icolumns]]
        res = [ncolumns[col].get(olang,None) or ncolumns[col].get(ilang,None)   \
               if col in ncolumns.keys() else None for col in columns]
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
                if force_rename is False:       
                    warnings.warn("\n! column '%s' will not be reported in the formatted output table !" % ind)
                    continue
                else:                           
                    field = ind 
            ofield = INDEX[ind]['name'] if ind in INDEX.keys() and force_rename is False else ind
            cast = BASETYPE[INDEX[ind]['type']]            
            #t if ind in self.oindex: # update the index: this will inform us about which renamings were successful
            #t    self.oindex.update({ind: ofield})              
            if field == ofield:
                fields.update({field: ofield}) # add it the first time it appears
                continue
            elif field in fields: # dumb copy
                self.data[ofield] = self.data[fields[field]]
                continue
            else:
                fields.update({field: ofield}) # deal with duplicated columns
                self.data.rename(columns={field: ofield}, inplace=True)          
            if cast == self.data[ofield].dtype:
                continue
            elif cast == datetime:                
                self.data[ofield] = IOProcess.to_date(self.data, ofield, DATE, ifmt=idate) 
            else:
                self.data[ofield] = IOProcess.to_cast(self.data, ofield, cast)
        return columns 

    #/************************************************************************/
    def clean_column(self, *columns, **kwargs):
        """Filter the dataframe.
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
                except:     continue
                else:
                    # col = [col_[self.lang] for col_ in self.icolumns if col_[lang]==col][0]
                    columns.pop(i)
                    #t columns.insert(i, self.oindex[col])
                    columns.insert(i, INDEX[col]) #t
            else:       continue
        for i, ind in enumerate(index):
            try:        assert ind in self.data.columns
            except:
                try:        assert ind in self.oindex and self.oindex[ind] is not None
                except:     continue
                else:
                    index.pop(i)
                    #t index.insert(i, self.oindex[ind])
                    index.insert(i, INDEX[col])
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
            cast = BASETYPE[INDEX[ind]['type']] if ind in INDEX else object    
            if cast == datetime:    cast = str
            try:
                self.data[ind] = pd.Series(dtype=cast)
            except:     pass
    
    #/************************************************************************/
    def define_place(self, *place, **kwargs):
        """Build the place field as a concatenation of existing columns.
        
                >>> hcs.define_place(place=['street', 'no', 'city', 'zip', 'country'])
        """
        lang = kwargs.pop('lang', LANG)  
        place = (place not in ((None,),()) and place[0])            or \
                kwargs.pop('place', None)                           or \
                self.place
        try:
            assert place in ([],None,'')
            tplace = TextProcess.translate(GeoProcess.PLACE, ilang='en', olang=lang)
        except (AssertionError,IOError,OSError):
            pass
        else:
            place = tplace
        #force_match = kwargs.pop('force_match', False)
        if isinstance(place, Mapping):
            kwargs.update(place)
            place = list(place.keys())
        self.place = place if isinstance(place, string_types) else 'place' 
        if isinstance(place, string_types):
            place = [place,] # just to be sure...
        if 'place' in INDEX.keys() and not 'place' in self.oindex: # actually not recorded: always False
            self.oindex.update({'place': 'place'}) # it is created on the fly
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
        if not isinstance(latlon, string_types) and isinstance(latlon, Sequence):
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
        olat, olon = INDEX['lat']['name'], INDEX['lon']['name']
        if lat == lon and lat in self.data.columns: #self.icolumns[lang]
            latlon = lat
            if order == 'lL':           lat, lon = olat, olon
            elif order == 'Ll':         lat, lon = olon, olat
            else:
                raise IOError("unknown order keyword - must be 'lL' or 'Ll'")
            self.data[[lat, lon]] = self.data[latlon].str.split(pat=r'\s+', n=1, expand=True) #.astype(float)
            geo_qual = 1
        elif lat in self.data.columns and lon in self.data.columns: 
        # elif lat in self.icolumns[lang] and lon in self.icolumns[lang]: 
            if lat != olat:
                self.data.rename(columns={lat: olat}, inplace=True)
            if lon != olon:                
                self.data.rename(columns={lon: olon}, inplace=True)
            geo_qual = 1
        else:
            if not(isinstance(place, string_types) and place in self.data.columns):
                self.define_place(**kwargs)
            #elif set(self.place).difference(set(self.data.columns)) == {}: 
            #    self.set_column(**kwargs)         
            f = lambda place : self.geoserv.locate(place)
            try:                        f(coder=-1)
            except TypeError:
                self.data[olat], self.data[olon] = zip(*self.data[self.place].apply(f))                                     
                self.proj = None
            except ImportError:
                raise IOError('no geocoder available')
            geo_qual = None # TBD
        ind = INDEX['geo_qual']['name']
        self.data[ind] = geo_qual 
        if not 'geo_qual' in self.oindex: 
            self.oindex.update({'geo_qual': ind})
        # no need: self.icolumns.extend([{'en': ind}])
        if not 'lat' in self.oindex:
            self.oindex.update({'lat': olat})
        if not 'lon' in self.oindex:
            self.oindex.update({'lon': olon})
            # no need: self.icolumns.extend([{'en': olat}, {'en': olon}}])
        if PROJ is not None and self.proj not in (None,'') and self.proj != PROJ:
            f = lambda lat, lon : self.geoserv.project([lat, lon], iproj=self.proj, oproj=PROJ)
            try:                        f('-1')
            except TypeError:
                self.data[olat], self.data[olon] = zip(*self.data[[olat, olon]].apply(f))
            except ImportError:
                raise IOError('no projection transformer available')
        # cast
        # self.data[olat], self.data[olon] = pd.to_numeric(self.data[olat]), pd.to_numeric(self.data[olon])
        self.data[olat], self.data[olon] =                              \
            self.data[olat].astype(BASETYPE[INDEX['lat']['type']]),    \
            self.data[olon].astype(BASETYPE[INDEX['lon']['type']])
        
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
        if isinstance(_index, string_types):
            _index = {_index: None}  
        elif isinstance(_index, Sequence):
            _index = dict(zip(_index,_index))
        elif not isinstance(_index, Mapping):
            raise TypeError('wrong format for input index - must a mapping dictionary')
        lang = kwargs.pop('lang', LANG)
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
            index = {k: self.get_column(v, ilang=lang, olang=self.lang)  or \
                        self.get_column(v, olang=self.lang)                 \
                     for (k,v) in index.items() if v not in (None,'')}
        try:
            assert index != {}
        except: # not vey happy with this, but ok... it's a default!
            try:
                index = {col[LANG]: col[self.lang] for col in self.icolumns}
            except:
                raise IOError('nothing to match to the input columns - check the (empty) index')
        # check for country- and redate-related columns - special cases
        for attr in ['country', 'cc', 'refdate']:
            if attr in index:
                _index = index[attr] or attr
                if not _index in self.data.columns:   
                    self.data[_index] = getattr(self, '__' + attr, None) 
                if not attr in self.oindex:   
                    self.oindex.update({attr: _index})
            else:       pass
        # find the locations associated to the data
        latlon = [index.get(l, l) for l in ['lat', 'lon']]
        ## define the place: we actually skip this (see 'assert False' below), and 
        ## do it only if needed when running find_location later
        #try:
        #    assert False # 
        #    place = [key for key in index.keys() if key in PLACE]
        #    self.define_place(place = place)
        #except:
        #    pass
        try:
            latlon = [index.get(l, l) for l in ['lat', 'lon']]
            self.find_location(latlon = latlon)
        except:
            warnings.warn('! location not assigned for data !')            
        finally:
            [index.pop(l,None) for l in ['lat', 'lon']]
        ## update oindex with index (which has been modified by get_column and
        ## does not contain ['lat','lon'])
        # self.oindex.update(index)
        # reset the columns with the right exptected names 
        try:
            self.set_column(columns = index)
        except:     pass
        # clean the data so that it matches the template; keep even those fields
        # from index which have no corresponding column
        #t keep = [v if v is not None and k in INDEX else INDEX[k]['name'] for (k,v) in self.oindex.items()]
        keepcol = [INDEX[k]['name'] for (k,v) in self.oindex.items() if k in INDEX and v is not None]
        try:
            self.clean_column(list(self.data.columns), keep = keepcol)
        except:
            pass
        if _KEEP_INDEX_AS_ILANG is True:
            self.oindex.update(index)
        
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
        if fmt is None: # we give it a default value...
            fmt = 'csv'
        if not isinstance(fmt, string_types):
            raise TypeError('wrong input format - must be a string key')
        else:
            fmt = fmt.lower()
        encoding = kwargs.pop('enc', ENC)
        sep = kwargs.pop('sep', SEP)
        date = kwargs.pop('date', DATE)#analysis:ignore
        if not fmt in FMT.keys():
            raise TypeError('wrong input format - must be any string among %s' % list(FMT.keys()))
        if dest in (None,''):
            dest = osp.abspath(osp.join(PATH, fmt, FILE % (self.cc, FMT[fmt])))
        #try:
        #    kwargs.update(self.save_data.__dict__)
        #except:         pass
        columns = [col for col in [ind['name'] for ind in INDEX.values()]  \
                                   if col in self.data.columns]     # self.oindex.copy()
        # reorder the columns - note this is useful for csv and json data only
        # but ok, not critical...
        self.data.reindex(columns = columns)
        try:
            olat, olon = INDEX['lat']['name'], INDEX['lon']['name'] #t self.oindex.get('lat', None), self.oindex.get('lon', None)
            assert fmt not in ('geojson','gpkg') or (olat in columns and olon in columns)
        except:
            raise IOError('geographic lat/lon columns not set')
        if fmt == 'csv':
            kwargs.update({'header': True, 'index': False, 
                           'encoding': encoding, 'sep': sep})
            self.data.to_csv(dest, columns = columns, **kwargs) 
            #                date_format=date
        elif fmt == 'geojson':
            geom = IOProcess.to_geojson(self.data, columns = columns, latlon = [olat, olon])
            with open(dest, 'w', encoding=encoding) as f:
                json.dump(geom, f, ensure_ascii=False)
        elif  fmt == 'json':
            records = IOProcess.to_json(self.data, columns = columns)
            with open(dest, 'w', encoding=encoding) as f:
                json.dump(records, f, ensure_ascii=False)
        elif fmt == 'gpkg':
            results = IOProcess.to_gpkg(self.data, columns = columns)#analysis:ignore
        return
        
    #/************************************************************************/
    def save_meta(self, *dest, **kwargs):
        """Save metadata into a JSON file.
        
            >>> hcs.save_meta(dest=metaname)
        """
        dest = (dest not in ((None,),()) and dest[0])               or \
             kwargs.pop('dest', None)   
        if dest is None:   
            dest = '%s%s.json' % (self.cc, BASENAME) 
        if _KEEP_META_UPDATED is False:
            for attr in OCFGNAME:
                if attr == 'columns':
                    self.meta.update({'columns': self.icolumns})
                elif attr == 'index':
                    # NO: self.meta.update({'index': self.oindex})
                    pass
                elif attr == 'country':
                    self.meta.update({'country': GeoProcess.isoCountry(self.cc)})
                elif attr == 'lang':
                    self.meta.update({'lang': TextProcess.isoLang(self.cc)})
                else:
                    try:
                        self.meta.update({attr: getattr(self,attr)})
                    except:         pass
        try:
            # self.meta.save(dest)
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
    
        >>>  NewHCS = hcsFactory(metadata)
        >>>  NewHCS = hcsFactory(country=CC1, coder={'Bing', yourkey})
        >>>  NewHCS = hcsFactory(country=CC2, coder='GISCO')
    """
    basecls = BaseHCS # kwargs.pop('base', BaseHCS)
    if args in ((),(None,)):        metadata = None
    else:                           metadata = args[0]
    if not metadata is None:
        if isinstance(metadata,MetaHCS):
            meta = metadata.copy()
        elif isinstance(metadata, (string_types,Mapping)):
            meta = MetaHCS(metadata)
        elif not isinstance(metadata,MetaHCS):
            raise TypeError('metadata type not recognised - must be a filename, dictionary or %s' % MetaHCS.__name__)
    else:
        meta = {}
    attributes = {}
    country = meta.get('country') if 'country' in meta else kwargs.pop('country', None)
    try:
        assert country is None or isinstance(country,Mapping) or isinstance(country,string_types)
    except AssertionError:
        raise TypeError('country type not recognised - must be a dictionary')
    if country not in (None,{}):
        country = GeoProcess.isoCountry(country)
        #if isinstance(country,string_types): 
        #    country = {'code': country, 'name': None}
        #try:
        #    assert set(country.keys()) == set(['name', 'code'])
        #except AssertionError:
        #    raise IOError('country format not recognised')
        CC = country.get('code')
        #COUNTRY = country.get('name')
        attributes.update({'CC': CC})
        #attributes.update({"CC": {'code': CC, 'name': COUNTRY}})
        name = CC + basecls.__name__
    else:
        name = 'NewHCS'
    #lang = kwargs.pop('lang', None)
    #if lang not in (None,{}):
    #    lang = TextProcess.isoLang(lang)
    #    LANG = lang.get('code')
    #    attributes.update({'LANG': LANG})
    coder = kwargs.pop('coder', None)
    try:
        assert coder is None or isinstance(coder,string_types) or isinstance(coder,Mapping)
    except AssertionError:
        raise TypeError('coder type not recognised - must be a dictionary or a single string')
    if not coder in ({}, ''): # None accepted, it will be default geocoder defined by the GeoProcess class
        geoserv = GeoProcess(coder)
    else: 
        geoserv = None
    def __init__(self, *args, **kwargs):
        # one metadata dictionary defined 'per country'
        try:
            self.meta = meta # meta.copy() 
        except:
            pass
        # the geocoder is defined 'per country', i.e. you may use different geocoders 
        # for different countries since the quality (e.g., OSM) may differ
        try:
            self.geoserv = geoserv
        except:
            pass
        #for key, value in kwargs.items():
        #    # here, the argnames variable is the one passed to the
        #    # ClassFactory call
        #    if key not in argnames:
        #        raise TypeError("Argument %s not valid for %s" 
        #            % (key, self.__class__.__name__))
        #    setattr(self, key, value)
        basecls.__init__(self, *args, **kwargs)
    attributes.update({"__init__": __init__})
    return type(name, (basecls,), attributes)
 
