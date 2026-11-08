# exemplos — scripts prontos com o Q-BASIC

Scripts curtos que mostram o uso da biblioteca em problemas físicos. Cada um roda
sozinho depois de instalar o pacote com os gráficos:

```bash
pip install "Q-BASIC[plot]"
python exemplos/jaynes_cummings.py
```

| Script | O que mostra |
|---|---|
| [`jaynes_cummings.py`](jaynes_cummings.py) | Modelo de Jaynes-Cummings (átomo de dois níveis + cavidade): monta o Hamiltoniano, resolve a equação de Schrödinger e plota o número de fótons e a população atômica. |
| [`jaynes_cummings_esparso.py`](jaynes_cummings_esparso.py) | O mesmo Hamiltoniano montado com matrizes esparsas. |

Os testes em `tests/test_exemplos.py` executam estes scripts para garantir que continuam
funcionando.
