import numpy as np

class Uncertainty:

    DIMENSION = 1

    @property
    def dimension(self,):
        return self.__class__.DIMENSION

    @property
    def step_function(self, ta, tb, previous_states, current_states):
        raise NotImplementedError("You need to implement the step function of uncertainty %s." % self.__class__.__name__)

    @property
    def dependancies(self,):
        return set()

    def get_reservation_requests(self,):
        return (self, self.dimension)

    @property
    def innovations(self,):
        return set()

    @property
    def initial_value(self,):
        raise NotImplementedError("You need to implement get_initial_states in your uncertainty model.")

    def get_initial_states(self, nb_paths, t):
        """
        By default, we use _get_initial_value
        for this metho    
        """
        v0 = self.initial_value
        return np.repeat(v0, nb_paths).reshape((self.dimension, nb_paths))
    
    def cursor(self, val, t):
        return val