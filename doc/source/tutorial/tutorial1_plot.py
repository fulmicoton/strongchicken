import numpy as np
import matplotlib.pyplot as plt
from strongchicken.uncertainties import Market1F
from strongchicken.uncertainties import ForwardSimulator
from strongchicken.uncertainties import UncertaintySystem
from strongchicken.core import RegularTimeSerie
from strongchicken.utils import *

# this is the timeline on which we want to perform the simulation
timeline = np.arange(0., UNIT.YEAR, UNIT.DAY)

# ... and this is the initial forward curve
F0 = RegularTimeSerie(0., UNIT.DAY, 50.+10.*np.sin(INV.WEEK*timeline) )

# ... the market : 80% / sqrt(year) of volatilty
market = Market1F(F0, .0*INV.YEAR, .8 * INV.SQRT.YEAR, INV.WEEK)

uncertainty_system = UncertaintySystem([market])

# and the simulator, we're all set to begin the simulation!
nb_paths = 5
simulator = ForwardSimulator(uncertainty_system, timeline, nb_paths)

paths = np.zeros((len(timeline), nb_paths))
for (t_id,t) in enumerate(timeline):
	paths[t_id,:] = simulator.state.cursor(market).spot()
	simulator.go_next()

plt.plot(paths)
plt.savefig("tutorial1_1factor.png")