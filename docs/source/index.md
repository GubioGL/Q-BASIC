# Q-BASIC

```{image} _static/Bra.png
:alt: Q-BASIC — Brazilian package for quantum computing
:class: banner-qbasic
```

**Q-BASIC** (*Quantum Brazilian Algorithms, SImulations, and Computational tools*) é um
simulador quântico em Python, feito no Brasil, para **ensino e pesquisa**. Ele cria estados
e operadores, resolve a dinâmica de sistemas fechados e abertos, simula circuitos de
qubits e desenha funções de Wigner e a esfera de Bloch — tudo com NumPy e SciPy, em
matrizes densas ou esparsas.

```python
import qbasic as qb

bell = qb.cnot() * qb.tensor(qb.hadamard(), qb.identidade(2)) * qb.ket("00")
qb.amostrar(bell, 1000)  # por exemplo, {'00': 503, '11': 497}
```

::::{grid} 1 2 3 3
:gutter: 3

:::{grid-item-card} 📦 Instalação
:link: instalacao
:link-type: doc

`pip install Q-BASIC` e os extras para gráficos e tutoriais.
:::

:::{grid-item-card} 🚀 Guia rápido
:link: guia_rapido
:link-type: doc

Estados, operadores, dinâmica, circuitos e gráficos em poucos minutos.
:::

:::{grid-item-card} 📖 Guia do usuário
:link: guia/index
:link-type: doc

Os conceitos e as convenções da biblioteca, com exemplos.
:::

:::{grid-item-card} 🎓 Tutoriais
:link: tutoriais/index
:link-type: doc

Aulas em notebooks: construindo o simulador do zero e computação quântica.
:::

:::{grid-item-card} 🔎 Referência da API
:link: api/index
:link-type: doc

Todas as funções e classes, geradas a partir do código.
:::

:::{grid-item-card} 🛠️ Desenvolvimento
:link: desenvolvimento/index
:link-type: doc

Como contribuir, rodar os testes e publicar versões.
:::
::::

## Recursos

- **Estados e operadores**: base de Fock, estados coerentes, kets de vários qubits, estados
  de Bell, GHZ e W, matriz densidade; operadores de criação/destruição, posição, momento,
  Pauli, produto tensorial e comutadores.
- **Dinâmica**: equação de Schrödinger e **equação mestra de Lindblad** (sistemas abertos),
  com evolução exata (`expm_multiply`) ou integradores Runge-Kutta.
- **Computação quântica**: portas de um e vários qubits (H, S, T, rotações, CNOT, CZ, SWAP,
  Toffoli, portas controladas em qubits quaisquer) e simulação de medidas.
- **Medidas**: valores esperados, traço parcial, pureza, entropia de von Neumann,
  fidelidade, vetor de Bloch.
- **Visualização**: função de Wigner, esfera de Bloch e distribuição de Fock.
- **Denso ou esparso**: os dois formatos se misturam livremente.

```{toctree}
:hidden:
:caption: Primeiros passos

instalacao
guia_rapido
```

```{toctree}
:hidden:
:caption: Aprender

guia/index
tutoriais/index
```

```{toctree}
:hidden:
:caption: Referência

api/index
changelog
citar
```

```{toctree}
:hidden:
:caption: Projeto

desenvolvimento/index
```
