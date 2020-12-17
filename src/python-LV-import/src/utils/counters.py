class Counters:
    def __init__(self):
        pass

    def __getattr__(self, name):
        setattr(self, name, 0)

    def set(self, key, count):
        self.__dict__[key] = count

    def get(self, key):
        if not key in self.__dict__:
            self.set(key, 0)
        return self.__dict__[key]

    def inc(self, key, number = 1):
        self.set(key, self.get(key) + number)

    def multi(self, counts):
        for key, count in counts.items():
            self.set(key, count)

    def reset(self, key):
        self.set(key, 0)

    def multiReset(self, keys):
        for key in keys:
            self.set(key, 0)
