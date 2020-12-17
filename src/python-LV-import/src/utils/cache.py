import logging
import os
import io
import json
import glob

class Cacher(object):
    def __init__(self, cacheDir = '.' + os.path.sep + 'cache'):
        self.cacheDir = cacheDir
        if not os.path.exists(self.cacheDir):
            os.makedirs(self.cacheDir)

    def file(self, id):
        return os.path.join(self.cacheDir, id + ".json")

    def remove(self, id):
        if self.exists(id):
            os.remove(self.file(id))

    def save(self, id, data):
        with io.open(self.file(id), mode="w", encoding="utf-8", newline='') as f:
            json.dump(data, f, ensure_ascii=False)

    def exists(self, id):
        return os.path.exists(self.file(id))

    def valid(self, id):
        if not self.exists(id):
            return False
        try:
            self.load(id)
        except Exception as e:
            logging.error("File {} cannot be loaded, error\n{}".format(self.file(id), str(e)))
            return False
        return True

    def load(self, id):
        # New
        if self.exists(id):
            with io.open(self.file(id), mode="r", encoding="utf-8") as f:
                return json.load(f)

    def items(self):
        for path in glob.glob(os.path.join(self.cacheDir, "*.json")):
            with io.open(path, mode="r", encoding="utf-8") as f:
                yield json.load(f)
