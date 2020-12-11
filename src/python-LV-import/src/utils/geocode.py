import re
import logging
import os
import io
import json
# import urllib.request
# import urllib.parse
# import urllib.request
import requests

engines = {
    # Azure engine needs subscription key.
    # Please replace <subscription-key> with your own Azure Maps subscription key.
    # See details https://azure.microsoft.com/en-us/pricing/details/azure-maps
    # At the moment of writing, 25,000 free transactions/month, then €0.422 per 1,000 transactions.
    "azure": {
        "url": "https://atlas.microsoft.com/search/address/json?subscription-key=<subscription-key>&api-version=1.0&countrySet=LV&limit=1&query=#{query}"
    }
}
geoQual = {
    "Point Address": 1,
    "Address Range": 2,
    "Street": 2,
    "Cross Street": 2,
    "Geography": 3
}

class Geocoder(object):
    def __init__(self, engine):
        # engine: one from engines
        if not engine in engines:
            raise "Unknown engine {}".format(engine)
        self.engine = engines[engine]

    def exists(self, data):
        return "georesult" in data and data["georesult"]

    def parse(self, data):
        georesult = data["georesult"]
        if not georesult:
            logging.error("Not geocoded:\n{}".format(str(data)))
            return
        data["geo_type"] = georesult["type"]
        data["geo_id"] = georesult["id"]
        addr = georesult["address"]
        if "streetName" in addr:
            data["street"] = addr["streetName"]
        elif "municipalitySubdivision" in addr:
            data["street"] = addr["municipalitySubdivision"]
        if "streetNumber" in addr:
            data["house_number"] = addr["streetNumber"]
        if "postalCode" in addr:
            data["postcode"] = addr["postalCode"]
        if "municipality" in addr:
            data["city"] = addr["municipality"]
        pos = georesult["position"]
        data["lat"] = pos["lat"]
        data["lon"] = pos["lon"]
        data["geo_qual"] = -1
        if georesult["type"] in geoQual:
            data["geo_qual"] = geoQual[georesult["type"]]


    def geocode(self, data):
        errors = []
        try:
            url = self.engine["url"].replace("#{query}", data["address"])
            gcResponse = requests.get(url).json()
            if len(gcResponse["results"]) == 0:
                raise Exception("Geocoder found no matches")
            bestResult = gcResponse["results"][0]
            data["georesult"] = bestResult
            self.parse(data)
        except Exception as e:
            logging.error(e)
            errors.append(str(e))
        data["errors-geocoding"]  = "; ".join(errors)
        return len(errors) == 0


    # Custom address parser fine-tuned to addresses coming from
    # https://viis.lv/Pages/Institutions/Search.aspx
    def parseAddress(self, data):
        full = data["address"]
        orgParts = [part.strip() for part in full.split(',')]
        if len(orgParts) == 3:
            data["street"], data["city"], data["postcode"] = orgParts
        elif len(orgParts) == 4:
            if full.find("PRIEKŠPILSĒTA") > 0 or full.find("RAJONS") > 0: # 2nd position is suburb - skipping
                data["street"], dummy, data["city"], data["postcode"] = orgParts
            if full.find("NOVADS") > 0: # 3rd position is local administrative unit - skipping
                data["street"], data["city"], dummy, data["postcode"] = orgParts
        elif len(orgParts) == 5:
            data["street"], data["city"], dummy, dummy, data["postcode"] = orgParts
        elif len(orgParts) not in [3, 5]:
            logging.error("Incorrect address - number of parts not between 3 and 5: " + full)
            return
        streetNum = data["street"]
        #m = re.match("(.*?)\s+(\d+(?:.*[/-]*\s*\w*)?)?$", streetNum)
        m = re.match("(.*(?:IELA|iela|LĪNIJA|ŠOSEJA|PROSPEKTS|prospekts|GATVE|DAMBIS|BULVĀRIS|ALEJA|LAUKUMS|CEĻŠ|KRASTMALA|MAĢISTRĀLE))\s+(.*)?$", streetNum)
        if m:
            data["street"], data["house_number"] = m.groups()
            #logging.info(data["street"] + "|" + data["house_number"])
        # else:
        #     logging.info(streetNum)
