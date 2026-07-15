import numpy as np
from scipy.integrate import quad

def f(x, p):
    if x == 1: return np.inf
    return (1 + (x**(p*(p-1))) / ((1 - x**p)**(p-1)))**(1/p)

def pi_p(p):
    val, _ = quad(lambda x: f(x, p), 0, 1)
    return 2 * val

for p in [4.0, 10.0]:
    print(f"p={p} -> {pi_p(p)}")
