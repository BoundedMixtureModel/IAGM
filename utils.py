import sys
import numpy as np
from scipy.stats import gamma, wishart, norm
from scipy.stats import multivariate_normal as mv_norm
from numpy.linalg import inv, det, slogdet
from scipy import special
from ars import ARS
import mpmath


# the maximum positive integer for use in setting the ARS seed
maxsize = sys.maxsize


# def posterior_distribution_s_ljk(s_ljk, s_rjk, nj, beta, w, sum):
#     s_ljk = mpmath.mpf(s_ljk)
#     s_rjk = mpmath.mpf(s_rjk)
#     return mpmath.power(1/(mpmath.power(s_ljk, -0.5) + mpmath.power(s_rjk, -0.5)), nj) \
#         * mpmath.power(s_ljk, (beta/2-1)) \
#         * mpmath.exp(-0.5*s_ljk*sum) \
#         * mpmath.exp(-0.5*w*beta*s_ljk)

def compare_s_ljk(s_ljk, previous_s_ljk, s_rjk, nj, beta, w, sum):
    s_ljk = mpmath.mpf(s_ljk)
    s_rjk = mpmath.mpf(s_rjk)
    a1 = mpmath.power(s_ljk, -0.5) + mpmath.power(s_rjk, -0.5)
    a2 = mpmath.power(previous_s_ljk, -0.5) + mpmath.power(s_rjk, -0.5)
    ratio_a = a2/a1
    ratio_a_power = np.power(ratio_a, nj)
    ratio_b = mpmath.power(s_ljk, (beta/2-1)) * mpmath.exp(-0.5*s_ljk*sum) * mpmath.exp(-0.5*w*beta*s_ljk) \
            / (mpmath.power(previous_s_ljk, (beta/2-1)) * mpmath.exp(-0.5*previous_s_ljk*sum) * mpmath.exp(-0.5*w*beta*previous_s_ljk))
    return ratio_a_power * ratio_b


def Metropolis_Hastings_Sampling_posterior_sljk(s_ljk, s_rjk, nj, beta, w, sum):
    n = 100
    x = s_ljk
    vec = []
    vec.append(x)
    for i in range(n):
        # proposed distribution make sure 25%-40% accept
        # random_walk algorithm, using symmetric Gaussian distribution, so it's simplified to Metropolis algoritm
        # the parameter is mu: the previous state of x and variation
        candidate = norm.rvs(x, 0.75, 1)[0]
        if candidate <= 0:
            candidate = np.abs(candidate)
        # acceptance probability
        alpha = min([1., compare_s_ljk(candidate, x, s_rjk, nj, beta, w, sum)])
        # alpha = min([1., posterior_distribution_s_ljk(candidate, s_rjk, nj, beta, w, sum)/
        #              posterior_distribution_s_ljk(x, s_rjk, nj, beta, w, sum)])
        u = np.random.uniform(0,1)
        if u < alpha:
            x = candidate
            vec.append(x)
    return vec[-1]


# def posterior_distribution_s_rjk(s_rjk, s_ljk, nj, beta, w, sum):
#     s_ljk = mpmath.mpf(s_ljk)
#     s_rjk = mpmath.mpf(s_rjk)
#     return mpmath.power((mpmath.power(s_ljk, -0.5) + mpmath.power(s_rjk, -0.5)), -nj) \
#         * mpmath.power(s_rjk, (beta/2-1)) \
#         * mpmath.exp(-0.5*s_rjk*sum) \
#         * mpmath.exp(-0.5*w*beta*s_rjk)


def compare_s_rjk(s_rjk, previous_s_rjk, s_ljk, nj, beta, w, sum):
    s_ljk = mpmath.mpf(s_ljk)
    s_rjk = mpmath.mpf(s_rjk)
    a1 = mpmath.power(s_ljk, -0.5) + mpmath.power(s_rjk, -0.5)
    a2 = mpmath.power(s_ljk, -0.5) + mpmath.power(previous_s_rjk, -0.5)
    ratio_a = a2/a1
    ratio_a_power = np.power(ratio_a, nj)
    ratio_b = mpmath.power(s_rjk, (beta/2-1)) * mpmath.exp(-0.5*s_rjk*sum) * mpmath.exp(-0.5*w*beta*s_rjk) \
            / (mpmath.power(previous_s_rjk, (beta/2-1)) * mpmath.exp(-0.5*previous_s_rjk*sum) * mpmath.exp(-0.5*w*beta*previous_s_rjk))
    return ratio_a_power * ratio_b


