import numpy as np
from uncertainty_system import UncertaintySystem

class Innovation:

    DIMENSION = 1

    class InnovationSystem(UncertaintySystem):
        def __init__(self,):
            raise NotImplementedError(
                    """You need to implement a Generator for
                    you generator.""")

    @property
    def dimension(self,):
        return self.__class__.DIMENSION

    def cursor(self, vals, t):
        return vals

class GaussianNoise(Innovation):

    # TODO handle correlation

    class InnovationSystem():

        def __init__(self, innovations):
            assert all([ isinstance(innovation, GaussianNoise)
                         for innovation in innovations ])
            assert all([ innovation.dimension == 1
                         for innovation in innovations ])
            self.innovations = innovations
            self.dimension = len(innovations)
            self.correlation_matrix = np.identity(self.dimension)

        def get_reservation_requests(self,):
            return (self, [ (innovation, 1)
                           for innovation in self.innovations ])

        def compute_innovation(self, t, N):
            return np.random.normal(size=(self.dimension, N))

