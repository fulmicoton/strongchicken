import sys
import os

from os import path
exec_name = sys.argv[0]
exec_dir = path.dirname(exec_name)
strongchicken_path = path.join(exec_dir, "../src/")
sys.path.append(strongchicken_path)

from strongchicken.uncertainties import *
from strongchicken.core import *
from strongchicken.utils import *

#from pylab import plot, show

timeline = np.arange(0., UNIT.YEAR, UNIT.DAY)
F0 = RegularTimeSerie(0., UNIT.DAY, 50.+10.*np.sin(INV .WEEK*timeline) )
market = Market1F(F0, .0*INV.YEAR, 0.2 * INV.SQRT.YEAR, INV.WEEK)

simulator = ForwardSimulator(UncertaintySystem([market]), timeline, 10)
for i in range(10):
	forward_curves = simulator.state.cursor(market)
	print forward_curves.spot()
	simulator.go_next()

#plot(F0(timeline)) 
#show()
