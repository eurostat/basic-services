import sys
import csv
import io
import json
import os
import codecs
from utils import map, cache, check, geocode, delim, counters
import logging
import shutil
logging.basicConfig(level=logging.INFO)

# File where merged output from several input files is collected.
# Follows https://webgate.ec.europa.eu/fpfis/wikis/pages/viewpage.action?spaceKey=GISCO&title=Education+services+in+Europe
outFileName = "LV.csv"

inputParamsExplain = 'Input params: \n\t(1) input file name\n\t(2) delimiter.'
if len(sys.argv) <= 2:
    #logging.error(inputParamsExplain)
    raise Exception(inputParamsExplain)
inFileName = sys.argv[1]
delimiter = sys.argv[2]
if not os.path.exists(inFileName):
    raise Exception("File {} not found".format(inFileName))
logging.info("Input file: {} is supposed to be '{}'-delimited.".format(inFileName, delimiter))

datasetName = os.path.splitext(inFileName)[0]
mapFileName = datasetName + '.json'
if not os.path.exists(mapFileName):
    raise Exception('Required: file {} in the current directory describing field mapping. Cannot proceed.'.format(mapFileName))
logging.info("Mapping file: {}".format(mapFileName))

csvFileName = datasetName + '.csv'
if delimiter == ',':
    if inFileName != csvFileName: # Comma-delimited, but not .csv extension
        shutils.copyfile(inFileName, csvFileName)
else:
    delimReplacer = delim.DelimReplacer("|", ",")
    delimReplacer.replace(inFileName, csvFileName)

# Importing files into ./ceche/<id-field-value>.json
limitProcessed = 999999999
mapper   = map.Mapper(mapFileName)
cacher   = cache.Cacher()
geocoder = geocode.Geocoder('azure')
checker  = check.Checker()
cnt = counters.Counters()
cnt.multiReset(("processed", "created", "loaded", "geocodedBefore", "geocodedNow", "geocodedFail"))
geocodedFailIds = []
logging.info("Processing/merging stage: opening {} for processing".format(csvFileName))
with io.open(csvFileName, mode="r", encoding="utf-8-sig") as inData:
    rdr = csv.DictReader(inData)
    mapper.check(rdr.fieldnames)
    for row in rdr:
        id = mapper.id(row)
        if cacher.valid(id): # File data["id"].json exists and can be loaded
            data = cacher.load(id)
            dataNew = mapper.empty() # create fields listed in field-map.json
            if not mapper.map(dataNew, row): # do mapping
                logging.error("Mapping errors: {}".format(dataNew["errors-map"]))
            logging.debug("Before merge:\n{}".format(str(data)))
            mapper.merge(data, dataNew)
            logging.debug("After merge:\n{}".format(str(data)))
            cnt.loaded += 1
        else:
            data = mapper.empty() # create fields listed in field-map.json
            if not mapper.map(data, row): # do mapping
                logging.error("Mapping errors: {}".format(data["errors-map"]))
            cnt.created += 1
        # logging.debug("Saving to {}\n{}".format(id, str(data)))
        cacher.save(id, data)

        if not geocoder.exists(data): # Previously geocoded data found
            if geocoder.geocode(data):
                cnt.geocodedNow += 1
            else:
                logging.error("Geocoding failed: for ID {}: {}".format(data["id"], data["errors-geocoding"]))
                cnt.geocodedFail += 1
                geocodedFailIds.append(id)
            cacher.save(id, data)
        else:
            geocoder.parse(data)
            cnt.geocodedBefore += 1

        if not checker.check(data): # checks
            logging.error("Failed checks: {}" + '; '.join(data["errors-check"]))

        cnt.processed += 1
        if cnt.processed % 100 == 0:
            logging.info("\t{} records processed, {} geocoded".format(cnt.processed, cnt.geocodedNow))
        if cnt.processed >= limitProcessed:
            break
logging.info("Processing/merging stage finished. {} records processed:\n\t" \
    "cache: {} loaded, {} created\n\tgeocoding: {} reused, {} geocoded, {} failed.".format(
    cnt.processed, cnt.loaded, cnt.created, cnt.geocodedBefore, cnt.geocodedNow, cnt.geocodedFail))
if len(geocodedFailIds) > 0:
    logging.info("Geocoding failed: {}".format(','.join(geocodedFailIds)))
logging.info("Output stage: opening {} for writing".format(outFileName))
cnt.processed = 0
with io.open(outFileName, mode="w", encoding="utf-8", newline='') as outData:
    wrt = csv.DictWriter(outData, fieldnames=mapper.fieldnamesFinal())
    wrt.writeheader()
    for item in cacher.items():
        cleanData = mapper.clean(item)
        wrt.writerow(cleanData)
        cnt.processed += 1
        if cnt.processed % 100 == 0:
            logging.info("\t{} records processed.".format(cnt.processed))
        if cnt.processed >= limitProcessed:
            break
logging.info("Output stage finished. {} records processed.".format(cnt.processed))
logging.info("End.".format(cnt.processed))
