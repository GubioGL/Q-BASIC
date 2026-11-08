"""
Colapso e renascimento das oscilações de Rabi (Jaynes-Cummings com matrizes esparsas).

O átomo começa excitado e a cavidade num estado coerente com |alpha|^2 = 10 fótons em
média. As oscilações de Rabi de cada número de fótons se desfazem (colapso) e voltam a
entrar em fase depois de t ≈ 2π|alpha|/g (renascimento).

Com 40 níveis de Fock o espaço tem dimensão 80; em formato esparso (``sparsa=True``)
os operadores guardam só os elementos não nulos, e o solver padrão (``"expm"``)
trabalha direto com as matrizes esparsas.

Execução:  python exemplos/jaynes_cummings_esparso.py   (requer matplotlib)
"""

import matplotlib.pyplot as plt
import numpy as np

import qbasic as qb

N = 40  # níveis de Fock da cavidade
g = 1.0  # acoplamento (no referencial girante, em ressonância)
alpha = np.sqrt(10)

a = qb.tensor(qb.destruicao(N, sparsa=True), qb.identidade(2, sparsa=True))
sm = qb.tensor(qb.identidade(N, sparsa=True), qb.destruicao(2, sparsa=True))
H = g * (a.dag() * sm + a * sm.dag())
print(H)  # mostra o formato e o número de elementos não nulos

psi0 = qb.tensor(qb.coerente(N, alpha, sparsa=True), qb.ket("1", sparsa=True))
tempos = np.linspace(0, 50, 1000)
resultado = qb.resolver_schrodinger(H, psi0, tempos, observaveis=[sm.dag() * sm])
populacao = resultado.valores_esperados[0]

plt.plot(tempos, populacao)
plt.axvline(2 * np.pi * alpha / g, color="gray", linestyle="--", label="renascimento previsto")
plt.xlabel("tempo (g t)")
plt.ylabel("população do estado excitado")
plt.title("Jaynes-Cummings: colapso e renascimento")
plt.legend()
plt.show()
