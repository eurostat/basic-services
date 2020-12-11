import csv
import io
import json
import os
import logging

class DelimReplacer(object):
    def __init__(self, oldDelim, newDelim):
        self.oldDelim = oldDelim
        self.newDelim = newDelim

    def replace(self, inFileName, outFileName):
        logging.info("Converting delimiters '{}' -> '{}' in file {}. Saving as {}.".format(self.oldDelim, self.newDelim, inFileName, outFileName))
        numRecs = 0
        with io.open(inFileName, mode="r", encoding="utf-8-sig") as inData:
            with io.open(outFileName, mode="w", encoding="utf-8") as outData:
                for row in inData:
                    if row[-2] == self.oldDelim: # strip closing | which otherwise makes closing empty field
                        row = row[:-2] + '\n'
                    outData.write(row.replace(self.oldDelim, self.newDelim))
                    numRecs += 1
        logging.info("{} rows processed".format(numRecs))
