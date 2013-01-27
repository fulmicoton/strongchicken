from collections import defaultdict
import numpy as np


class Cache:

    def __init__(self,):
        self.cache = {}

    def get(self, f, *args, **kargs):
        key = (f, args, kargs)
        if key not in self.cache:
            self.cache[key] = f(*args, **kargs)
        return self.cache[key]



def compose(f, g):
    def aux(*args, **kargs):
        return f(g(*args, **kargs))
    return aux


def MagicDic():
    return defaultdict(MagicDic)


def positive(X):
    return  X * (X > 0)


def strictly_positive(X):
    return  X * (X > 0) + 1e-8
