"""
Modelo de Jaynes-Cummings com o Q-BASIC (matrizes densas).

Um átomo de dois níveis acoplado a um modo de cavidade. O script monta o
Hamiltoniano, resolve a equação de Schrödinger e plota o número médio de fótons
e a população atômica ao longo do tempo (oscilações de Rabi no vácuo).

Execução:  python exemplos/jaynes_cummings.py   (requer matplotlib)
"""

import matplotlib.pyplot as plt
import numpy as np

import qbasic as qb

wc = 1.0 * 2 * np.pi  # cavity frequency
wa = 1.0 * 2 * np.pi  # atom frequency
g = 0.05 * 2 * np.pi  # coupling strength

basefock = 2

psi0 = qb.estados.bases(basefock, 0) @ qb.estados.bases(2, 0)

# cavity mode operator
a = qb.operador.destruiçao(basefock) @ qb.operador.Identidade(2)
print(a.full())
# qubit/atom operators
sm = qb.operador.Identidade(basefock) @ (qb.operador.destruiçao(2).dag())  # sigma-minus operator
print(sm.full())
# the Jaynes-Cumming Hamiltonian
H_acomplamento = g * (a * (sm.dag()) + a.dag() * sm)

H = wc * a.dag() * a + wa * sm.dag() * sm + H_acomplamento
print(H.full())
tempo = np.linspace(0, 10, 100)  # Pontos de avaliação

# Resolvendo a equação de Schrödinger e calculando o valor esperado
resultado = qb.funçoes.edo.solve(H, tempo, psi0)

# Definindo as observáveis
O1 = a.dag() * a  # Número de fótons no campo
O2 = sm.dag() * sm  # Sigma_z para o átomo
print(resultado.y.shape)
valores_esperados = qb.funçoes.Valor_esperado(resultado.y, [O1, O2])
plt.plot(tempo, valores_esperados[0], label="número de fótons")
plt.plot(tempo, valores_esperados[1], label="população atômica")
plt.xlabel("tempo")
plt.ylabel("valor esperado")
plt.legend()
plt.show()
