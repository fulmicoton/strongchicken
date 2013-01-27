import unittest

from strongchicken.utils import *
from strongchicken.assets.regression import *

class TestAsset(unittest.TestCase):

    def setUp(self):
        pass
    
    def test_polynomial(self,):
        X = np.random.random((1, 100))
        Y = (0.5 * X * X + 1.5 * X + 2.).flatten()
        regressed_function = polynomial_regression(X, Y)
        assert (norm(regressed_function(X) - Y) < 1e-6).all()


    def test_linear(self,):
        X = np.random.random((2, 100))
        A = np.array([ 3., 4.])
        Y = (np.inner(A, X.T) + 1.)
        regressed_function = linear_regression(X, Y)
        assert norm(regressed_function(X) - Y) < 1e-4
        X += 0.1 * np.random.random((2, 100))
        regressed_function = linear_regression(X, Y)
        assert (norm(regressed_function(X) - Y) / norm(Y) < .1).all()

    def test_local_basis_function(self,):
        X=np.random.random((1.,100))
        functions = [
            extract_dim(0),
            lambda x:np.ones(x.shape[0])
        ]
    	R = local_basis_function([0.5],
                         np.array([[0,-1.],[0.,1.]]),
                         functions)
        assert np.all( (X>0.5).flatten() == (R(X)==1.) )
    
    def test_local_linear_regression(self,):
        X = np.random.random((1, 10000))
        Y = np.sin(X).flatten()
        regressed_function = local_linear_regression(M=10)(X, Y)
        assert (norm(regressed_function(X) - Y)/norm(Y) < 1e-1)