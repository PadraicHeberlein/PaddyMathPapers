#!/usr/bin/env python3
"""
Quaternionic Frenet Frame Integration and SU(2) Path Visualization
==================================================================

Solves the quaternionic differential equation governing the Frenet-Serret frame:
    dq/ds = 1/2 * q(s) * omega(s)
where omega(s) = tau * i + kappa * k is the local Darboux vector (angular velocity).

1. Integrates the ODE along a helical space curve using RK4.
2. Extracts the (T, N, B) frame vectors via SU(2) rotation conjugation (q * v * q^-1).
3. Verifies alignment with numerically computed Frenet vectors.
4. Visualizes the 4D quaternion trajectory q(s) on S^3 projected to 3D.

Saves the diagnostic plot to figures/quaternion_trajectory.png.
"""

import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
import numpy as np
import matplotlib.pyplot as plt
import os

# Quaternion algebra helpers
def quat_mult(p, q):
    """Multiplies two quaternions p and q represented as arrays [w, x, y, z]."""
    pw, px, py, pz = p
    qw, qx, qy, qz = q
    w = pw*qw - px*qx - py*qy - pz*qz
    x = pw*qx + px*qw + py*qz - pz*qy
    y = pw*qy - px*qz + py*qw + pz*qx
    z = pw*qz + px*qy - py*qx + pz*qw
    return np.array([w, x, y, z])

def quat_conjugate(q):
    """Returns the conjugate of a quaternion q = [w, x, y, z]."""
    return np.array([q[0], -q[1], -q[2], -q[3]])

def quat_rotate(q, v):
    """Rotates a 3D vector v by unit quaternion q via q * [0, v] * q^-1."""
    v_quat = np.array([0, v[0], v[1], v[2]])
    rotated = quat_mult(quat_mult(q, v_quat), quat_conjugate(q))
    return rotated[1:] # Return vector part

# Helical space curve definition
def helix_curve(s):
    """Standard helix: x = cos(4*pi*s), y = sin(4*pi*s), z = 2*s."""
    x = np.cos(4 * np.pi * s)
    y = np.sin(4 * np.pi * s)
    z = 2.0 * s
    return np.array([x, y, z])

def compute_analytical_helix_curvature_torsion(r=1.0, pitch=2.0):
    """
    For a helix r*cos(t), r*sin(t), c*t, where pitch = 2*pi*c:
    curvature = r / (r^2 + c^2)
    torsion = c / (r^2 + c^2)
    """
    c = pitch / (2 * np.pi)
    denom = r**2 + c**2
    kappa = r / denom
    tau = c / denom
    return kappa, tau

def compute_curve_derivatives_and_geometry(gamma_func, s_vals):
    """
    Computes velocity, acceleration, jerk, speed, curvature, and torsion
    numerically for any 3D curve gamma_func(s).
    """
    h = 1e-4
    N = len(s_vals)
    
    # Evaluate curve at central, forward, and backward points
    g = gamma_func(s_vals)
    g_p1 = gamma_func(s_vals + h)
    g_m1 = gamma_func(s_vals - h)
    g_p2 = gamma_func(s_vals + 2*h)
    g_m2 = gamma_func(s_vals - 2*h)
    
    # 5-point stencil finite differences for derivatives
    # Velocity (first derivative)
    v = (-g_p2 + 8*g_p1 - 8*g_m1 + g_m2) / (12 * h)
    # Acceleration (second derivative)
    a = (-g_p2 + 16*g_p1 - 30*g + 16*g_m1 - g_m2) / (12 * h**2)
    # Jerk (third derivative)
    j = (g_p2 - 2*g_p1 + 2*g_m1 - g_m2) / (2 * h**3)
    
    # Speed ds/dt
    speed = np.linalg.norm(v, axis=0)
    
    # Curvature: kappa = ||v x a|| / ||v||^3
    v_cross_a = np.cross(v.T, a.T).T
    norm_v_cross_a = np.linalg.norm(v_cross_a, axis=0)
    kappa = norm_v_cross_a / (speed**3)
    
    # Torsion: tau = (v x a) . j / ||v x a||^2
    tau = np.sum(v_cross_a * j, axis=0) / (norm_v_cross_a**2)
    
    return v, a, speed, kappa, tau

