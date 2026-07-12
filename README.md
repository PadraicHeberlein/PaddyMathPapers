# PaddyMathPapers

A collection of mathematical research papers by Padraic.

## Papers

### 1. Spectral Entropy of Modular Multiplication
**Directory:** [`spectral-entropy/`](spectral-entropy/)

An investigation into the connection between the Shannon entropy of modular multiplication tables, the algebraic structure of finite fields, and primality testing. Establishes that the entropy achieves its maximum if and only if *n* is prime, defines the Spectral Remainder Transform, and constructs a non-circular continuous entropy signal whose peaks locate the primes.

### 2. Spectral Methods in Data Compression and Geometric Encoding
**Directory:** [`spectral-compression/`](spectral-compression/)

Three interconnected explorations at the intersection of information theory, signal processing, and differential geometry:

- **Block Entropy and FFT-Based Compression** — Finding the "fundamental frequency" of a binary string by treating block-coded symbol windows as a spectral problem, and using the FFT to efficiently determine the optimal block size and phase alignment that minimizes per-bit entropy.

- **Information Conservation Under Domain Transforms** — A rigorous analysis of why encoding binary data onto sinusoids or polynomials and applying Fourier series compression fails: the conservation of degrees of freedom, the Gibbs phenomenon, and the floating-point inflation penalty.

- **Generalized Surfaces of Revolution via Quaternionic Frames** — Rotating a target curve around a curved axis using the Frenet–Serret frame parameterized by unit quaternions in ℍ, connecting to SU(2) sandwich operators from quantum mechanics, and the dimensional reduction of 3D surfaces via spiral space-filling paths.

## Building

Each paper directory contains its own LaTeX source. To build:

```bash
cd <paper-directory>/
pdflatex main.tex
# or use latexmk:
latexmk -pdf main.tex
```

## Repository Structure

```
PaddyMathPapers/
├── README.md
├── .gitignore
├── spectral-entropy/          # Paper 1: Modular multiplication & primes
│   ├── main.tex
│   ├── scripts/               # Supporting Python scripts
│   └── figures/               # Generated plots and diagrams
└── spectral-compression/      # Paper 2: Compression & geometry
    ├── main.tex
    ├── scripts/               # Supporting Python scripts
    └── figures/               # Generated plots and diagrams
```

## License

Research use. Contact the author for other uses.
