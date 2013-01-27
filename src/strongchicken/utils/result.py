import numpy as np
from numpy import sqrt
from scipy.stats import norm



def wrap_antithetic(u):
  (D, S) = u.shape
  assert D==1
  pivot = (S+1)/2
  res = np.zeros((1,pivot))
  res = (u[:pivot] + u[-pivot:])/2.
  return res


class Result:
    """ Result of some computation
    
    Many computation are giving back
    an estimation rather than an accurate result.
    This object includes informations about
    the precision of the estimation.
    """

    def is_exact():
        """ Returns true if the result is exact
        
        Returns true for an analytical computation.
        false for an estimation.
        """
        raise

    def is_compatible(self, x, confidence=0.95):
        """ Returns true if the likelihood of our 
        estimator knowing that the real value is x is
        less than 0.95.
        (m,M) = self.get_interval(confidence)
        return m <= x <= M
        """

    def get_interval(self, confidence=0.95):
        """ Returns a confidence interval
        """
        p = (1. - p) / 2.
        error = -norm.ppf(p)
        return s


class ExactResult(Result):
    """ Exact result.
    """
    def __init__(self, r):
        self.result = result

    def get_interval(self, confidence=0.95):
        return (self.result * 0.9999, self.result * 1.0001)


class EstimationResult(Result):
    """ Estimation of the result
    """
    def is_exact():
        return False


class MonteCarloEstimation(EstimationResult):
    """ Estimation given by a Monte-Carlo method
        
    In this implementation we consider 
    that the standard deviation of the sample
    is a correct estimation of the standard estimation
    of the random value. 
    
    TODO Fix this, Actually this should be a Student Law !!!
    """
    def __init__(self, sample, antithetic=False):
        if antithetic:
            wrapped_sample = wrap_antithetic(sample)
            MonteCarloEstimation.__init__(wrapped_sample)
        else:
            nb_sample = sample.shape[-1]
            self.mean = sample.mean()
            self.std = sample.std(ddof=1) / sqrt(nb_sample)
    
    def get_interval(self, confidence=0.95):
        p = (1. - confidence)
        margin_in_std = -norm.ppf(p)
        return self.mean - margin_in_std * self.std, self.mean + margin_in_std * self.std

    def is_compatible(self, x, confidence=0.95):
        (m, M) = self.get_interval(confidence)
        return m <= x <= M

    def __repr__(self,):
        return "\n".join(str(100. * confidence) + "% confidence : " + "[%.4f,%4f]" % self.get_interval(confidence)
                  for confidence in [.8, .9, .95])