if __name__ == "__main__":
    print("Computing helix geometry numerically...")
    N_STEPS = 1000
    s_vals = np.linspace(0.01, 0.99, N_STEPS) # Avoid edge issues with finite differences
    ds = s_vals[1] - s_vals[0]
    helix = helix_curve(s_vals)
    
    v, a, speed, kappa, tau = compute_curve_derivatives_and_geometry(helix_curve, s_vals)
    print(f"  Helix Speed: {np.mean(speed):.4f}")
    print(f"  Helix Curvature kappa: {np.mean(kappa):.4f}")
    print(f"  Helix Torsion tau: {np.mean(tau):.4f}")
    
    # 1. Integrate the Quaternionic ODE: dq/ds = 1/2 * q * [0, tau * speed, 0, kappa * speed]
    # Initialize quaternion q(0)
    q = np.zeros((N_STEPS, 4))
    
    # Find the initial Frenet frame to set q[0]
    # T[0] = v / speed
    # B[0] = (v x a) / ||v x a||
    # N[0] = B[0] x T[0]
    T0 = v[:, 0] / speed[0]
    vxa0 = np.cross(v[:, 0], a[:, 0])
    B0 = vxa0 / np.linalg.norm(vxa0)
    N0 = np.cross(B0, T0)
    
    # Construct initial rotation matrix R0 = [T0, N0, B0]
    # Convert R0 to initial quaternion q[0]
    R0 = np.column_stack((T0, N0, B0))
    
    # Standard rotation matrix to quaternion conversion
    tr = np.trace(R0)
    if tr > 0:
        S_q = np.sqrt(tr + 1.0) * 2
        qw = 0.25 * S_q
        qx = (R0[2, 1] - R0[1, 2]) / S_q
        qy = (R0[0, 2] - R0[2, 0]) / S_q
        qz = (R0[1, 0] - R0[0, 1]) / S_q
    else:
        # Diagonal elements
        if (R0[0, 0] > R0[1, 1]) and (R0[0, 0] > R0[2, 2]):
            S_q = np.sqrt(1.0 + R0[0, 0] - R0[1, 1] - R0[2, 2]) * 2
            qw = (R0[2, 1] - R0[1, 2]) / S_q
            qx = 0.25 * S_q
            qy = (R0[0, 1] + R0[1, 0]) / S_q
            qz = (R0[0, 2] + R0[2, 0]) / S_q
        elif R0[1, 1] > R0[2, 2]:
            S_q = np.sqrt(1.0 + R0[1, 1] - R0[0, 0] - R0[2, 2]) * 2
            qw = (R0[0, 2] - R0[2, 0]) / S_q
            qx = (R0[0, 1] + R0[1, 0]) / S_q
            qy = 0.25 * S_q
            qz = (R0[1, 2] + R0[2, 1]) / S_q
        else:
            S_q = np.sqrt(1.0 + R0[2, 2] - R0[0, 0] - R0[1, 1]) * 2
            qw = (R0[1, 0] - R0[0, 1]) / S_q
            qx = (R0[0, 2] + R0[2, 0]) / S_q
            qy = (R0[1, 2] + R0[2, 1]) / S_q
            qz = 0.25 * S_q
            
    q[0] = np.array([qw, qx, qy, qz])
    q[0] /= np.linalg.norm(q[0])
    
    # Runge-Kutta 4th Order Integrator
    for i in range(N_STEPS - 1):
        q_curr = q[i]
        
        # Local Darboux vector scaled by local speed
        # omega_local = tau * T_local + kappa * B_local
        # In our coordinate alignment: T_local = i = [1,0,0], B_local = k = [0,0,1]
        sp = speed[i]
        kp = kappa[i]
        tp = tau[i]
        omega_i = np.array([0.0, tp * sp, 0.0, kp * sp])
        
        k1 = 0.5 * quat_mult(q_curr, omega_i)
        
        # Midpoint speeds and curvatures
        sp_mid = 0.5 * (speed[i] + speed[i+1])
        kp_mid = 0.5 * (kappa[i] + kappa[i+1])
        tp_mid = 0.5 * (tau[i] + tau[i+1])
        omega_mid = np.array([0.0, tp_mid * sp_mid, 0.0, kp_mid * sp_mid])
        
        k2 = 0.5 * quat_mult(q_curr + 0.5 * ds * k1, omega_mid)
        k3 = 0.5 * quat_mult(q_curr + 0.5 * ds * k2, omega_mid)
        
        omega_next = np.array([0.0, tau[i+1] * speed[i+1], 0.0, kappa[i+1] * speed[i+1]])
        k4 = 0.5 * quat_mult(q_curr + ds * k3, omega_next)
        
        q_next = q_curr + (ds / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        q[i+1] = q_next / np.linalg.norm(q_next)
        
    print("Extracting T, N, B frames from quaternion rotations...")
    T_quat = np.zeros((N_STEPS, 3))
    N_quat = np.zeros((N_STEPS, 3))
    B_quat = np.zeros((N_STEPS, 3))
    
    for i in range(N_STEPS):
        T_quat[i] = quat_rotate(q[i], [1, 0, 0])
        N_quat[i] = quat_rotate(q[i], [0, 1, 0])
        B_quat[i] = quat_rotate(q[i], [0, 0, 1])
        
    # 2. Compute the exact Frenet frame numerically for verification
    print("Verifying against numerical Frenet-Serret frame...")
    T_num = np.zeros((N_STEPS, 3))
    N_num = np.zeros((N_STEPS, 3))
    B_num = np.zeros((N_STEPS, 3))
    
    for i in range(N_STEPS):
        T_num[i] = v[:, i] / speed[i]
        vxa = np.cross(v[:, i], a[:, i])
        B_num[i] = vxa / np.linalg.norm(vxa)
        N_num[i] = np.cross(B_num[i], T_num[i])
        
    # Calculate error between quaternionic extraction and numerical calculation
    error_T = np.mean(np.linalg.norm(T_quat - T_num, axis=1))
    error_N = np.mean(np.linalg.norm(N_quat - N_num, axis=1))
    error_B = np.mean(np.linalg.norm(B_quat - B_num, axis=1))
    
    print(f"  Frame Reconstruction Mean Error:")
    print(f"    Tangent vector T error:   {error_T:.6e}")
    print(f"    Normal vector N error:    {error_N:.6e}")
    print(f"    Binormal vector B error:  {error_B:.6e}")
    
    # 3. Visualize the 4D quaternion trajectory projected to 3D
    # Stereographic projection from the north pole (1, 0, 0, 0) of S^3 to R^3:
    # proj_i = q_i / (1 - q_0) for i = 1, 2, 3
    print("Projecting S^3 quaternion trajectory to 3D...")
    proj_x = q[:, 1] / (1.001 - q[:, 0]) # Add small delta to avoid division by zero
    proj_y = q[:, 2] / (1.001 - q[:, 0])
    proj_z = q[:, 3] / (1.001 - q[:, 0])
    
    fig = plt.figure(figsize=(20, 10), dpi=150)
    
    # Left Panel: 3D Helix Curve with Frenet Frames
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.plot3D(helix[0], helix[1], helix[2], 'b-', linewidth=3, label='Helical Curve')
    
    # Draw some frames
    draw_indices = np.linspace(0, N_STEPS-1, 10, dtype=int)
    for idx in draw_indices:
        origin = helix[:, idx]
        # Vectors from quaternion rotation
        t_vec = T_quat[idx] * 0.4
        n_vec = N_quat[idx] * 0.4
        b_vec = B_quat[idx] * 0.4
        ax1.quiver(origin[0], origin[1], origin[2], t_vec[0], t_vec[1], t_vec[2], color='red', length=1.0, normalize=True)
        ax1.quiver(origin[0], origin[1], origin[2], n_vec[0], n_vec[1], n_vec[2], color='green', length=1.0, normalize=True)
        ax1.quiver(origin[0], origin[1], origin[2], b_vec[0], b_vec[1], b_vec[2], color='blue', length=1.0, normalize=True)
        
    ax1.set_title("Helical Curve & Integrator-Derived Frenet Frames", fontsize=14, fontweight='bold')
    ax1.set_xlabel("X")
    ax1.set_ylabel("Y")
    ax1.set_zlabel("Z")
    
    # Right Panel: Quaternion Trajectory on S^3 (stereographically projected)
    ax2 = fig.add_subplot(122, projection='3d')
    ax2.plot3D(proj_x, proj_y, proj_z, 'm-', linewidth=2.5, label='SU(2) Quaternion Path')
    ax2.scatter(proj_x[0], proj_y[0], proj_z[0], color='green', s=100, label='Start q(0)')
    ax2.scatter(proj_x[-1], proj_y[-1], proj_z[-1], color='red', s=100, label='End q(1)')
    
    ax2.set_title("Quaternion Trajectory Projected from $S^3$ to $\mathbb{R}^3$", fontsize=14, fontweight='bold')
    ax2.set_xlabel("q_x' (projected)")
    ax2.set_ylabel("q_y' (projected)")
    ax2.set_zlabel("q_z' (projected)")
    ax2.legend()
    
    os.makedirs("figures", exist_ok=True)
    outfile = "figures/quaternion_trajectory.png"
    plt.savefig(outfile, bbox_inches='tight')
    print(f"Plot saved to {outfile}")
