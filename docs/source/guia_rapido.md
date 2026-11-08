---
file_format: mystnb
kernelspec:
  name: python3
  display_name: Python 3
mystnb:
  execution_mode: force
---

# Guia rápido

Um passeio pelos recursos principais. Todo o código desta página é executado quando a
documentação é gerada, então as saídas são exatamente o que a biblioteca produz.

```{code-cell} python
import matplotlib.pyplot as plt
import numpy as np

import qbasic as qb
```

## Estados e operadores

Estados e operadores são objetos {class}`~qbasic.objeto.ObjQuantico`. O produto matricial
é `*` e o produto tensorial é `@` (ou {func}`~qbasic.tensor`).

```{code-cell} python
psi = qb.ket("0")              # |0>
X = qb.pauliX()                # porta NOT
print(X * psi)                 # X|0> = |1>
```

No Jupyter, os objetos aparecem como matrizes em LaTeX:

```{code-cell} python
qb.destruicao(4)               # operador de destruição com 4 níveis
```

```{code-cell} python
a = qb.destruicao(10)
print(qb.valor_esperado(qb.coerente(10, 1.5), a.dag() * a))   # <n> = |alpha|^2 = 2.25
```

## Dinâmica: oscilação de Rabi

{func}`~qbasic.resolver_schrodinger` resolve $i\,d|\psi\rangle/dt = H|\psi\rangle$
($\hbar = 1$). Para $H = (\Omega/2)\,\sigma_x$, a população oscila como
$\langle\sigma_z\rangle = \cos(\Omega t)$.

```{code-cell} python
tempos = np.linspace(0, 10, 200)
resultado = qb.resolver_schrodinger(0.5 * qb.pauliX(), qb.ket("0"), tempos, [qb.pauliZ()])

plt.plot(tempos, resultado.valores_esperados[0])
plt.xlabel("t")
plt.ylabel(r"$\langle\sigma_z\rangle$");
```

## Sistemas abertos: decaimento

{func}`~qbasic.resolver_lindblad` resolve a equação mestra. Um átomo excitado que emite
com taxa $\gamma$ tem população $e^{-\gamma t}$:

```{code-cell} python
sm = qb.destruicao(2)                      # sigma-menos: |1> -> |0>
gamma = 0.5
res = qb.resolver_lindblad(0 * qb.numero(2), qb.ket("1"), tempos, [np.sqrt(gamma) * sm], [sm.dag() * sm])

plt.plot(tempos, res.valores_esperados[0], label="Q-BASIC")
plt.plot(tempos, np.exp(-gamma * tempos), "--", label=r"$e^{-\gamma t}$")
plt.xlabel("t")
plt.legend();
```

## Circuitos e medidas

```{code-cell} python
circuito = qb.cnot() * qb.tensor(qb.hadamard(), qb.identidade(2))
bell = circuito * qb.ket("00")
print(qb.amostrar(bell, 1000, semente=1))
print("entropia de um qubit:", qb.entropia_von_neumann(qb.traco_parcial(bell, 0)), "bit")
```

## Função de Wigner

```{code-cell} python
gato = (qb.coerente(30, 2.0) + qb.coerente(30, -2.0)).normalizar()
qb.plotar_wigner(gato)
plt.title("Gato de Schrödinger");
```

## Próximos passos

- {doc}`guia/index`: os conceitos e as convenções em detalhe.
- {doc}`tutoriais/index`: aulas completas em notebooks.
- {doc}`api/index`: a referência de cada função.
