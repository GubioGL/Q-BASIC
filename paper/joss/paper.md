---
title: 'Q-BASIC: a transparent Python simulator of closed and open quantum systems, built step by step in an open course'
tags:
  - Python
  - quantum physics
  - quantum optics
  - quantum computing
  - open quantum systems
  - physics education
authors:
  - name: Gubio Gomes de Lima
    # TODO: add the ORCID (https://orcid.org) before submitting, e.g.
    # orcid: 0000-0000-0000-0000
    affiliation: 1
affiliations:
  # TODO: add the author's affiliation before submitting.
  - name: Affiliation to be defined
    index: 1
date: 9 November 2026
bibliography: paper.bib
---

<!--
Draft for the Journal of Open Source Software (JOSS). Every point marked TODO must be
filled in with real, verifiable information before submission; see paper/JOSS.md.
-->

# Summary

Quantum mechanics describes physical systems such as atoms, photons in an optical cavity
or the qubits of a quantum computer with vectors (states) and matrices (operators).
Simulating such a system on a classical computer therefore reduces to linear algebra:
building those vectors and matrices, combining them, and solving the differential
equations that describe how they change in time, either in isolation (the Schrödinger
equation) or in contact with an environment (the Lindblad master equation)
[@lindblad1976; @gorini1976].

Q-BASIC (*Quantum Brazilian Algorithms, SImulations, and Computational tools*) is an
open-source Python library that performs these simulations for small systems with a
deliberately transparent implementation on top of NumPy [@harris2020numpy] and SciPy
[@virtanen2020scipy]. It provides quantum states (Fock, coherent, multi-qubit, Bell, GHZ
and W states, density matrices), operators (bosonic ladder, number, position, momentum
and Pauli operators, tensor products), quantum logic gates acting on arbitrary qubits,
closed- and open-system dynamics, measurements and information-theoretic quantities
(partial trace, purity, entropy, fidelity) [@nielsen2010], and plots of Wigner functions
[@wigner1932; @cahill1969], Bloch spheres and photon-number distributions with
Matplotlib [@hunter2007matplotlib].

Q-BASIC is the end product of an open course: a sequence of Jupyter notebooks
[@kluyver2016jupyter], also compiled automatically into a book, in which the reader
builds the simulator from scratch and then uses the finished library to study quantum
optics and quantum computing. The library is thus both a tool for small-scale
simulations and a codebase small enough to be read in full.

# Statement of need

Small quantum systems are the everyday object of research in quantum optics and quantum
information: a two-level atom coupled to a cavity mode, a handful of qubits under a
sequence of gates, a damped oscillator. Such problems appear in student research
projects and theses, and whenever a researcher checks an analytical calculation
numerically. They do not need high-performance code, but code whose results can be
trusted and understood.

Q-BASIC addresses this need with a "glass box" design: every function is a short,
documented version of code derived in the course, so a user who obtains a surprising
result can read exactly what was computed. Its target audience is (i) students starting
research in quantum optics and quantum information, and their supervisors; (ii)
instructors who want students to build a simulator before using one; and (iii)
researchers who need a small, auditable reference implementation to cross-check larger
packages. The API, documentation and course are in Portuguese, lowering the language
barrier for the physics community of Brazil and other Portuguese-speaking countries.

# State of the field

QuTiP [@johansson2012qutip; @johansson2013qutip2] is the reference open-source package
for the dynamics of open quantum systems in Python, QuantumOptics.jl
[@kramer2018quantumoptics] offers similar functionality with high performance in Julia,
and Qiskit [@javadi2024qiskit] is a complete software stack for circuit-based quantum
computing on simulators and real hardware. These packages are more complete and faster
than Q-BASIC, which does not try to replace them: problems that outgrow it, such as large
Hilbert spaces, time-dependent Hamiltonians, quantum trajectories or circuits on real
devices, belong in those tools.

We built a new library instead of contributing to these projects because the main
contribution of Q-BASIC is the codebase itself as an object of study, which conflicts
with the design goals of established packages:

- **Readability over generality.** Mature packages rely on compiled extensions and
  dispatch layers over several data formats, which is right for general-purpose software
  but hides the linear algebra from a beginner. Q-BASIC stays at a size (about 2,400
  lines including docstrings) that a student can read in a semester.
- **A course that converges to the library.** Each module corresponds to lessons in
  which the reader writes the same code. A tutorial for an existing package can explain
  how to use it, but cannot let students write its core.
- **Language.** Portuguese names for functions and arguments (`ket`, `coerente`,
  `resolver_lindblad`) cannot reasonably be added upstream to an English-language
  package.

At the same time, Q-BASIC builds on the existing ecosystem instead of reinventing it. All
numerical kernels (sparse matrices, matrix exponentials, ODE integrators, special
functions) come from SciPy, the course compares results with QuTiP along the way, and
every object converts to NumPy and SciPy arrays, so moving to QuTiP when a problem
outgrows Q-BASIC is direct.

# Software design

The design follows from one requirement: the library must be code that a reader of the
course could have written, while being correct and fast enough for research-sized
problems.

