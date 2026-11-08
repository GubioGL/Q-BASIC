---
file_format: mystnb
kernelspec:
  name: python3
  display_name: Python 3
mystnb:
  execution_mode: force
---

# Dinâmica

```{code-cell} python
import matplotlib.pyplot as plt
import numpy as np

import qbasic as qb
```

Unidades com $\hbar = 1$. Os dois resolvedores devolvem um {class}`~qbasic.dinamica.Resultado`
com os `tempos`, os estados (`estados`, ou a matriz `vetores`) e os `valores_esperados` dos
observáveis pedidos.

## Equação de Schrödinger

{func}`~qbasic.resolver_schrodinger` resolve

$$ i\frac{d}{dt}\ket{\psi(t)} = H\ket{\psi(t)} $$

para Hamiltonianos independentes do tempo. Exemplo: modelo de Jaynes-Cummings em
ressonância, com o átomo excitado e a cavidade vazia. A excitação vai e volta entre os dois
(oscilação de Rabi no vácuo), com $P_\text{excitado}(t) = \cos^2(gt)$:

```{code-cell} python
N, g = 3, 0.5
a = qb.tensor(qb.destruicao(N), qb.identidade(2))
sm = qb.tensor(qb.identidade(N), qb.destruicao(2))
H = a.dag() * a + sm.dag() * sm + g * (a.dag() * sm + a * sm.dag())

psi0 = qb.tensor(qb.fock(N, 0), qb.ket("1"))
tempos = np.linspace(0, 15, 300)
res = qb.resolver_schrodinger(H, psi0, tempos, observaveis=[a.dag() * a, sm.dag() * sm])

qb.plotar_valores_esperados(res, ["fótons na cavidade", "átomo excitado"]);
```

### Métodos

| `metodo` | Como funciona | Quando usar |
|---|---|---|
| `"expm"` (padrão) | evolução exata, $e^{-iHt}\ket{\psi_0}$, com `scipy.sparse.linalg.expm_multiply` | quase sempre: erro na precisão de máquina, funciona com matrizes esparsas |
| `"DOP853"`, `"RK45"`, ... | integradores do `scipy.integrate.solve_ivp` (`rtol=1e-8`, `atol=1e-10`) | quando o estado vive num subespaço pequeno de um espaço grande |

```{code-cell} python
exato = qb.resolver_schrodinger(H, psi0, tempos, [sm.dag() * sm])
rk = qb.resolver_schrodinger(H, psi0, tempos, [sm.dag() * sm], metodo="DOP853")
print("diferença máxima:", np.abs(exato.valores_esperados[0] - rk.valores_esperados[0]).max())
```

## Equação mestra de Lindblad

Para sistemas abertos, {func}`~qbasic.resolver_lindblad` evolui a matriz densidade:

$$ \frac{d\rho}{dt} = -i[H, \rho] + \sum_k \left(L_k \rho L_k^\dagger
   - \tfrac{1}{2}\{L_k^\dagger L_k, \rho\}\right) $$

Os operadores de colapso $L_k$ já incluem as taxas: perda de fótons com taxa $\kappa$ é
`np.sqrt(kappa) * a`; emissão espontânea com taxa $\gamma$ é `np.sqrt(gamma) * sm`.
O estado inicial pode ser um ket ou uma matriz densidade.

Com perdas, as oscilações de Rabi do exemplo anterior são amortecidas:

```{code-cell} python
kappa, gamma = 0.1, 0.05
res = qb.resolver_lindblad(
    H, psi0, tempos,
    operadores_colapso=[np.sqrt(kappa) * a, np.sqrt(gamma) * sm],
    observaveis=[a.dag() * a, sm.dag() * sm],
)
qb.plotar_valores_esperados(res, ["fótons na cavidade", "átomo excitado"]);
```

```{code-cell} python
rho_final = res.estados[-1]
print("traço:", round(rho_final.traco(), 10), " pureza:", round(qb.pureza(rho_final), 4))
```

### O Liouvilliano

Internamente, $\rho$ é vetorizado (coluna por coluna) e a equação vira
$d\,\mathrm{vec}(\rho)/dt = \mathcal{L}\,\mathrm{vec}(\rho)$. O superoperador
$\mathcal{L}$ (esparso, $N^2 \times N^2$) é dado por {func}`~qbasic.liouvilliano`. Seus
autovalores dão as taxas de relaxação; para um qubit que decai com taxa $\gamma$, eles são
$0$, $-\gamma/2$ (duas vezes) e $-\gamma$:

```{code-cell} python
L = qb.liouvilliano(0 * qb.numero(2), [np.sqrt(0.8) * qb.destruicao(2)])
np.sort(np.linalg.eigvals(L.full()).real)
```
