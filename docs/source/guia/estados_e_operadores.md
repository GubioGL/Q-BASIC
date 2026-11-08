---
file_format: mystnb
kernelspec:
  name: python3
  display_name: Python 3
mystnb:
  execution_mode: force
---

# Estados e operadores

```{code-cell} python
import numpy as np

import qbasic as qb
```

## Estados

| Função | Estado |
|---|---|
| {func}`~qbasic.bases` `(N, n)` | vetor da base $\ket{n}$ num espaço de dimensão $N$ |
| {func}`~qbasic.fock` `(N, n=0)` | estado de Fock $\ket{n}$ (por padrão, o vácuo) |
| {func}`~qbasic.ket` / {func}`~qbasic.bra` | qubits: `ket("0")`, `ket("1")`, `ket("0110")` |
| {func}`~qbasic.coerente` `(N, alpha)` | estado coerente $\ket{\alpha}$ |
| {func}`~qbasic.bell`, {func}`~qbasic.ghz`, {func}`~qbasic.w` | estados emaranhados de qubits |
| {func}`~qbasic.matriz_densidade` | $\rho = \sum_k p_k \ket{\psi_k}\bra{\psi_k}$ |

O estado coerente tem distribuição de Poisson, com $\langle n\rangle = |\alpha|^2$:

```{code-cell} python
alpha = 1.5
psi = qb.coerente(30, alpha)
print(qb.probabilidades(psi)[:5].round(4))
print(qb.valor_esperado(psi, qb.numero(30)), abs(alpha) ** 2)
```

Ele pode ser calculado aplicando o operador deslocamento ao vácuo (`metodo="operador"`,
padrão) ou pela fórmula fechada (`metodo="analitico"`, estável mesmo com centenas de
níveis).

A matriz densidade de um estado puro é $\ket{\psi}\bra{\psi}$; para uma mistura, passe a lista
de estados e as probabilidades:

```{code-cell} python
rho = qb.matriz_densidade([qb.ket("0"), qb.ket("1")], [0.75, 0.25])
print(rho.full().real)
print("pureza:", qb.pureza(rho))
```

## Operadores

| Função | Operador |
|---|---|
| {func}`~qbasic.identidade` `(N)` | $I$ |
| {func}`~qbasic.destruicao` / {func}`~qbasic.criacao` `(N)` | $a$, $a^\dagger$, com $a\ket{n} = \sqrt{n}\ket{n-1}$ |
| {func}`~qbasic.numero` `(N)` | $\hat n = a^\dagger a$ |
| {func}`~qbasic.operador_x` / {func}`~qbasic.operador_p` | $x = (a + a^\dagger)/\sqrt2$, $p = -i(a - a^\dagger)/\sqrt2$ |
| {func}`~qbasic.pauliX`, {func}`~qbasic.pauliY`, {func}`~qbasic.pauliZ` | matrizes de Pauli |
| {func}`~qbasic.tensor` | produto tensorial de vários objetos |
| {func}`~qbasic.comutador` / {func}`~qbasic.anticomutador` | $[A, B]$ e $\{A, B\}$ |

Os operadores de Fock são **truncados** em $N$ níveis. Por isso $[a, a^\dagger] = I$ vale
em todos os níveis menos o último:

```{code-cell} python
print(qb.comutador(qb.destruicao(5), qb.criacao(5)).full().real.diagonal())
```

Use $N$ bem maior que os números de fótons relevantes (para um estado coerente, alguns
desvios-padrão acima de $|\alpha|^2$).

## Sistemas compostos

O produto tensorial combina subsistemas, e `dims` registra a dimensão de cada um. Um
operador que age só numa parte é o produto tensorial com identidades:

```{code-cell} python
N = 5
a = qb.tensor(qb.destruicao(N), qb.identidade(2))    # cavidade ⊗ átomo
sm = qb.tensor(qb.identidade(N), qb.destruicao(2))   # sigma-menos do átomo
H = a.dag() * a + sm.dag() * sm + 0.1 * (a.dag() * sm + a * sm.dag())
print(H.dims, H.shape)
```
