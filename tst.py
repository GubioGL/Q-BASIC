from qbasic import bases


basefock = 2

psi0 = bases(basefock, 0,sparsa=True)@ bases(2, 0,sparsa=True)
print(psi0.full())
print(psi0.full_sparsa())
