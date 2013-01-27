import numpy as np
#import matplotlib.pyplot as plt

from sys import path
from os import path as osp

CURDIR = osp.abspath(osp.dirname(__file__))
path.append(CURDIR + "/../../../src")

from strongchicken.uncertainties import BlackScholes
from strongchicken.uncertainties import ForwardSimulator
from strongchicken.uncertainties import UncertaintySystem
from strongchicken.utils import *

# this is the timeline on which we want to perform the simulation
timeline = np.arange(0., UNIT.YEAR, UNIT.DAY)

# ... a BS market with 20% / sqrt(year) of volatilty
market = BlackScholes(36., .06*INV.YEAR, .2*INV.SQRT.YEAR)

uncertainty_system = UncertaintySystem([market])

# and the simulator, we're all set to begin the simulation!
nb_paths = 1000
simulator = ForwardSimulator(uncertainty_system, timeline, nb_paths)

paths = np.zeros((len(timeline), nb_paths))
for (t_id,t) in enumerate(timeline):
	paths[t_id,:] = simulator.state[market]
	simulator.go_next()
print paths.mean(axis=1)

#plt.plot(paths)
#plt.savefig("tutorial1_1factor.png")