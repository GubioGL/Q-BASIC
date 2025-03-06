#from operador import destruiçao,Identidade
import numpy as np
import qbasic as qb
import scipy  as sp

wc = 1.0 * 2 * np.pi  # cavity frequency
wa = 1.0 * 2 * np.pi  # atom frequency
g  = 0.05 * 2 * np.pi  # coupling strength

basefock = 2

psi0 = qb.estados.bases(basefock, 0)@qb.estados.bases(2, 0)

# cavity mode operator
a = qb.operador.destruiçao(basefock,sparsa=True)@qb.operador.Identidade(2,sparsa=True)
print("Operador de criaçao", a.full())
# qubit/atom operators
sm = qb.operador.Identidade(basefock,sparsa=True)@(qb.operador.destruiçao(2,sparsa=True).dag())  # sigma-minus operator
print("Operador de levantamento ",sm.full())

H_acomplamento = g * ( a*sm.dag() + a.dag()*sm )


H = wc * a.dag() * a  + wa * sm.dag()*sm + H_acomplamento
print(H.full())