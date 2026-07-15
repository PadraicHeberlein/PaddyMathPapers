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
from scipy.integrate import quad

def pi_p(p):
    if p == 1:
        return 4.0
    # The true value of pi in Lp space (ratio of Lp-circumference to diameter)
    val, _ = quad(lambda u: (u**(1-p) + (1-u)**(1-p))**(1/p), 0, 1)
    return 2 * val

p_range = np.linspace(1, 11, 500)
pi_vals = [pi_p(p) for p in p_range]

plt.figure(figsize=(8, 4))
plt.plot(p_range, pi_vals, color='#1f449c', linewidth=1.5)
plt.axhline(np.pi, color='gray', linewidth=1, alpha=0.7)
plt.text(11, np.pi + 0.02, '3.14159', ha='right', va='bottom')

# Find and mark minimum
min_idx = np.argmin(pi_vals)
plt.plot(p_range[min_idx], pi_vals[min_idx], marker='*', color='#a0403a', markersize=12)

plt.xlabel('p (Exponent for Lp Distance)')
plt.ylabel('pi(p)')
plt.title('The Value of pi for the Lp Metric', fontweight='bold')
plt.grid(True, color='gray', linestyle='-', linewidth=0.2, alpha=0.5)
plt.xlim(0.8, 11.2)
plt.ylim(2.95, 4.05)
plt.savefig(os.path.join(figures_dir, 'pi_p.png'), dpi=300, bbox_inches='tight')
plt.close()
