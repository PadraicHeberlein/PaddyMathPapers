#!/usr/bin/env python3
import numpy as np
import sys

def pMatrix(n):
    p = np.zeros((n-1,n-1));
    for i in range(1,n):
        for j in range(1,n):
            p[i-1][j-1] = (i*j)%n
    return p

def main():
    if len(sys.argv) != 3:
        print("Usage: python pmatrix.py <from> <to>")
        sys.exit(1)
    
    m = int(sys.argv[1])
    n = int(sys.argv[2])

    if m >= n:
        print("Usage: <from> strictly less than <to>")
        sys.exit(1)

    for i in range(m,n):
        p = pMatrix(i)
        det = round(np.linalg.det(p))
        egn_vals,egn_vecs = np.linalg.eig(p) 
        
        egn_vals[np.abs(egn_vals) < 1e-9] = 0.0
        egn_vecs[np.abs(egn_vecs) < 1e-9] = 0.0

        print(f'{i} : {egn_vals} : \n{egn_vecs}')

if __name__ == "__main__": main()

