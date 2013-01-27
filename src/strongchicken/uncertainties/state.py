import numpy as np


def allocate_helper(key, contents=1, offset=0):
    """
        Allocation requests is a list of allocation request.
        An allocation consists of either :
            - (key, dimension),
            - or (key, list of allocation requests).
            
        This function returns the total dimension for the system, and a map
        with the requested slice.
    """
    if contents.__class__ == int:
        suboffset = offset + contents
        return (suboffset, { key: slice(offset, suboffset) })
    elif contents.__class__ == list:
        reservations = {}
        suboffset = offset
        for (subkey, subcontent) in contents:
            (suboffset, subreservations) = allocate_helper(subkey, subcontent, suboffset)
            reservations.update(subreservations)
        reservations[key] = slice(offset, suboffset)
        return (suboffset, reservations)

def allocate_state(contents, nb_simulations):
    nb_dimensions, uncertainty_map = allocate_helper("all", contents)
    return State(uncertainty_map, np.zeros((nb_dimensions, nb_simulations)), 0)


class State:

    def __init__(self, uncertainty_map, data, tid):
        self._uncertainty_map = uncertainty_map
        self._data = data
        self.nb_simulations = data.shape[-1]
        self.tid = tid
        self.t = 0
    
    def cursor(self, uncertainty):
        vals = self[uncertainty]
        return uncertainty.cursor(vals, self.t)
    
    def __getitem__(self, uncertainty):
        return self._data[ self._uncertainty_map[uncertainty] ] 
        
    def __setitem__(self, uncertainty):
        raise AttributeError("You're not supposed to set a state.")

    def _set_state(self, uncertainty, value):
        assert value.shape[-1] == self.nb_simulations
        self._data[ self._uncertainty_map[uncertainty], : ] = value
    
    def copy(self,):
        return State(self._uncertainty_map,
                     self._data.copy(),
                     self.tid)

    def mask(self, simulations):
        return StateMask(self, simulations)


class StateMask:

    def __init__(self, state, simulations):
        self.simulations = simulations
        self.nb_simulations = simulations.shape[0]
        self.state = state
    
    def __getitem__(self, uncertainty):
        return self.state[uncertainty][:, self.simulations]
    
    def cursor(self, uncertainty):
        data = self[uncertainty]
        return uncertainty.cursor(data, self.t)
    
    @property
    def tid(self,):
        return self.state.tid

    @property
    def t(self,):
        return self.state.t

