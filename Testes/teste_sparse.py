import sys
import scipy as sp
import numpy as np
import matplotlib.pyplot as plt

# Add the directory containing the Main module to the Python path
sys.path.append('C:/Users/Gubio/Desktop/Gubio/Simulador_quantico')
from Main.estados import bases
from Main.operador import destruiçao,Identidade

wc = 1.0 * 2 * np.pi  # cavity frequency
wa = 1.0 * 2 * np.pi  # atom frequency
g = 0.05 * 2 * np.pi  # coupling strength

basefock = 2

psi0 = bases(basefock, 0,sparsa=True)@ bases(2, 0,sparsa=True)
print(psi0.full())
print(psi0.full_sparsa())

print(sp.sparse.csr_array(psi0.full()))
# # cavity mode operator
# a = destruiçao(basefock,sparsa=True)@Identidade(2,sparsa=True)
# print(a.full())
# print(a.full_sparsa())
# # # qubit/atom operators
# sm = Identidade(basefock,sparsa=True)@(destruiçao(2,sparsa=True).dag())  # sigma-minus operator
# print(sm.full())
# print(sm.full_sparsa())
# # the Jaynes-Cumming Hamiltonian
# H_acomplamento = g * ( a*(sm.dag()) + a.dag()*sm )

# H = wc * a.dag() * a  + wa * sm.dag()*sm + H_acomplamento
# print(H.full())
# print(H.full_sparsa())
