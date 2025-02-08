#from operador import destruiçao,Identidade
import qbasic as qb
import scipy  as sp

g = 0.05 * 2   # coupling strength

basefock = 2

a = qb.operador.destruiçao(basefock,sparsa=True)@qb.operador.Identidade(2,sparsa=True)

sm = qb.operador.Identidade(basefock,sparsa=True)@(qb.operador.destruiçao(2,sparsa=True).dag())  # sigma-minus operator

H_acomplamento = g * ( a*sm.dag() + a.dag()*sm )
print(H_acomplamento.full())