def Metropolis_Hastings_Sampling_posterior_srjk(s_ljk, s_rjk, nj, beta, w, sum):
    n = 100
    x = s_rjk
    vec = []
    vec.append(x)
    for i in range(n):
        # proposed distribution make sure 25%-40% accept
        # random_walk algorithm, using symmetric Gaussian distribution, so it's simplified to Metropolis algoritm
        # the parameter is mu: the previous state of x and variation
        candidate = norm.rvs(x, 0.75, 1)[0]
        if candidate <= 0:
            continue
        # acceptance probability
        alpha = min([1., compare_s_rjk(candidate, x, s_ljk, nj, beta, w, sum)])
        # alpha = min([1., posterior_distribution_s_rjk(candidate, s_ljk, nj, beta, w, sum)/
        #              posterior_distribution_s_rjk(x, s_ljk, nj, beta, w, sum)])
        u = np.random.uniform(0,1)
        if u < alpha:
            x = candidate
            vec.append(x)
    return vec[-1]


def beta_posterior_distribution(beta, w, s_l, M, k):
    product_sequence = [(mpmath.power(s_l[j][k]*w[k], 0.5*beta) * mpmath.exp(-0.5*s_l[j][k]*beta*w[k]))
                        for j in range(M)][0]
    return mpmath.power(special.gamma(0.5*beta), -M) \
        * mpmath.exp(- 0.5/beta)\
        * mpmath.power(0.5*beta, 0.5*(M*beta-3))\
        * product_sequence




def Metropolis_Hastings_Sampling_beta(beta, w, s_l, M, k):
    n = 100
    x = beta
    vec = []
    vec.append(x)
    for i in range(n):
        # proposed distribution make sure 25%-40% accept
        # random_walk algorithm, using symmetric Gaussian distribution, so it's simplified to Metropolis algoritm
        # the parameter is mu: the previous state of x and variation
        candidate = norm.rvs(x, 0.5, 1)[0]
        if candidate <= 0:
            candidate = np.abs(candidate)
        # acceptance probability
        # alpha = min([1., compare_s_rjk(candidate, x, s_ljk, nj, beta, w, sum)])
        alpha = min([1., beta_posterior_distribution(candidate, w, s_l, M, k)/
                     beta_posterior_distribution(x, w, s_l, M, k )])
        u = np.random.uniform(0,1)
        if u < alpha:
            x = candidate
            vec.append(x)
    return vec[-1]


def Asymmetric_Gassian_Distribution(xik, mu_jk, s_ljk, s_rjk):
    # if xik < mu_jk:
    #     print( mpmath.sqrt(2/mpmath.pi)/(mpmath.power(s_ljk, -0.5) + mpmath.power(s_rjk, -0.5))\
    #            * mpmath.exp(- 0.5 * s_ljk * (xik- mu_jk)**2))
    # else:
    #     print( mpmath.sqrt(2/mpmath.pi)/(mpmath.power(s_ljk, -0.5) + mpmath.power(s_rjk, -0.5))\
    #            * mpmath.exp(- 0.5 * s_rjk * (xik- mu_jk)**2))
    if xik < mu_jk:
        return mpmath.sqrt(2/mpmath.pi)/(mpmath.power(s_ljk, -0.5) + mpmath.power(s_rjk, -0.5))\
               * mpmath.exp(- 0.5 * s_ljk * (xik- mu_jk)**2)
    else:
        return mpmath.sqrt(2/mpmath.pi)/(mpmath.power(s_ljk, -0.5) + mpmath.power(s_rjk, -0.5))\
               * mpmath.exp(- 0.5 * s_rjk * (xik- mu_jk)**2)



def Metropolis_Hastings_Sampling_AGD(mu_jk, s_ljk, s_rjk, size, n=10000):
    x = norm.rvs(0, 2.5, 1)[0]
    vec = []
    vec.append(x)
    for i in range(n):
        # print(i)
        # proposed distribution make sure 25%-40% accept
        # random_walk algorithm, using symmetric Gaussian distribution, so it's simplified to Metropolis algoritm
        # the parameter is mu: the previous state of x and variation
        candidate = norm.rvs(x, 3, 1)[0]
        # acceptance probability
        alpha = min([1., Asymmetric_Gassian_Distribution(candidate, mu_jk, s_ljk, s_rjk) /
                     Asymmetric_Gassian_Distribution(x, mu_jk, s_ljk, s_rjk)])
        u = np.random.uniform(0, 1)

        if u < alpha:
            x = candidate
            vec.append(x)
        # the sample results is enough
        if len(vec) >= (size+500):
            print(i)
            break
    return vec[-size:]


