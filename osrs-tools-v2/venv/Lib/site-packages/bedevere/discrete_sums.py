from bedevere import *


def convolution(x: dict, y: dict) -> dict:
    """Return a distribution representing the sum of two distributions"""
    z = {}

    for j in range(sum([min(x), min(y)]), sum([max(x), max(y)]) + 1):
        rolling_sum = 0

        for k in x.keys():
            if j - k in y:
                rolling_sum += x[k] * y[j - k]

        if not rolling_sum == 0:
            z[j] = rolling_sum

    return z


def convolution_list(x: List[dict]) -> dict:
    """Return a distribution representing the sum of all distributions in a list"""
    assert len(x) > 1

    z = convolution(x[0], x[1])

    for i, d in enumerate(x):
        if i < 2:
            continue

        z = convolution(z, d)

    return z


def n_convolution(x: dict, n: int) -> dict:
    """Return a distribution representing the sum of n distributions x"""
    assert n > 0

    if n > 2:
        return convolution(x, n_convolution(x, n-1))

    elif n == 2:
        return convolution(x, x)

    elif n == 1:
        return x

    else:
        raise RuntimeError


def discrete_uniform_sum_term(n: int, y: int, k: int) -> float:
    """Returns a very specific term as descrbied by Caiado & Rathie

    Link: http://community.dur.ac.uk/c.c.d.s.caiado/multinomial.pdf"""

    itersum = 0

    for p in range(0, math.floor(y/(k+1)) + 1):
        a = n + y - p*(k+1)

        if a >= 1:
            numerator = math.factorial(a - 1) * (-1)**p

        else:
            numerator = math.gamma(a) * (-1)**p

        b = n - p + 1
        c = y - p*(k+1) + 1

        if b >= 1:
            d1 = math.factorial(b - 1)

        else:
            d1 = math.gamma(b)

        if c >= 1:
            d2 = math.factorial(c - 1)

        else:
            d2 = math.gamma(c)

        denominator = math.factorial(p+1) * d1 * d2

        itersum += numerator / denominator

    return itersum

    # condensed function that causes memory overload
    # return sum(map(lambda p: math.gamma(n + y - p*(k+1))*(-1)**p /
    #                          (math.gamma(p+1)*math.gamma(n - p + 1)*math.gamma(y - p*(k+1) + 1)),
    #                range(0, math.floor(y/(k+1))+1)))


def n_convolution_discrete_uniform(k: int, n: int) -> dict:
    """Returns a distribution representing the sum of n discrete uniform variables from 0 to k

    given a discrete uniform variable X with values (0, 1, 2, ... k), return the distribution of the sum of n instances
    with values (0, 1, 2, ... nk)"""

    assert n > 0
    d = {}

    for y in range(n*k + 1):
        d[y] = n * (k + 1)**(-n) * discrete_uniform_sum_term(n, y, k)

    return d


def n_convolution_discrete_uniform_non_standard_range(value_range: Tuple[int, int], n: int):
    """Returns a distribution representing the sum of n discrete uniform variables over a specified range

    given a discrete uniform variable X with values (j, j+1, j+2, ... j+k), return the distribution of the sum of n
    instances with values (nj, nj + 1, nj + 2, ... n(j+k)"""

    assert n > 0
    assert all(type(i) == int for i in value_range)

    low_value, high_value = (min(value_range), max(value_range))
    k = high_value - low_value
    d = n_convolution_discrete_uniform(k, n)
    dprime = {}

    for key, val in d.items():
        dprime[key + n*low_value] = val

    return dprime
