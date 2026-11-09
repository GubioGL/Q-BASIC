---
title: 'Q-BASIC: a didactic quantum simulator in Python for quantum optics and quantum computing education'
tags:
  - Python
  - quantum physics
  - quantum optics
  - quantum computing
  - open quantum systems
  - physics education
authors:
  - name: Gubio Gomes de Lima
    affiliation: 1
affiliations:
  # TODO: add the author's affiliation before submitting.
  - name: Affiliation to be defined
    index: 1
date: 9 November 2026
bibliography: paper.bib
---

# Summary

Q-BASIC (*Quantum Brazilian Algorithms, SImulations, and Computational tools*) is an
open-source Python library for simulating small quantum systems in the classroom. It
represents kets, bras, operators and density matrices as dense or sparse matrices built on
NumPy [@harris2020numpy] and SciPy [@virtanen2020scipy], and provides:

- **states**: Fock, coherent, multi-qubit computational-basis states, Bell, GHZ and W states,
  and density matrices;
- **operators**: bosonic creation/annihilation, number, position and momentum operators,
  Pauli matrices, tensor products and commutators;
- **quantum logic gates**: Hadamard, phase, rotations, CNOT, CZ, SWAP, Toffoli and controlled
  versions of any single-qubit gate, applied to arbitrary (also non-adjacent) qubits;
- **dynamics**: the Schrödinger equation and the Lindblad master equation
  [@lindblad1976; @gorini1976];
- **measurements**: expectation values, measurement sampling, partial trace, purity,
  von Neumann entropy and fidelity [@nielsen2010];
- **visualization**: Wigner functions [@wigner1932; @cahill1969], Bloch spheres and Fock
  distributions with Matplotlib [@hunter2007matplotlib].

The library is accompanied by a sequence of Jupyter notebooks [@kluyver2016jupyter] that
build the simulator from scratch and then use it to study quantum optics and quantum
computing. The same notebooks are rendered in the documentation website and compiled
automatically into a PDF book.

# Statement of need

Mature tools such as QuTiP [@johansson2012qutip; @johansson2013qutip2],
QuantumOptics.jl [@kramer2018quantumoptics] and Qiskit [@javadi2024qiskit] are the
standard choices for research in quantum optics, open quantum systems and quantum
computing. Their size and layers of abstraction, however, make it hard for beginners to
see what a simulation actually does, and their interfaces and documentation are in
English only.

Q-BASIC follows a "glass box" approach aimed at undergraduate and early graduate courses,
in particular in Portuguese-speaking countries. Its public API is in Portuguese, and every
function is a short, readable version of code that students write themselves in the
tutorials: a ket is a column vector, `A * B` is the matrix product, `A @ B` is the tensor
product, and the Schrödinger equation is solved with a single call. A complete Rabi
oscillation example reads:

```python
import numpy as np
import qbasic as qb

times = np.linspace(0, 4 * np.pi, 100)
H = 0.5 * qb.pauliX()  # H = (Omega/2) sigma_x
result = qb.resolver_schrodinger(H, qb.ket("0"), times, observaveis=[qb.pauliZ()])
result.valores_esperados[0]  # equals cos(Omega t)
```

Despite its didactic focus, the library is efficient enough for classroom and
undergraduate research problems. Dense and sparse formats can be mixed freely. Time
evolution uses the action of the matrix exponential [@almohy2011expmv] by default. This
is exact to machine precision and works directly with sparse matrices; adaptive
Runge-Kutta integrators [@dormand1980rk] are also available. The Lindblad equation is
solved through the vectorized Liouvillian superoperator, which is also exposed to users,
since its spectrum gives the relaxation rates. Wigner functions are computed from the Fock
expansion in generalized Laguerre polynomials.

# Example: decoherence of a Schrödinger cat

\autoref{fig:cat} shows the Wigner function of the cat state
$|\alpha\rangle + |-\alpha\rangle$ ($\alpha = 2$) in a lossy cavity, computed with the
master equation. The interference fringes vanish long before the photons leave the
cavity [@haroche2006]:

```python
a = qb.destruicao(30)
cat = (qb.coerente(30, 2.0) + qb.coerente(30, -2.0)).normalizar()
res = qb.resolver_lindblad(0 * qb.numero(30), cat, [0, 0.1, 0.4], [a])  # kappa = 1
W = [qb.wigner(rho, x, x) for rho in res.estados]
```

![Wigner function of a Schrödinger-cat state under photon loss at three instants: the
negative interference fringes disappear while the two coherent components survive.
\label{fig:cat}](figura_qbasic.png)

Other worked examples include collapse and revival in the Jaynes-Cummings model
[@jaynes1963; @eberly1980], atom-cavity entanglement, Bell-state preparation and quantum
teleportation [@bennett1993].

# Quality assurance

The test suite has more than 800 tests. They check physical results instead of
implementation details:

- Pauli algebra and canonical commutation relations;
- Poisson statistics of coherent states;
- Rabi and Jaynes-Cummings dynamics against analytical solutions and exact
  diagonalization;
- spontaneous emission and damped oscillators;
- gate truth tables;
- Wigner functions against the displaced-parity definition.

Almost every test runs in both the dense and the sparse format. Continuous integration
runs the following on Linux, Windows and macOS with Python 3.10 to 3.14:

- the test suite and the docstring examples;
- all tutorial notebooks;
- a build with the oldest supported dependencies.

Deprecated names from earlier versions keep working with warnings that point to the new
API.

# Acknowledgements

<!-- TODO: add acknowledgements and funding, if any. -->

# References
