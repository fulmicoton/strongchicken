import unittest
from strongchicken.utils import *

from strongchicken.uncertainties import simulator, \
                UncertaintySystem, \
                AssumptionSet, \
                BlackScholes, \
                HistoricalData
from strongchicken.assets import EuropeanPut, AmericanPut
from strongchicken.assets import longstaff_schwartz
from strongchicken.assets.regression import polynomial_regression, force_positive_regression




class TestAsset(unittest.TestCase):

    def setUp(self):
        self.black_scholes = BlackScholes(36., 0.06 * INV.YEAR, 0.20 * INV.SQRT.YEAR)
        self.uncertainty_system = UncertaintySystem([self.black_scholes])
        self.assumption_set = AssumptionSet(self.uncertainty_system,
                                            interest_rate=.06 * INV.YEAR,)
    """    
    def test_european_put(self,):
        european_put = EuropeanPut(1. * UNIT.YEAR, 40., self.black_scholes)
        assert european_put.valuation(self.assumption_set,
                                      nb_simulations=100000).is_compatible(3.844)
    """

    def test_american_put(self,):
        american_put = AmericanPut(0., 1. * UNIT.YEAR, 40., self.black_scholes)
        optimized_asset = longstaff_schwartz.optimize(american_put,
                                                self.assumption_set,
                                                nb_simulations=100000,
                                                regression=force_positive_regression(polynomial_regression))
        assert optimized_asset.optimization_value.is_compatible(4.472)
        print optimized_asset.optimization_value
        assert optimized_asset.valuation(self.assumption_set, nb_simulations=100000).is_compatible(4.472)
    
    """
    def test_european_like_american_put(self,):
        american_put2 = AmericanPut(1. * UNIT.YEAR, 1. * UNIT.YEAR, 40., self.black_scholes)
        optimized_american_option = longstaff_schwartz.optimize(american_put2,
                        self.assumption_set,
                        nb_simulations=10000,
                        regression=force_positive_regression(polynomial_regression))
    """