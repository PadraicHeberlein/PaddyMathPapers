#!/usr/bin/env python3
"""
Block Entropy Sweep Analysis for Binary Strings
===============================================

Sweeps over block sizes and shifts to analyze how representation structure
affects the empirical Shannon entropy. Demonstrates that periodic sequences
exhibit strong entropy minima when the block size matches the period, whereas
random sequences remain flat.

Saves the diagnostic plot to figures/block_entropy_sweep.png.
"""

import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
import numpy as np
import matplotlib.pyplot as plt
import collections
import os

def compute_block_entropy(bitstring, block_size, shift=0):
    """
    Partitions the bitstring (shifted by 'shift') into blocks of size 'block_size'
    and computes the Shannon entropy of the block distribution.
    """
    sliced = bitstring[shift:]
    # Group into blocks
    n_blocks = len(sliced) // block_size
    if n_blocks == 0:
        return 0.0
        
    blocks = [sliced[i*block_size : (i+1)*block_size] for i in range(n_blocks)]
    counts = collections.Counter(blocks)
    
    entropy = 0.0
    for block, count in counts.items():
        p = count / n_blocks
        entropy -= p * np.log2(p)
        
    # Return per-bit entropy
    return entropy / block_size

if __name__ == "__main__":
    # Test cases
    strings = {
        "Period-2 Sequence (01...)": "01" * 150,
        "Period-3 Sequence (001...)": "001" * 100,
        "Mixed Period Sequence": ("000111" * 25) + ("01" * 75),
        "Random Sequence": "".join(np.random.choice(['0', '1'], size=300).astype(str))
    }
    
    max_block_size = 10
    results = {}
    
    for label, bitstring in strings.items():
        entropy_sweep = []
        for n in range(1, max_block_size + 1):
            # Try all shifts and take the minimum entropy
            min_h = min(compute_block_entropy(bitstring, n, s) for s in range(n))
            entropy_sweep.append(min_h)
        results[label] = entropy_sweep
        
    print("Plotting block entropy sweeps...")
    fig, ax = plt.subplots(figsize=(12, 7), dpi=150)
    
    colors = ['#4caf50', '#2196f3', '#ff9800', '#f44336']
    markers = ['o', 's', '^', 'D']
    
    for idx, (label, sweep) in enumerate(results.items()):
        ax.plot(np.arange(1, max_block_size + 1), sweep, marker=markers[idx], 
                color=colors[idx], label=label, linewidth=2, markersize=8)
        
    ax.set_xlabel("Block Size n (bits)", fontsize=12)
    ax.set_ylabel("Per-Bit Shannon Entropy h_n", fontsize=12)
    ax.set_title("Per-Bit Entropy Sweep vs Block Size", fontsize=14, fontweight='bold')
    ax.set_xticks(np.arange(1, max_block_size + 1))
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.set_ylim(-0.05, 1.05)
    ax.legend(fontsize=11)
    
    os.makedirs("figures", exist_ok=True)
    outfile = "figures/block_entropy_sweep.png"
    plt.savefig(outfile, bbox_inches='tight')
    print(f"Plot saved to {outfile}")
