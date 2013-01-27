# coding=utf-8

import numpy as np


#class TimeSerie:
#
#	def __init__(self, timeline, values,):
""" Defines a time serie beginning at t0 and ending
at +∞. If the timeline go t0, ... tN, and values
go v0, ... , vN, it is interpreted as :

∀i, f(t)=v_i when t_i ≤ t < t_i

and

f(t) = v_N if t>t_N
"""
#		self.


class TimeSerie:
    pass

class RegularTimeSerie(TimeSerie):

    def __init__(self, t0, time_step, values):
    	"""
    	Defines a time serie with a 
    	regular time step.
    	"""
        self.t0 = t0
        self.time_step = time_step
        self.values = values

    def __call__(self,t):
    	"""
    	Accepts float or vector.
    	When t is a vector, returns a vector of the same
    	dimension.
    	"""
        t_id = np.int_( (t-self.t0) / self.time_step ) 
        #assert np.all(0 <= t_id < self.values.size)
        return self.values[t_id]