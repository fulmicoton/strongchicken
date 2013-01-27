import numpy as np
from innovation import GaussianNoise
from uncertainty import Uncertainty


""" the first dimension is the simulations """

class BlackScholes(Uncertainty):

    def __init__(self, S, rate, vol, w=None):
        self.S = S
        self.vol = vol
        self.rate = rate
        self.w = w or GaussianNoise()
        self.initial_value = S

    @property
    def innovations(self,):
        return [ self.w ]

    def step_function(self, ta, tb, previous_states, current_states):
        dt = tb - ta
        jump_amplitude = np.sqrt(dt) * self.vol
        drift = (self.rate - .5 * self.vol * self.vol) * dt
        log_return = drift + jump_amplitude * current_states[self.w]
        return previous_states[self] * np.exp(log_return)


class HistoricalData(Uncertainty):

    def __init__(self, data, timeline):
        # time, dim, sims
        assert len(data) == len(timeline) > 1
        assert reduce(lambda x, y: x == y and y,
                      [ d.shape for d in data ])
        self.data = data
        self.timeline = timeline

    @property
    def dimension(self,):
        return self.data[0].shape[0]

    def get_state_at_t(self, nb_paths, t):
        assert t >= self.timeline[0]
        t_id = np.searchsorted(self.timeline, t, "right") - 1
        return self.data[t_id][:, slice(0, nb_paths)]

    def get_initial_states(self, nb_paths, t):
        return self.get_state_at_t(nb_paths, t)

    def step_function(self, ta, tb, previous_states, current_states):
        return self.get_state_at_t(previous_states.nb_simulations, tb)



class Market1F(Uncertainty):

    class ForwardCurve: # TODO check out terminology Future vs Fwd curve
    
        def __init__(self, market1f, risk_factor, t):
            self.market1f = market1f
            self.risk_factor = risk_factor
            self.t = t
        
        def spot(self,):
            t = self.t
            a = self.market1f.mean_reverting
            vol = self.market1f.vol
            r = self.market1f.rate
            F_t0 = self.market1f.F0
            scaling = r*t - vol*vol*( 1. - np.exp(-2.*a*t))/(2.*a)
            return F_t0(t) * np.exp( scaling + self.risk_factor)
            
        def eval(self, ts):
            T = len(ts)
            assert np.all(ts>=self.t)
            t = self.t
            dt = ts-t
            a = self.market1f.mean_reverting
            vol = self.market1f.vol
            r = self.market1f.rate
            F_t0 = self.market1f.F0
            scaling = r*t - np.exp(-2.*a*dt)*vol*vol*( 1. - np.exp(-2.*a*t))/(2.*a)
            assert scaling.shape == ts.shape
            (a,S) = self.risk_factor.shape
            assert a==1 and S>1 
            stochastic = np.outer(np.exp(-a*dt), self.risk_factor)
            assert stochastic.shape == (T,S)
            return F_t0(ts).reshape((T,1)) *  np.exp( scaling.reshape(T,1) + stochastic )
    
    def __init__(self, F0, rate, vol, mean_reverting, w=None):
        self.F0 = F0
        self.rate = rate
        self.vol = vol
        self.mean_reverting = mean_reverting
        self.w = w or GaussianNoise()
        self.initial_value = 0.
    
    @property
    def innovations(self,):
        return [ self.w ]

    def step_function(self, ta, tb, previous_states, current_states):
        dt = tb-ta
        sdt = np.sqrt(dt)
        forget_factor = np.exp(-self.mean_reverting*dt)
        amplitude = self.vol * np.sqrt(  (  1. - np.exp(-2.*self.mean_reverting*dt )  ) / (2.*self.mean_reverting)  )
        return forget_factor * previous_states[self] + amplitude * current_states[self.w]
    

    def cursor(self, data, t):
        return Market1F.ForwardCurve(self, data, t)