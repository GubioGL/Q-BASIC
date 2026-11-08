# Instalação

O Q-BASIC precisa do **Python 3.10 ou mais recente** e depende apenas de **NumPy** e
**SciPy**.

```bash
pip install Q-BASIC
```

O pacote se chama `Q-BASIC` no PyPI, mas é importado como `qbasic`:

```python
import qbasic as qb

print(qb.__version__)
```

## Extras opcionais

| Comando | O que acrescenta |
|---|---|
| `pip install "Q-BASIC[plot]"` | matplotlib, para os gráficos (`plotar_wigner`, `esfera_bloch`...) |
| `pip install "Q-BASIC[tutorial]"` | JupyterLab, matplotlib, SymPy e QuTiP, para rodar os tutoriais |
| `pip install "Q-BASIC[gpu]"` | PyTorch (experimental, para os rascunhos de backend em GPU) |
| `pip install "Q-BASIC[docs]"` | ferramentas para gerar esta documentação |
| `pip install "Q-BASIC[dev]"` | testes, lint e empacotamento (para quem desenvolve) |

## Google Colab

Numa célula do notebook:

```text
!pip install "Q-BASIC[plot]"
```

## A partir do código-fonte

```bash
git clone https://github.com/GubioGL/Q-BASIC.git
cd Q-BASIC
pip install -e ".[dev]"     # modo editável, com as ferramentas de desenvolvimento
pytest                      # confere a instalação rodando os testes
```

Veja {doc}`desenvolvimento/index` para o fluxo completo de desenvolvimento.

## Vindo da versão 0.0.x?

A versão 0.1.0 renomeou as funções para nomes sem acento (`destruiçao` → `destruicao`,
`edo.solve` → `resolver_schrodinger`...). Os nomes antigos continuam funcionando, mas
mostram um aviso com o nome novo. A tabela completa está no {doc}`changelog`.
