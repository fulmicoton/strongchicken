from collections import defaultdict
from state import allocate_state
import numpy as np

def build_innovation_generators(innovations):
    innovations_grouped_by_type = defaultdict(list)
    for innovation in innovations:
        innovations_grouped_by_type[innovation.__class__].append(innovation)
    return [ generator_class.InnovationSystem(innovations)
             for (generator_class, innovations) in innovations_grouped_by_type.items() ]


class ForwardSimulator:

    def __init__(self, uncertainty_system, timeline, nb_simulations, antithetic=False):
        self.timeline = sorted(timeline)
        assert self.timeline[0] == 0.
        self.antithetic = antithetic
        self.uncertainty_system = uncertainty_system
        innovations = uncertainty_system.innovations
        self.innovation_systems = build_innovation_generators(innovations)
        self.tid = 0
        self.nb_simulations = nb_simulations
        reservation_request = [ self.uncertainty_system.get_reservation_requests()
                              ] + [ innovation_system.get_reservation_requests()
                                    for innovation_system in self.innovation_systems ]
        self.state = allocate_state(reservation_request, nb_simulations)
        for uncertainty in self.uncertainty_system:
            initial_states = uncertainty.get_initial_states(nb_simulations, self.timeline[0])
            self.state._set_state(uncertainty, initial_states)
        self.state.tid = 0
        self.next_state = self.state.copy()
    
    def apply_step(self, t_a, t_b):
        if self.antithetic:
            S = self.nb_simulations
            S_p = (S+1)/2
            S_n = S/2
            assert S == S_p + S_n
            for innovation_system in self.innovation_systems:
                computed_innovations = innovation_system.compute_innovation(self.t, S_p)
                (D,S_) = computed_innovations.shape
                assert S_ == S_p
                innovations_value = np.zeros((D, S))
                innovations_value[:,:S_p] = computed_innovations[:,:S_p]
                innovations_value[:,S_p:] = -computed_innovations[:,:S_n]
                self.next_state._set_state(innovation_system, innovations_value)
        else:
            for innovation_system in self.innovation_systems:
                computed_innovations = innovation_system.compute_innovation(self.t, self.nb_simulations)
                self.next_state._set_state(innovation_system, computed_innovations)
        for uncertainty in self.uncertainty_system:
            self.next_state._set_state(uncertainty,
                                   uncertainty.step_function(t_a, t_b, self.state, self.next_state))
        self.next_state.t = t_b
        self.swap_states()
    
    def swap_states(self,):
        self.state, self.next_state = self.next_state, self.state

    @property
    def t(self,):
        return self.timeline[self.tid]

    def go_next(self,):
        if self.tid < len(self.timeline) - 1:
            t_a, t_b = self.timeline[self.tid:self.tid + 2]
            self.apply_step(t_a, t_b)
            self.tid += 1
            self.state.tid = self.tid
            return True
        else:
            return False

    def go_end(self,):
        while self.go_next():
            pass



class BidirectionalSimulator:

    def __init__(self,
            uncertainty_system,
            timeline,
            nb_simulations,
            **kargs):
        self.timeline = timeline
        self.tid = len(self.timeline) - 1
        self.nb_simulations = nb_simulations
        self.states = []
        simulator = ForwardSimulator(uncertainty_system, timeline, nb_simulations, **kargs)
        self.states.append(simulator.state.copy())
        while simulator.go_next():
            self.states.append(simulator.state.copy())
        self.state = simulator.state

    @property
    def t(self,):
        return self.timeline[self.tid]

    @property
    def previous(self,):
        return self.states[self.tid - 1]

    def go_back(self,):
        if self.tid > 0:
            self.tid -= 1
            self.state = self.states[self.tid]
            return True
        else:
            return False

    def go_next(self,):
        if self.tid < len(self.timeline) - 1:
            self.tid += 1
            self.state = self.states[self.tid]
            return True
        else:
            return False

    def go_end(self,):
        self.tid = len(self.timeline) - 1
