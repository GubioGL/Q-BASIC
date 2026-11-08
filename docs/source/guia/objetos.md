---
file_format: mystnb
kernelspec:
  name: python3
  display_name: Python 3
mystnb:
  execution_mode: force
---

# Objetos quânticos

```{code-cell} python
import numpy as np

import qbasic as qb
```

Tudo no Q-BASIC — kets, bras, operadores e matrizes densidade — é um
{class}`~qbasic.objeto.ObjQuantico`. Ele guarda a matriz e algumas informações sobre ela:

```{code-cell} python
psi = qb.ket("01")
print(psi.tipo, psi.shape, psi.dims, psi.formato)
```

| Atributo | Significado |
|---|---|
| `tipo` | `"ket"` (coluna), `"bra"` (linha), `"operador"` (quadrado) ou `"escalar"` (1×1) |
| `shape` | forma da matriz, `(linhas, colunas)` |
| `dims` | dimensões dos subsistemas, por exemplo `[[2, 2], [1, 1]]` para dois qubits |
| `formato` | `"denso"` (NumPy) ou `"esparso"` (SciPy CSR) |
| `dados` | a matriz em si (`numpy.ndarray` ou `scipy.sparse.csr_array`) |

Também é possível criar um objeto a partir de qualquer matriz:

```{code-cell} python
H = qb.ObjQuantico([[1, 0.5], [0.5, -1]])
H.autovalores()
```

## Convenções das operações

| Expressão | Significado |
|---|---|
| `A * B` | produto matricial (operador × operador, operador × ket, bra × ket...) |
| `A @ B` ou `qb.tensor(A, B)` | produto tensorial $A \otimes B$ |
| `c * A`, `A / c` | multiplicação e divisão por um número (real ou complexo) |
| `A + c` | $A + c\,I$ (soma com um múltiplo da identidade) |
| `A ** n` | potência inteira |
| `A.dag()` | adjunto $A^\dagger$ |

```{code-cell} python
X, Y, Z = qb.pauliX(), qb.pauliY(), qb.pauliZ()
print((X * Y - 1j * Z).norma())       # XY = iZ
print((X @ Z).dims)                   # produto tensorial: [[2, 2], [2, 2]]
print(qb.bra("0") * qb.ket("0"))      # produto interno <0|0> = 1
```

## Denso ou esparso?

Todas as funções que criam objetos aceitam `sparsa=True`. Matrizes esparsas guardam só os
elementos não nulos, o que economiza memória e tempo em espaços de Hilbert grandes
(por exemplo, muitos níveis de Fock ou muitos subsistemas):

```{code-cell} python
a = qb.destruicao(2000, sparsa=True)
print(a.formato, a.shape, "elementos guardados:", a.dados.nnz)
```

Os dois formatos se misturam: o resultado é esparso só quando os dois operandos são.

```{code-cell} python
misto = qb.pauliX() * qb.pauliZ(sparsa=True)
print(misto.formato)
print(qb.pauliX(sparsa=True).para_denso().formato)
```

Regra prática: use denso para dimensões até algumas centenas e esparso acima disso.

## Exibição e interoperabilidade

No Jupyter, o objeto é exibido em LaTeX (matrizes grandes são resumidas com reticências);
`print` mostra um resumo em texto. Com `numpy.asarray` (ou `.full()`) obtém-se a matriz
densa, e a indexação acessa os elementos:

```{code-cell} python
a = qb.destruicao(3)
print(np.asarray(a))
print(a[0, 1], a.traco(), a.eh_hermitiano())
```
