"""
Modelo de Jaynes-Cummings com o Q-BASIC.

Um átomo de dois níveis acoplado a um modo de cavidade. O script monta o
Hamiltoniano, resolve a equação de Schrödinger e plota o número médio de fótons
e a população do estado excitado ao longo do tempo (oscilações de Rabi no vácuo).

Execução:  python exemplos/jaynes_cummings.py   (requer matplotlib)
"""

import matplotlib.pyplot as plt
import numpy as np

import qbasic as qb

wc = 1.0 * 2 * np.pi  # frequência da cavidade
wa = 1.0 * 2 * np.pi  # frequência do átomo
g = 0.05 * 2 * np.pi  # acoplamento átomo-cavidade
N = 2  # níveis de Fock da cavidade

# Operadores no espaço cavidade ⊗ átomo
a = qb.tensor(qb.destruicao(N), qb.identidade(2))
sm = qb.tensor(qb.identidade(N), qb.destruicao(2))  # sigma-menos: |1> (excitado) -> |0>

# Hamiltoniano de Jaynes-Cummings (aproximação de onda girante)
H = wc * a.dag() * a + wa * sm.dag() * sm + g * (a.dag() * sm + a * sm.dag())

psi0 = qb.tensor(qb.fock(N, 0), qb.ket("1"))  # cavidade vazia, átomo excitado
tempos = np.linspace(0, 20, 200)

resultado = qb.resolver_schrodinger(H, psi0, tempos, observaveis=[a.dag() * a, sm.dag() * sm])
n_fotons, populacao = resultado.valores_esperados

plt.plot(tempos, n_fotons, label="número de fótons")
plt.plot(tempos, populacao, label="população do estado excitado")
plt.xlabel("tempo")
plt.ylabel("valor esperado")
plt.title("Jaynes-Cummings: oscilação de Rabi no vácuo")
plt.legend()
plt.show()
