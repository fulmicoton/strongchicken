
from math import sqrt


UNIT_DICT = {
    "DAY" : 1.,
    "WEEK" : 7.,
    "YEAR" : 365.,
}


class UnitOperator :
    def __init__(self, operator):
        modified_units = [ (k, operator(v))
                          for (k, v) in UNIT_DICT.items() ]
        self.__dict__.update(modified_units)

UNIT = UnitOperator(lambda x:x)
INV = UnitOperator(lambda x: 1. / x)
SQRT = UnitOperator(lambda x: sqrt(x))
INV.SQRT = UnitOperator(lambda x: 1. / sqrt(x))
