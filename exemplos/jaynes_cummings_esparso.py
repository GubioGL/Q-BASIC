"""
Hamiltoniano de Jaynes-Cummings montado com matrizes esparsas no Q-BASIC.

Mesmo sistema de ``jaynes_cummings.py`` (átomo de dois níveis + cavidade), mas com
os operadores em formato esparso (``sparsa=True``), mais econômico para espaços de
Hilbert grandes. O script imprime os operadores e o Hamiltoniano.

Execução:  python exemplos/jaynes_cummings_esparso.py
"""

import numpy as np

import qbasic as qb

wc = 1.0 * 2 * np.pi  # cavity frequency
wa = 1.0 * 2 * np.pi  # atom frequency
g = 0.05 * 2 * np.pi  # coupling strength

basefock = 2

psi0 = qb.estados.bases(basefock, 0) @ qb.estados.bases(2, 0)

# cavity mode operator
a = qb.operador.destruiçao(basefock, sparsa=True) @ qb.operador.Identidade(2, sparsa=True)
print("Operador de destruição a:\n", a.full())
# qubit/atom operators
sm = qb.operador.Identidade(basefock, sparsa=True) @ (
    qb.operador.destruiçao(2, sparsa=True).dag()
)  # sigma-minus operator
print("Operador sigma-menos:\n", sm.full())

H_acomplamento = g * (a * sm.dag() + a.dag() * sm)

H = wc * a.dag() * a + wa * sm.dag() * sm + H_acomplamento
print("Hamiltoniano H:\n", H.full())
