---
file_format: mystnb
kernelspec:
  name: python3
  display_name: Python 3
mystnb:
  execution_mode: force
---

# Medidas e emaranhamento

```{code-cell} python
import numpy as np

import qbasic as qb
```

## Valores esperados

{func}`~qbasic.valor_esperado` aceita kets, bras, matrizes densidade, listas de kets,
matrizes `(N, T)` com um estado por coluna e objetos `Resultado`. O resultado é real
quando o observável é hermitiano:

```{code-cell} python
mais = (qb.ket("0") + qb.ket("1")) / np.sqrt(2)
print(qb.valor_esperado(mais, qb.pauliX()))
print(qb.valor_esperado(qb.coerente(20, 1 + 1j), qb.destruicao(20)))   # <a> = alpha (complexo)
print(qb.valores_esperados([qb.ket("0"), qb.ket("1")], [qb.pauliZ()]))
```

## Probabilidades e amostragem

{func}`~qbasic.probabilidades` dá $|\braket{k}{\psi}|^2$ na base computacional, e
{func}`~qbasic.amostrar` simula medidas repetidas (use `semente` para reproduzir):

```{code-cell} python
psi = qb.ry(2 * np.pi / 3) * qb.ket("0")
print(qb.probabilidades(psi).round(3))
print(qb.amostrar(psi, 1000, semente=0))
```

## Traço parcial

{func}`~qbasic.traco_parcial` devolve o estado reduzido dos subsistemas indicados (os
índices seguem `dims`, da esquerda para a direita):

```{code-cell} python
ghz = qb.ghz(3)
rho_01 = qb.traco_parcial(ghz, [0, 1])
print(rho_01.dims)
print(rho_01.full().real)
```

## Pureza, entropia e fidelidade

- {func}`~qbasic.pureza`: $\mathrm{Tr}\,\rho^2$ (1 para estados puros);
- {func}`~qbasic.entropia_von_neumann`: $S = -\mathrm{Tr}\,\rho\log_2\rho$ (em bits);
- {func}`~qbasic.fidelidade`: $F = \left(\mathrm{Tr}\sqrt{\sqrt\rho\,\sigma\sqrt\rho}\right)^2$,
  que para estados puros é $|\braket{\psi}{\phi}|^2$.

A entropia do estado reduzido mede o emaranhamento de um estado puro bipartido:

```{code-cell} python
for nome, estado in [("produto", qb.ket("00")), ("Bell", qb.bell()), ("W", qb.w(3))]:
    reduzido = qb.traco_parcial(estado, 0)
    print(f"{nome:8s} S = {qb.entropia_von_neumann(reduzido):.3f} bit   pureza = {qb.pureza(reduzido):.3f}")
```

```{code-cell} python
print(qb.fidelidade(qb.bell("phi+"), qb.bell("psi+")))
print(qb.fidelidade(qb.ket("0"), qb.matriz_densidade([qb.ket("0"), qb.ket("1")], [0.9, 0.1])))
```

## Vetor de Bloch

Para um qubit, {func}`~qbasic.vetor_bloch` devolve
$(\langle X\rangle, \langle Y\rangle, \langle Z\rangle)$; o comprimento é 1 para estados
puros e menor para estados mistos:

```{code-cell} python
print(qb.vetor_bloch(mais))
print(qb.vetor_bloch(qb.traco_parcial(qb.bell(), 0)))
```
