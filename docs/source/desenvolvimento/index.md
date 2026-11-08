# Desenvolvimento

Contribuições são bem-vindas: correções, novos recursos, exemplos, tutoriais e melhorias
na documentação.

```{toctree}
:hidden:

publicacao
```

## Ambiente

```bash
git clone https://github.com/GubioGL/Q-BASIC.git
cd Q-BASIC
pip install -e ".[dev]"        # pacote em modo editável + pytest, ruff, pre-commit, build
pre-commit install             # verificações automáticas a cada commit
```

## Estrutura do repositório

| Pasta | Conteúdo |
|---|---|
| `src/qbasic/` | o pacote (`objeto`, `estados`, `operadores`, `portas`, `medidas`, `dinamica`, `visualizacao`) |
| `tests/` | testes unitários (pytest) |
| `tutoriais/` | notebooks, com a ordem em `tutoriais/indice.yml` |
| `exemplos/` | scripts curtos |
| `benchmarks/` | medições de desempenho |
| `docs/` | esta documentação (Sphinx) |

## Comandos do dia a dia

| Comando | O que faz |
|---|---|
| `make test` | roda os testes |
| `make cov` | testes com relatório de cobertura (mínimo exigido: 90 %) |
| `make doctest` | roda os exemplos das docstrings |
| `make lint` / `make format` | confere / corrige o estilo (ruff) |
| `make tutoriais` | executa todos os notebooks (precisa de `".[tutorial]"` e `nbmake`) |
| `make docs` | gera este site em `docs/_build/html` (precisa de `".[docs]"`) |
| `make bench` | compara o desempenho com a versão anterior à reestruturação |
| `make build` | gera o pacote (`dist/`) e confere os metadados |

No Windows sem `make`, rode os comandos que aparecem no `Makefile`.

## Boas práticas

- **Teste o comportamento físico**: compare com soluções analíticas (oscilação de Rabi,
  distribuição de Poisson...) e rode cada teste nos formatos denso e esparso (fixture
  `sparsa`).
- **Docstrings no padrão NumPy**, em português, com um exemplo (`Examples`) quando fizer
  sentido — eles aparecem na {doc}`../api/index` e são testados.
- Os avisos são tratados como erros nos testes (`filterwarnings = ["error"]`).
- Nomes novos devem ser em português, sem acento e em minúsculas.

## Integração contínua

A cada push e pull request, o GitHub Actions roda:

- **lint**: todos os hooks do pre-commit (ruff, espaços, YAML/TOML);
- **testes**: Python 3.10 a 3.14 no Linux, e 3.13 no Windows e no macOS, com cobertura e
  doctests;
- **dependências mínimas**: as versões mais antigas aceitas pelo `pyproject.toml`;
- **pacote**: gera o wheel e roda os testes com ele instalado num ambiente limpo;
- **tutoriais**: executa todos os notebooks;
- **documentação**: gera este site (e o publica no GitHub Pages a partir da `main`).

Para lançar uma versão no PyPI, veja {doc}`publicacao`.
