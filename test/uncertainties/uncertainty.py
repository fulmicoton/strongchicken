import unittest
import numpy as np

from strongchicken.uncertainties import ForwardSimulator, BidirectionalSimulator
from strongchicken.uncertainties import BlackScholes, HistoricalData, Market1F

from strongchicken.uncertainties import UncertaintySystem
from strongchicken.uncertainties import allocate_helper
from strongchicken.core import RegularTimeSerie
from strongchicken.utils import *
from math import pi


class TestState(unittest.TestCase):

    def test_allocate_state(self,):
        test_data = [ ("a", 3),
                      ("b", [
                              ("ba", 2),
                              ("bb", 2),
                             ]) ]
        result_data = (7, {
                            "all": slice(0, 7),
                            "a"  : slice(0, 3),
                            "b"  : slice(3, 7),
                                "ba"  : slice(3, 5),
                                "bb"  : slice(5, 7),
                          })
        self.assertEqual(allocate_helper("all", test_data), result_data)




class TestBlackScholes(unittest.TestCase):

    def setUp(self):
        self.model = BlackScholes(
             55.,
             0.0,
             0.20)
        self.timeline = np.arange(0., 1., 1. / 52.)

    def test_forward(self):
        simulator = ForwardSimulator(UncertaintySystem([self.model]), self.timeline, 10000)
        model_state = simulator.state[self.model]
        while (simulator.go_next()):
            pass


    def test_antithetic(self):
        simulator = ForwardSimulator(UncertaintySystem([self.model]), self.timeline, 10000, True)
        model_state = simulator.state[self.model]
        while (simulator.go_next()):
            pass
    
    def test_bidirectional_simulator(self):
        simulator = BidirectionalSimulator(UncertaintySystem([self.model]), self.timeline, 10000)
        while (simulator.go_back()):
            pass



class TestMarket1F(unittest.TestCase):
    def setUp(self,):
        self.timeline = np.arange(0., UNIT.YEAR, UNIT.DAY)
        self.F0 = RegularTimeSerie(0., UNIT.DAY, 50.+10.*np.sin(INV .WEEK*self.timeline) )
        self.market = Market1F(self.F0, .0*INV.YEAR, 0.2 * INV.SQRT.YEAR, INV.WEEK)

    def test_spot(self):
        simulator = ForwardSimulator(UncertaintySystem([self.market]), self.timeline, 10000)
        while (simulator.go_next()):
            forward_curves = simulator.state.cursor(self.market) 
            error = np.abs( forward_curves.spot().mean() - self.F0(simulator.t) )
            self.assertTrue( np.all(error < .05))



class TestHistoricalData(unittest.TestCase):

    def setUp(self,):
        self.timeline = np.arange(0, 3, 1.)
        self.model = HistoricalData(
            [ np.array([[1., 2., 3.]]),
              np.array([[1., 4., 9.]]),
              np.array([[1., 8., 27.]]), ],
              self.timeline)

    def test_forward(self):
        simulator = ForwardSimulator(UncertaintySystem([self.model]), self.timeline, 2)
        model_state = simulator.state[self.model]
        self.assertTrue((model_state == np.array([[1., 2.]])).all())
        simulator.go_next()
        model_state = simulator.state[self.model]
        self.assertTrue((model_state == np.array([[1., 4.]])).all())
        simulator.go_next()
        model_state = simulator.state[self.model]
        self.assertTrue((model_state == np.array([[1., 8.]])).all())
        simulator.go_next()
        model_state = simulator.state[self.model]

















