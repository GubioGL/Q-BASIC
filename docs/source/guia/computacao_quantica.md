---
file_format: mystnb
kernelspec:
  name: python3
  display_name: Python 3
mystnb:
  execution_mode: force
---

# Computação quântica

```{code-cell} python
import numpy as np

import qbasic as qb
```

## Convenção de ordem dos qubits

O qubit 0 é o da **esquerda** (o mais significativo): `ket("01")` é
$\ket{0}\otimes\ket{1}$, o vetor da base de índice 1. As portas recebem os índices nessa
mesma convenção.

## Portas

| Portas de um qubit | Portas de vários qubits |
|---|---|
| {func}`~qbasic.pauliX`, {func}`~qbasic.pauliY`, {func}`~qbasic.pauliZ` | {func}`~qbasic.cnot` `(controle, alvo, n_qubits)` |
| {func}`~qbasic.hadamard` | {func}`~qbasic.cz`, {func}`~qbasic.swap` |
| {func}`~qbasic.porta_s`, {func}`~qbasic.porta_t`, {func}`~qbasic.fase` `(φ)` | {func}`~qbasic.toffoli` |
| {func}`~qbasic.rx`, {func}`~qbasic.ry`, {func}`~qbasic.rz` `(θ)` | {func}`~qbasic.porta_controlada` (qualquer porta de 1 qubit) |

Para aplicar uma porta a qubits específicos de um registro maior, use
{func}`~qbasic.porta_em` (os qubits não precisam ser vizinhos):

```{code-cell} python
X_no_meio = qb.porta_em(qb.pauliX(), 1, n_qubits=3)
print(qb.amostrar(X_no_meio * qb.ket("000"), 10))
```

```{code-cell} python
qb.cnot()
```

## Montando um circuito

Um circuito é o produto das portas, **da direita para a esquerda** (a primeira porta
aplicada fica mais à direita). O circuito de Bell:

```{code-cell} python
circuito = qb.cnot(0, 1) * qb.tensor(qb.hadamard(), qb.identidade(2))
bell = circuito * qb.ket("00")
print(qb.probabilidades(bell))
print(qb.fidelidade(bell, qb.bell("phi+")))
```

Um estado GHZ de 4 qubits, com uma Hadamard e uma cascata de CNOTs:

```{code-cell} python
n = 4
estado = qb.porta_em(qb.hadamard(), 0, n) * qb.ket("0" * n)
for q in range(n - 1):
    estado = qb.cnot(q, q + 1, n_qubits=n) * estado
print(qb.amostrar(estado, 1000, semente=3))
```

## Identidades úteis

```{code-cell} python
H, S, T = qb.hadamard(), qb.porta_s(), qb.porta_t()
print((H * qb.pauliX() * H - qb.pauliZ()).norma())          # HXH = Z
print((T * T - S).norma())                                   # T² = S
print((qb.rx(np.pi) + 1j * qb.pauliX()).norma())             # Rx(π) = -iX
print((qb.swap() - qb.cnot(0, 1) * qb.cnot(1, 0) * qb.cnot(0, 1)).norma())  # SWAP = 3 CNOTs
```

O tutorial {doc}`../tutoriais/computacao_quantica/02_portas_e_emaranhamento` vai além:
esfera de Bloch, correlações e teleportação quântica.
