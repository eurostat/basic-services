import io
import json
import logging
import datetime
import jmespath

class Mapper(object):
    def __init__(self, mapFile):
        logging.info("Loading field definitions from {}".format(mapFile))
        with io.open(mapFile, mode="r", encoding="utf-8") as fldMap:
            self.fieldMap = json.load(fldMap)
            self.orgId = self.fieldMap["id"]["mapping-name"]

    def name(self, fieldName):
        return self.fieldMap[fieldName]["mapping-name"] if fieldName in self.fieldMap and "mapping-name" in self.fieldMap[fieldName] else None

    def id(self, data):
        if "id" in data:
            return data["id"]
        if "mapping-name" in self.fieldMap["id"]:
            if self.fieldMap["id"]["mapping-name"] in data:
                return data[self.fieldMap["id"]["mapping-name"]].strip()
        raise Exception('Cannot extract ID from {}'.format(str(data)))

    def check(self, fields): # checks that all fields with mapping definitions are represented in the data
        mappedFields = [fldDef["mapping-name"] for fld, fldDef in self.fieldMap.items() if "mapping-name" in fldDef]
        for mappedField in mappedFields:
            if not mappedField in fields:
                raise Exception("Mapped field '{}' not found in the list of fields '{}'".format(mappedField, ','.join(fields)))
        calcFieldLists = [fldDef["mapping-calc"] for fld, fldDef in self.fieldMap.items() if "mapping-calc" in fldDef]
        for calcFieldList in calcFieldLists:
            for calcField in calcFieldList.split(','):
                if not calcField in fields:
                    raise Exception("Calculation field '{}' not found in the list of fields '{}'".format(calcField, ','.join(fields)))

    def map(self, data, src):
        errors = []
        # First round - mapping of original fields to our fields
        for fieldName, fieldDef in self.fieldMap.items():
            val = None
            if "mapping-name" in fieldDef: # mapping exists
                if not fieldDef["mapping-name"] in src:
                    errors.append("Field {} not found in {}".format(fieldDef["mapping-name"], str(src)))
                else:
                    val = src[fieldDef["mapping-name"]].strip() # taking correspoing input field value
                    if "mapping" in fieldDef: # corresponding exists between in and out values; out value can correspond to several in values
                        delim = fieldDef["delim"] if "delim" in fieldDef else ","
                        val = delim.join([code for code, values in fieldDef["mapping"].items() if val in values])
                    data[fieldName] = val
            if "mapping-sum" in fieldDef: # mapping exists
                tot = 0
                fields = fieldDef["mapping-sum"].split(',')
                for field in fields:
                    tot += int(src[field])
                data[fieldName] = tot
        data["errors-map"] = "; ".join(errors)
        return len(errors) == 0

    def merge(self, old, new):
        for field in self.fieldnames():
            valNew = new[field]
            if str(valNew).strip() == "":
                valNew = None
            valOld = old[field]
            if str(valNew).strip() == "":
                valNew = None
            val = None
            if not valNew and valOld: # no new value
                val = valOld
            elif not valOld and valNew: # no old value
                logging.info("id {} field {}: {} <-- {}".format(self.id(new), field, str(valOld), str(valNew)))
                val = valNew
            else:
                val = valNew
            old[field] = val
        logging.debug("End of merge:\n{}".format(str(old)))

    def empty(self): # construct empty output row
        row = {fld: None for fld in self.fieldMap}
        # put default values
        for fieldName, fieldDef in self.fieldMap.items():
            if "default" in fieldDef: # constant value
                defaultExpr = fieldDef["default"]
                if defaultExpr == 'current-date':
                    defaultExpr = datetime.datetime.now().strftime("%d/%m/%Y")
                row[fieldName] = defaultExpr
        return row

    def fieldnames(self):
        return [fld for fld in self.fieldMap]

    def fieldnamesFinal(self):
        return [fld for fld, fldDef in self.fieldMap.items() if not "temporary" in fldDef or not fldDef["temporary"]]

    def clean(self, data): # removes original and temporary fields
        finalFieldNames = self.fieldnamesFinal()
        return {key:value for key, value in data.items() if key in finalFieldNames}