def integral_approx(X, lam, r, beta_l, beta_r, w_l, w_r, G=1, size=1):
    """
    estimates the integral, eq 17 (Rasmussen 2000)
    """
    size = 1
    N, D = X.shape
    temp = np.zeros(len(X))
    i = 0
    while i < size:
        # print(i)
        mu = np.array([np.squeeze(norm.rvs(loc=lam[k], scale=1/r[k], size=1)) for k in range(D)])
        s_l = np.array([np.squeeze(draw_gamma(beta_l[k] / 2, 2 / (beta_l[k] * w_l[k]))) for k in range(D)])
        s_r = np.array([np.squeeze(draw_gamma(beta_r[k] / 2, 2 / (beta_r[k] * w_r[k]))) for k in range(D)])
        ini = np.ones(len(X))
        for k in range(D):
            # use metropolis-hastings algorithm to draw sampling from AGD
            # the size parameter is the required sampling number which is equal to the dataset's number
            # the n parameter is MH algorithm itering times,because the acceptance rate should be 25%-40%
            test = Metropolis_Hastings_Sampling_AGD(mu[k], s_l[k], s_r[k], size=N, n=N*50)
            # print(test)
            ini *= test

        temp += ini
        i += 1
    return temp/float(size)


def log_p_alpha(alpha, k, N):
    """
    the log of eq15 (Rasmussen 2000)
    """
    return (k - 1.5)*np.log(alpha) - 0.5/alpha + special.gammaln(alpha) - special.gammaln(N + alpha)


def log_p_alpha_prime(alpha, k, N):
    """
    the derivative (wrt alpha) of the log of eq 15 (Rasmussen 2000)
    """
    return (k - 1.5)/alpha + 0.5/(alpha*alpha) + special.psi(alpha) - special.psi(alpha + N)


def log_p_s_ljk(s_ljk, s_rjk, w, beta, N, cumculative_sum_equation):
    return -N*np.log(np.power(s_ljk, -0.5) + np.power(s_rjk, -0.5)) \
        - 0.5*s_ljk*cumculative_sum_equation \
        + (beta/2 - 1)*np.log(s_ljk) \
        - 0.5*w*beta*s_ljk


def log_p_s_ljk_prime(s_ljk, s_rjk, w, beta, N, cumculative_sum_equation):
    return 0.5*N*np.power(s_ljk, -1.5) / (np.power(s_ljk, -0.5) + np.power(s_rjk, -0.5)) \
        - 0.5*cumculative_sum_equation \
        + (beta/2 - 1)/s_ljk \
        - 0.5*w*beta


def log_p_s_rjk(s_rjk, s_ljk, w, beta, N, cumculative_sum_equation):
    return -N*np.log(np.power(s_ljk, -0.5) + np.power(s_rjk, -0.5)) \
        - 0.5*s_rjk*cumculative_sum_equation \
        + (beta/2 - 1)*np.log(s_rjk) \
        - 0.5*w*beta*s_rjk


def log_p_s_rjk_prime(s_rjk, s_ljk,  w, beta, N, cumculative_sum_equation):
    return 0.5*N*np.power(s_rjk, -1.5) / (np.power(s_ljk, -0.5) + np.power(s_rjk, -0.5)) \
        - 0.5*cumculative_sum_equation \
        + (beta/2 - 1)/s_rjk \
        - 0.5*w*beta


def log_p_beta_full_cov(beta,k=1,s=1,w=1,D=1,logdet_w=1,cumculative_sum_equation=1):
    """
    The log of the second part of eq 9 (Rasmussen 2000)
    the covariance matrix of the model is full cov
    """
    return -1.5*np.log(beta - D + 1.0) \
        - 0.5*D/(beta - D + 1.0) \
        + 0.5*beta*k*D*np.log(0.5*beta) \
        + 0.5*beta*k*logdet_w \
        + 0.5*beta*cumculative_sum_equation \
        - k*special.multigammaln(0.5*beta, D)

