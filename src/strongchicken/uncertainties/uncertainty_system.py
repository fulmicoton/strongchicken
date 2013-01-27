import numpy as np
from uncertainty import Uncertainty


def system_dimension(uncertainties):
    return sum([uncertainty.dimension
                for uncertainty in uncertainties])


class UncertaintySystem(Uncertainty, set,):

    def __init__(self, *args, **kargs):
        set.__init__(self, *args, **kargs)

    def __hash__(self,):
        return id(self,)

    @property
    def dimension(self,):
        return system_dimension(self)

    @property
    def dependancies(self,):
        return self

    def get_reservation_requests(self,):
        return (self, [ uncertainty.get_reservation_requests()
                        for uncertainty in self ])

    @property
    def innovations(self,):
        return set.union(*[ set(uncertainty.innovations)
                            for uncertainty in self ])

    """
    def get_state_reservation_tickets(self, nb_paths):
        state = np.zeros((nb_paths, self.dimension))
        offset = 0
        uncertainty_map = {}
        for uncertainty in self:
            uncertainty_dim = uncertainty.dimension
            uncertainty_range = slice(offset, offset + uncertainty_dim)
            uncertainty_map[uncertainty] = uncertainty_range
            state[uncertainty_range] = uncertainty.make_initial_state(nb_paths)
            offset += uncertainty_dim
        return State(uncertainty_map, state)
    """