**One class, two storage formats.** Every state and operator is an `ObjQuantico` that
holds a NumPy array or a SciPy sparse (CSR) matrix, plus the dimensions of each
subsystem and its type (ket, bra or operator). Earlier versions had separate dense and
sparse classes with duplicated code and inconsistent behavior. A single class makes the
formats interoperable, keeps one code path to read and lets almost every test run in
both formats, at the cost of some format dispatch inside each operation.

**Notation close to the blackboard.** `A * B` is the matrix product, `A @ B` the tensor
product $A \otimes B$, and `A + c` means $A + c\,\mathbb{1}$. Using `@` for the tensor
product departs from NumPy, where it means matrix multiplication; we accepted this
because tensor products are ubiquitous in composite systems and the course introduces
both operators explicitly. The class opts out of NumPy universal functions, so mixed
expressions raise clear errors instead of silently returning plain arrays.

**Exact propagation by default.** For time-independent Hamiltonians, the Schrödinger and
Lindblad equations are solved with the action of the matrix exponential on a vector
[@almohy2011expmv], which works directly with sparse matrices. For a Jaynes-Cummings
system [@jaynes1963] of dimension 80, the state agrees with exact diagonalization to
$2\times10^{-13}$, against $2\times10^{-7}$ for an adaptive eighth-order Runge-Kutta
method [@dormand1980rk] at default tolerances, which is also slower; Runge-Kutta
integrators remain available so that students can compare methods. The Lindblad equation
is solved through the vectorized Liouvillian, which is exposed to the user because its
spectrum gives the relaxation rates. The price is that a state of dimension $d$ becomes a
vector of length $d^2$, which limits open systems to dimensions of a few hundred.

**Gates by permutation.** A $k$-qubit gate acts on arbitrary, not necessarily adjacent,
qubits by conjugation with a sparse permutation of the computational basis, so one short
function covers CNOT, CZ, SWAP, Toffoli and any controlled single-qubit gate.

**Stable teaching material.** Names from version 0.0.x remain importable with
deprecation warnings that point to the new API, and continuous integration executes
every notebook of the course, so a change that breaks a lesson fails the build.

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

# Research impact statement

<!--
TODO (required by JOSS): the pre-review screening rejects submissions without evidence
that the software is used in research, at least by the author. "Aspirational statements
about future use are not sufficient." Replace the paragraph marked TODO below with
concrete, verifiable items: papers, preprints, theses or conference presentations that
used Q-BASIC (cite them in paper.bib); courses in which the material was taught
(institution, semester, number of students); other people or groups who use it.
-->

**TODO: realized impact.** *List here the research projects, publications, theses and
courses that used Q-BASIC, for example: "Q-BASIC was used to compute the dynamics
reported in (citation) and in the master's thesis of ..."; "the course was taught at
... in ... to ... students".*

Q-BASIC has been developed on GitHub since January 2024, and version 0.0.3 has been
available on the Python Package Index since December 2024. Version 0.1.0 adds the
following evidence of near-term significance, all verifiable in the repository:

- **Reproducible materials.** The 15 course notebooks, which cover topics such as
  collapse and revival in the Jaynes-Cummings model [@eberly1980] and quantum
  teleportation [@bennett1993], are executed by continuous integration and compiled into
  a PDF book for every release; the figure in this paper is regenerated from the library
  by a script in the repository.
- **Validation.** More than 800 automated tests (98% line coverage) check physical
  results rather than implementation details: Pauli algebra and canonical commutation
  relations, Poisson statistics of coherent states, Rabi and Jaynes-Cummings dynamics
  against analytical solutions and exact diagonalization, spontaneous emission and
  damped oscillators, gate truth tables, and Wigner functions against the
  displaced-parity definition. They run on Linux, Windows and macOS with Python 3.10 to
  3.14 and with the oldest supported dependencies.
- **Performance.** For a sparse Jaynes-Cummings evolution of dimension 400, version
  0.1.0 is 26 times faster than version 0.0.x with the same Runge-Kutta call, and 177
  times faster with the default exact propagator; the benchmark script is included.

# AI usage disclosure

<!--
TODO: JOSS requires the tools/models and versions, where they were used, the nature and
scope of the assistance, and a confirmation that the author reviewed and validated all
AI-assisted outputs. Fill in the model and version, and keep only statements that are
true at the time of submission.
-->

Version 0.0.x of Q-BASIC (2024–2025), including the original simulator, its operator
conventions and the course notebooks, was written by the author without generative AI.
Version 0.1.0 (November 2026) was developed with Claude Code, an AI coding assistant by
Anthropic (**TODO: model and version**), working under the author's direction in the
public repository, where the corresponding commits are marked as co-authored. The
assistant was used to reorganize the project as a package; to rewrite the core class,
fix bugs and add the exact propagator, the Lindblad solver, quantum gates and
visualization functions; to write most of the unit tests, the continuous-integration
workflows and the documentation website; to update the course notebooks to the new API;
to write the script that compiles the notebooks into a book; and to draft this paper.
The author defined the scope and the structure of the course, approved the design
decisions described above from a written plan, and reviewed, edited and validated all
AI-assisted outputs. Correctness was checked by the physics-based test suite, by
comparison with analytical results, exact diagonalization and QuTiP, and by executing
every notebook of the course.

# Acknowledgements

**TODO:** *acknowledge colleagues, students and institutions, and list any financial
support (agency and grant number), or state that no specific funding was received.*

# References
