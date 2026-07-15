import numpy as np
import matplotlib.pyplot as plt
from scipy.special import gamma
import os

figures_dir = os.path.join(os.path.dirname(__file__), '..', 'figures')
os.makedirs(figures_dir, exist_ok=True)

# 1. Lp Circles
theta = np.linspace(0, 2*np.pi, 1000)
p_values = [1, 2, 4, 10]
labels = [r'$L_1$ (Diamond)', r'$L_2$ (Circle)', r'$L_4$ (Squircle)', r'$L_\infty$ (Square)']

plt.figure(figsize=(6, 6))
for p, label in zip(p_values, labels):
    if p == 10: # approximation for infinity
        x = np.cos(theta) / np.maximum(np.abs(np.cos(theta)), np.abs(np.sin(theta)))
        y = np.sin(theta) / np.maximum(np.abs(np.cos(theta)), np.abs(np.sin(theta)))
    else:
        lp = (np.abs(np.cos(theta))**p + np.abs(np.sin(theta))**p)**(1/p)
        x = np.cos(theta) / lp
        y = np.sin(theta) / lp
    plt.plot(x, y, label=label, linewidth=2)

plt.axhline(0, color='black',linewidth=1, alpha=0.3)
plt.axvline(0, color='black',linewidth=1, alpha=0.3)
plt.grid(color = 'gray', linestyle = '--', linewidth = 0.5, alpha=0.5)
plt.axis('equal')
plt.legend()
plt.title('Unit Circles in Various $L_p$ Metrics')
plt.savefig(os.path.join(figures_dir, 'lp_circles.png'), dpi=300, bbox_inches='tight')
plt.close()

# 2. Pi_p Graph
def pi_p(p):
    return (2 * (gamma(1/p)**2)) / (p * gamma(2/p))

p_range = np.linspace(1, 10, 500)
pi_vals = [pi_p(p) for p in p_range]

plt.figure(figsize=(6, 4))
plt.plot(p_range, pi_vals, 'b-', linewidth=2)
plt.axhline(np.pi, color='r', linestyle='--', label=r'$\pi \approx 3.14159$')
plt.axhline(4.0, color='g', linestyle='--', label=r'$4.0$ ($L_1$ and $L_\infty$)')
plt.xlabel('$p$')
plt.ylabel(r'$\pi_p$')
plt.title(r'The Value of $\pi$ in $L_p$ Space')
plt.legend()
plt.grid(True, alpha=0.5)
plt.savefig(os.path.join(figures_dir, 'pi_p.png'), dpi=300, bbox_inches='tight')
plt.close()
