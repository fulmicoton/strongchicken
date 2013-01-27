import numpy as np
from strongchicken.uncertainties import AssumptionSet, BlackScholes, UncertaintySystem
from strongchicken.utils import *
from strongchicken.assets import AmericanPut, longstaff_schwartz
from strongchicken.assets.regression import polynomial_regression, force_positive_regression


market = BlackScholes(36., .06*INV.YEAR, .2*INV.SQRT.YEAR)

american_put = AmericanPut(0., 1. * UNIT.YEAR, 40., market)

uncertainty_system = UncertaintySystem([market])
assumption_set = AssumptionSet(uncertainty_system, interest_rate=.06 * INV.YEAR,)

optimized_asset = longstaff_schwartz.optimize(american_put,
                        assumption_set,
                        nb_simulations=100000,
                        regression=force_positive_regression(polynomial_regression))
print optimized_asset.optimization_value
print optimized_asset.valuation(assumption_set, nb_simulations=1000000)