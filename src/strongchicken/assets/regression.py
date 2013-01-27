import numpy as np
from numpy.linalg import lstsq, norm
from strongchicken.utils import compose, positive, strictly_positive


def image(X, functions):
    nb_functions = len(functions)
    f_X = np.zeros((len(functions), X.shape[-1]))
    for (i, f) in enumerate(functions):
        f_X[i] = f(X) # s, n
    return f_X

def regression_check(f):
    def aux(X,Y):
        assert len(Y.shape) == 1
        assert Y.shape[0] == X.shape[1]
        assert X.shape[1] > X.shape[0]
        return f(X,Y)
    return aux

def get_regression_coefficients(functions, X, Y):
    return lstsq(image(X, functions).T, Y.flatten())[0]


def base_function_regression(functions):
    def regression(X, Y):
        L = get_regression_coefficients(functions, X, Y)
        def regressed_function(x):
            nb_sims, nb_dims = x.shape
            f_X = image(x, functions)
            return np.inner(L, f_X.T)
        return regressed_function
    return regression_check(regression)

def extract_dim(d):
    return lambda x:x[d]



def local_basis_function(limits,
                         local_weights,
                         functions):
    """
    Result of a local basis 
    regression.

    local weights is an array such that
    local_weights[i] contains the weight
    w0, w1, ..., wN such that
     R(x) = w0.f0 + ... + wN.fN for
     local_weight[i] <= x < local_weight[i+1]
    """
    N = len(functions)
    L = len(limits)
    assert local_weights.shape == (L+1,N)
    def aux(X):
        (D,S) = X.shape
        assert D==1
        idx = np.searchsorted(limits,X).flatten()
        weights = local_weights[idx].T
        assert (N,S) == weights.shape
        Y = image(X, functions)
        assert (N,S) == Y.shape
        return (weights*Y).sum(0)
    return aux


def local_basis_regression(functions, M=10):
    """
    M is then number of local basis
    """
    assert M>1
    N = M-1
    L=len(functions)
    def aux(X,Y):
        (D,S) = X.shape
        assert D==1
        # at the moment only works with dim 1
        order = np.argsort(X).flatten()
        X_ = X[...,order]
        Y_ = Y[order]
        K=S/M
        limits = [ X[0,i*K]    
               for i in range(1,M) ]
        local_weights = np.zeros((M,L))
        for i in range(0,M):
            seg = slice(i*K, (i+1)*K)
            local_weights[i] = get_regression_coefficients(functions, X_[...,seg], Y_[seg])        
        return  local_basis_function(limits, local_weights, functions)
    return aux

def local_linear_regression(M=10):
    functions = [
        extract_dim(0),
        lambda x:np.ones(x.shape[0])
    ]
    return local_basis_regression(functions,M)

def polynomial_regression(X, Y):
    functions = []
    nb_dims, nb_sims = X.shape
    functions = [ lambda x:np.ones(x.shape[0]) ] \
      + [ extract_dim(d)
          for d in range(nb_dims) ] \
      + [ compose(lambda x:x * x, extract_dim(d))
          for d in range(nb_dims) ]
    return base_function_regression(functions)(X, Y)

def force_positive_regression(regression):
    return lambda X, Y:compose(strictly_positive, regression(X, Y))

def linear_regression(X, Y):
    functions = []
    nb_dims, nb_sims = X.shape
    functions.append(lambda x:np.ones(nb_sims))
    for d in range(nb_dims):
        functions.append(extract_dim(d))
    return base_function_regression(functions)(X, Y)