def log_p_beta_prime_full_cov(beta,k=1,s=1,w=1,D=1,logdet_w=1,cumculative_sum_equation=1):
    """
    The derivative (wrt beta) of the log of eq 9 (Rasmussen 2000)
    the covariance matrix of the model is full cov
    """
    psi = 0.0
    for j in range(1,D+1):
        psi += special.psi(0.5*beta + 0.5*(1.0 - j))
    return -1.5/(beta - D + 1.0) \
        + 0.5*D/(beta - D + 1.0)**2 \
        + 0.5*k*D*(1.0 + np.log(0.5*beta)) \
        + 0.5*k*logdet_w \
        + 0.5*cumculative_sum_equation \
        - 0.5*k*psi

def log_p_beta_diagonal_cov(beta,k=1,w=1,D=1,cumculative_sum_equation=1):
    """
    The log of the second part of eq 9 (Rasmussen 2000)
    the covariance matrix of the model is diagonal cov
    """
    return -k*special.gammaln(beta/2) \
        - 0.5/beta \
        + 0.5*(beta*k-3)*np.log(beta/2) \
        + 0.5*beta*cumculative_sum_equation


def log_p_beta_prime_diagonal_cov(beta,k=1,w=1,D=1,cumculative_sum_equation=1):
    """
    The derivative (wrt beta) of the log of eq 9 (Rasmussen 2000)
    the covariance matrix of the model is diagonal cov
    """
    return -k*special.psi(0.5*beta) \
        + 0.5/beta**2 \
        + 0.5*k*np.log(0.5*beta) \
        + (k*beta -3)/beta \
        + 0.5*cumculative_sum_equation


# def draw_gamma_ras(a, theta, size=1):
#     """
#     returns Gamma distributed samples according to the Rasmussen (2000) definition
#     """
#     return gamma.rvs(0.5 * a, loc=0, scale=2.0 * theta / a, size=size)


def draw_gamma(a, theta, size=1):
    """
    returns Gamma distributed samples
    """
    return gamma.rvs(a, loc=0, scale=theta, size=size)


def draw_wishart(df, scale, size=1):
    """
    returns Wishart distributed samples
    """
    return wishart.rvs(df=df, scale=scale, size=size)


def draw_normal(loc=0, scale=1, size=1):
    '''
    returns Normal distributed samples
    '''
    return norm.rvs(loc=loc, scale=scale, size=size)


def draw_MVNormal(mean=0, cov=1, size=1):
    """
    returns multivariate normally distributed samples
    """
    return mv_norm.rvs(mean=mean, cov=cov, size=size)


def draw_alpha(k, N, size=1):
    """
    draw alpha from posterior (depends on k, N), eq 15 (Rasmussen 2000), using ARS
    Make it robust with an expanding range in case of failure
    """
    ars = ARS(log_p_alpha, log_p_alpha_prime, xi=[0.1, 5], lb=0, ub=np.inf, k=k, N=N)
    return ars.draw(size)


def draw_s_ljk(s_rjk, w, beta, N, cumculative_sum_equation, size=1):
    lb = 0
    ars = ARS(log_p_s_ljk, log_p_s_ljk_prime, xi=[lb+0.5], lb=0, ub=lb+10, s_rjk=s_rjk,
                  w=w, beta=beta, N=N, cumculative_sum_equation=cumculative_sum_equation)
    return ars.draw(size)

def draw_s_rjk(s_ljk, w, beta, N, cumculative_sum_equation, size=1):
    lb = 1
    ars = ARS(log_p_s_rjk, log_p_s_rjk_prime, xi=[lb+5], lb=0, ub=lb+10, s_ljk=s_ljk,
                  w=w, beta=beta, N=N, cumculative_sum_equation=cumculative_sum_equation)
    return ars.draw(size)



def draw_beta(beta, w, s_l, M, k, size=1):
    """
    draw beta from posterior (depends on k, s, w), eq 9 (Rasmussen 2000), using Metropolis Hastings
    """
    beta = Metropolis_Hastings_Sampling_beta(beta[k], w, s_l, M, k)
    return beta


def draw_indicator(pvec):
    """
    draw stochastic indicator values from multinominal distributions, check wiki
    """
    res = np.zeros(pvec.shape[1])
    # loop over each data point
    for j in range(pvec.shape[1]):
        c = np.cumsum(pvec[ : ,j])        # the cumulative un-scaled probabilities
        R = np.random.uniform(0, c[-1], 1)        # a random number
        r = (c - R)>0                     # truth table (less or greater than R)
        y = (i for i, v in enumerate(r) if v)    # find first instant of truth
        try:
            res[j] = y.__next__()           # record component index
        except:                 # if no solution (must have been all zeros)
            res[j] = np.random.randint(0, pvec.shape[0]) # pick uniformly
    return res