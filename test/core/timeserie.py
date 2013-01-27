import unittest
import numpy as np
#from strongchicken.utils import *

from strongchicken.core import RegularTimeSerie

class TestTimeSerie(unittest.TestCase):

    def setUp(self):
        self.timeserie = RegularTimeSerie(1., .01, np.sin(np.arange(1., 3., 0.01)))
    
    def test_timeserie(self,):
        ts = np.arange(1., 3., 0.007)
        err = np.sin(ts)-self.timeserie(ts)
        self.assertTrue( (-.01 <= err).all() )
        self.assertTrue( (err <= .01).all() )

    def test_simple_timeserie(self,):
        timeserie = RegularTimeSerie(1., .01, [0., 1., 2., 3.])
        self.assertEqual(timeserie(1.), 0.)
        self.assertEqual(timeserie(1.009), 0.)
        self.assertEqual(timeserie(1.01), 1.)
        self.assertEqual(timeserie(1.015), 1.)
        self.assertEqual(timeserie(1.02), 2.)
