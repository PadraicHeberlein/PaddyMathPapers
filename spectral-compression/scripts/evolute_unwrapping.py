#!/usr/bin/env python3
"""
Evolute Unwrapping and Offset Curve Smoothing
=============================================

Demonstrates the inverse problem of the spiral transform:
1. For a closed 2D curve, computes its evolute (locus of centers of curvature).
2. Generates parallel offset curves to demonstrate the smoothing convergence
   behavior (offset curves smooth out and approach a perfect circle as offset d -> infinity).

Saves a publication-quality figure to figures/evolute_smoothing.png.
"""

import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
import numpy as np
import matplotlib.pyplot as plt
import os

def generate_target_curve(n_samples=500):
    """Generates a wavy closed 2D curve (a perturbed ellipse)."""
    t = np.linspace(0, 2 * np.pi, n_samples, endpoint=False)
    # Radius profile: base ellipse with high-frequency sinusoidal perturbation
    r = 2.0 + 0.3 * np.cos(3 * t) + 0.1 * np.sin(5 * t)
    
    # 2D coordinates
    x = r * np.cos(t)
    y = r * np.sin(t)
    
    return t, x, y

def compute_curve_geometry(t, x, y):
    """Computes tangent, normal, curvature, and evolute of a 2D curve."""
    # Derivates via finite differences
    dt = t[1] - t[0]
    
    dx = np.gradient(x, dt)
    dy = np.gradient(y, dt)
    
    ddx = np.gradient(dx, dt)
    ddy = np.gradient(dy, dt)
    
    # Speed
    ds = np.sqrt(dx**2 + dy**2)
    
    # Unit tangent vectors
    tx = dx / ds
    ty = dy / ds
    
    # Unit normal vectors (inward-pointing if parameterized counter-clockwise)
    nx = -ty
    ny = tx
    
    # Curvature: kappa = (x'*y'' - y'*x'') / (x'^2 + y'^2)^(3/2)
    curvature = (dx * ddy - dy * ddx) / (ds**3)
    
    # Radius of curvature: rho = 1 / curvature
    rho = 1.0 / curvature
    
    # Evolute: locus of centers of curvature
    ev_x = x + rho * nx
    ev_y = y + rho * ny
    
    return tx, ty, nx, ny, curvature, rho, ev_x, ev_y

if __name__ == "__main__":
    print("Generating 2D target curve...")
    t, x, y = generate_target_curve()
    
    print("Computing curve normals, curvature, and evolute...")
    tx, ty, nx, ny, kappa, rho, ev_x, ev_y = compute_curve_geometry(t, x, y)
    
    # Generate offset curves
    # beta_d(t) = beta(t) + d * N(t)
    offsets = [0.5, 1.5, 3.0, 5.0]
    offset_curves = []
    for d in offsets:
        ox = x + d * nx
        oy = y + d * ny
        offset_curves.append((ox, oy))
        
    print("Plotting evolute and offset curve smoothing...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9), dpi=150)
    
    # Panel 1: Curve and its Evolute
    ax1.plot(x, y, 'b-', linewidth=2.5, label='Target Curve β(t)')
    # Filter out singular peaks in the evolute to make plot readable
    # (evolute of a wavy curve can go to infinity at inflection points where kappa -> 0)
    valid_ev = (np.abs(rho) < 10.0)
    ax1.scatter(ev_x[valid_ev], ev_y[valid_ev], color='red', s=4, label='Evolute α(t) (Centers of Curvature)')
    
    # Draw some normal lines connecting curve to evolute
    draw_indices = np.linspace(0, len(t)-1, 16, dtype=int)
    for idx in draw_indices:
        ax1.plot([x[idx], ev_x[idx]], [y[idx], ev_y[idx]], 'k--', alpha=0.3)
        
    ax1.set_aspect('equal')
    ax1.grid(True, linestyle=':', alpha=0.5)
    ax1.set_title("Curve and its Local Evolute (Centers of Curvature)", fontsize=14, fontweight='bold')
    ax1.legend(loc='upper right')
    
    # Panel 2: Offset Curves Smoothing (Convergence to Circle)
    ax2.plot(x, y, 'b-', linewidth=2, label='Original Curve')
    colors = ['#ff6b6b', '#4ecdc4', '#ff9800', '#ab47bc']
    for idx, (ox, oy) in enumerate(offset_curves):
        ax2.plot(ox, oy, color=colors[idx], linewidth=1.5, 
                 label=f"Offset d = {offsets[idx]} (Inward)")
        
    ax2.set_aspect('equal')
    ax2.grid(True, linestyle=':', alpha=0.5)
    ax2.set_title("Offset Curves Smoothing (Asymptotic Convergence to Circle)", fontsize=14, fontweight='bold')
    ax2.legend(loc='upper right')
    
    os.makedirs("figures", exist_ok=True)
    outfile = "figures/evolute_smoothing.png"
    plt.savefig(outfile, bbox_inches='tight')
    print(f"Plot saved to {outfile}")
