import numpy as np
import matplotlib.pyplot as plt
import qbasic as qb


wc = 1.0 * 2 * np.pi  # cavity frequency
wa = 1.0 * 2 * np.pi  # atom frequency
g = 0.05 * 2 * np.pi  # coupling strength

basefock = 2

psi0 = qb.estados.bases(basefock, 0)@qb.estados.bases(2, 0)

# cavity mode operator
a = qb.operador.destruiçao(basefock)@qb.operador.Identidade(2)
print(a.full())
# qubit/atom operators
sm = qb.operador.Identidade(basefock)@(qb.operador.destruiçao(2).dag())  # sigma-minus operator
print(sm.full())
# the Jaynes-Cumming Hamiltonian
H_acomplamento = g * ( a*(sm.dag()) + a.dag()*sm )

H = wc * a.dag() * a  + wa * sm.dag()*sm + H_acomplamento
print(H.full())
tempo = np.linspace(0, 10, 100)  # Pontos de avaliação

# Resolvendo a equação de Schrödinger e calculando o valor esperado
resultado = qb.funçoes.edo.solve(H, tempo, psi0)

# Definindo as observáveis
O1 = a.dag() * a  # Número de fótons no campo
O2 = sm.dag() * sm  # Sigma_z para o átomo
print(resultado.y.shape)
valores_esperados = qb.funçoes.Valor_esperado(resultado.y,[O1,O2])
plt.plot(valores_esperados[0])
plt.plot(valores_esperados[1])
plt.show()