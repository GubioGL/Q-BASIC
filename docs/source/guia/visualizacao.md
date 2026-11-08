---
file_format: mystnb
kernelspec:
  name: python3
  display_name: Python 3
mystnb:
  execution_mode: force
---

# Visualização

Os gráficos usam o matplotlib (`pip install "Q-BASIC[plot]"`). Todas as funções aceitam um
argumento `ax` para desenhar em eixos já existentes e devolvem os eixos usados.

```{code-cell} python
import matplotlib.pyplot as plt
import numpy as np

import qbasic as qb
```

## Função de Wigner

{func}`~qbasic.wigner` calcula $W(x, p)$ de um modo bosônico (normalizada,
$\int W\,dx\,dp = 1$) e {func}`~qbasic.plotar_wigner` desenha o mapa (vermelho positivo, azul
negativo). Valores negativos são uma assinatura de estados não clássicos:

```{code-cell} python
fig, eixos = plt.subplots(1, 3, figsize=(13, 4))
for eixo, (nome, estado) in zip(eixos, [
    ("vácuo", qb.fock(20, 0)),
    ("Fock |2⟩", qb.fock(20, 2)),
    ("coerente α = 1.5 + i", qb.coerente(20, 1.5 + 1j)),
]):
    qb.plotar_wigner(estado, ax=eixo)
    eixo.set_title(nome)
plt.tight_layout()
```

```{code-cell} python
x = np.linspace(-4, 4, 161)
W = qb.wigner(qb.fock(10, 1), x, x)
print("W(0, 0) =", W[80, 80], " (= -1/π)")
```

## Distribuição de Fock

```{code-cell} python
qb.plotar_fock(qb.coerente(25, 3.0))
plt.title("Estado coerente: distribuição de Poisson com ⟨n⟩ = 9");
```

## Esfera de Bloch

{func}`~qbasic.esfera_bloch` desenha um ou mais estados de um qubit (kets ou matrizes
densidade) ou vetores de Bloch já calculados. Com `trajetoria=True`, os pontos são ligados
— útil para mostrar uma evolução no tempo. Abaixo, um qubit precessando em torno de
$z + x$ enquanto perde coerência:

```{code-cell} python
H = 0.5 * (qb.pauliZ() + qb.pauliX())
tempos = np.linspace(0, 20, 300)
res = qb.resolver_lindblad(H, qb.ket("0"), tempos, [np.sqrt(0.05) * qb.pauliZ()])
vetores = [qb.vetor_bloch(rho) for rho in res.estados]
qb.esfera_bloch(vetores, trajetoria=True);
```

## Valores esperados ao longo do tempo

```{code-cell} python
res = qb.resolver_schrodinger(H, qb.ket("0"), tempos, [qb.pauliX(), qb.pauliY(), qb.pauliZ()])
qb.plotar_valores_esperados(res, ["⟨X⟩", "⟨Y⟩", "⟨Z⟩"]);
```
