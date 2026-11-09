# tutoriais — aprendendo simulação e computação quântica

Notebooks Jupyter do Q-BASIC. A ordem e os títulos ficam em [`indice.yml`](indice.yml)
(usado também pela documentação e pelo livro em LaTeX).

## Como rodar

```bash
pip install "Q-BASIC[tutorial]"   # Q-BASIC + JupyterLab, matplotlib, SymPy e QuTiP
jupyter lab tutoriais/
```

No Google Colab, abra o notebook pelo GitHub (Arquivo → Abrir notebook → GitHub) e rode
`!pip install "Q-BASIC[tutorial]"` na primeira célula.

Os tutoriais também existem como **livro em PDF**, gerado a partir destes notebooks: veja
[`tutorial_latex/`](../tutorial_latex/).

Todos os notebooks são executados no CI a cada push, para garantir que continuam
funcionando. Algumas células mostram um erro **de propósito** (a aula seguinte resolve o
problema); elas têm a tag `raises-exception`.

## Parte I — Construindo um simulador quântico ([`simulador/`](simulador/))

As aulas 0 a 9 constroem, passo a passo, a classe de objetos quânticos que deu origem à
biblioteca, comparando os resultados com o QuTiP. As aulas 10 a 12 usam a biblioteca
pronta.

| Aula | Notebook | Assunto |
|---|---|---|
| 0 | [`00_introducao`](simulador/00_introducao.ipynb) | Kets, bras, operadores, estado de Fock, matriz densidade (com QuTiP) |
| 1 | [`01_classe_base`](simulador/01_classe_base.ipynb) | A classe `ObjQuantico`, kets/bras e exibição em LaTeX |
| 2 | [`02_soma_subtracao`](simulador/02_soma_subtracao.ipynb) | Soma e subtração |
| 3 | [`03_multiplicacao_divisao`](simulador/03_multiplicacao_divisao.ipynb) | Escalares, produto interno/externo, operadores, produto tensorial |
| 4 | [`04_matrizes_de_pauli`](simulador/04_matrizes_de_pauli.ipynb) | Matrizes de Pauli e Hamiltoniano de um qubit |
| 5 | [`05_estado_coerente`](simulador/05_estado_coerente.ipynb) | Base de Fock e estado coerente (duas formas) |
| 6 | [`06_matriz_densidade`](simulador/06_matriz_densidade.ipynb) | Matriz densidade de estados puros e mistos |
| 7 | [`07_operadores_x_e_p`](simulador/07_operadores_x_e_p.ipynb) | Operadores posição e momento |
| 8 | [`08_hamiltoniana`](simulador/08_hamiltoniana.ipynb) | Hamiltoniano de sistemas acoplados (Jaynes-Cummings) |
| 9 | [`09_dinamica`](simulador/09_dinamica.ipynb) | Resolvendo a equação de Schrödinger com o SciPy |
| 10 | [`10_testando_a_biblioteca`](simulador/10_testando_a_biblioteca.ipynb) | Jaynes-Cummings com a biblioteca `qbasic` |
| 11 | [`11_matrizes_esparsas`](simulador/11_matrizes_esparsas.ipynb) | A versão esparsa da classe e das funções |
| 12 | [`12_usando_o_qbasic`](simulador/12_usando_o_qbasic.ipynb) | Wigner, gato de Schrödinger, colapso e renascimento, emaranhamento, Lindblad |

## Parte II — Computação quântica ([`computacao_quantica/`](computacao_quantica/))

| # | Notebook | Assunto |
|---|---|---|
| 1 | [`01_primeiro_simulador`](computacao_quantica/01_primeiro_simulador.ipynb) | Estados, produto interno, superposição, medida e um simulador com NumPy |
| 2 | [`02_portas_e_emaranhamento`](computacao_quantica/02_portas_e_emaranhamento.ipynb) | Esfera de Bloch, portas, medidas, circuito de Bell, emaranhamento, teleportação |

## Em construção ([`em_construcao/`](em_construcao/))

Rascunhos de versões do simulador com PyTorch, Numba e CuPy (GPU). Não fazem parte da
sequência nem são executados no CI.
