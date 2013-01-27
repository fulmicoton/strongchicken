from uncertainty_system import UncertaintySystem
from numpy import exp

class AssumptionSet:

    """ at the moment, this class only hosts the interest rate and the uncertainty models. """
    def __init__(self, uncertainty_system=UncertaintySystem(), interest_rate=0.):
        self.uncertainty_system = uncertainty_system
        self.interest_rate = interest_rate

    def discount_factor(self, T):
        # TODO use discount factor time serie
        return exp(-self.interest_rate * T)

