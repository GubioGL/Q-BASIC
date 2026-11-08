# tests — testes unitários do Q-BASIC

Testes escritos com **pytest**. Rodam automaticamente no GitHub Actions a cada push e
pull request (`.github/workflows/testes.yml`).

Os testes verificam **resultados físicos conhecidos** (álgebra de Pauli, `[a, a†] = 1`,
estado coerente com distribuição de Poisson, oscilação de Rabi, modelo de
Jaynes-Cummings...). Assim eles continuam válidos quando o código interno for
reorganizado. Quase todos rodam duas vezes, com matrizes **densas** e **esparsas**
(fixture `sparsa` em `conftest.py`).

| Arquivo | O que cobre |
|---|---|
| `test_objeto.py` | Classes base `ObjQuantico` e `ObjQuantico_esparso`: soma, subtração, produto por escalar, produto matricial (`*`), produto tensorial (`@`), potência, adjunto, traço, autovalores, exponencial, erros de tipo e `repr`. |
| `test_operadores.py` | Pauli (`σ² = I`, `σxσy = iσz`, anticomutação), criação/destruição (`a\|n⟩ = √n\|n−1⟩`), operador número, `[a, a†]`, posição e momento (`[x, p] = i`), identidade. |
| `test_estados.py` | `bases`, `ket`, `bra`, `Fock` e estado coerente (normalização, Poisson, `⟨n⟩ = \|α\|²`, `a\|α⟩ = α\|α⟩`, método do operador = método analítico). |
| `test_matriz_densidade.py` | Estados puros e mistos: traço 1, hermiticidade, positividade, pureza, validação das entradas. |
| `test_dinamica.py` | Solver da equação de Schrödinger contra soluções analíticas (Rabi, Jaynes-Cummings) e contra `exp(−iHt)`; conservação da norma e das excitações; valores esperados. |
| `test_esparso.py` | Equivalência numérica entre os formatos denso e esparso em todas as construções e operações. |
| `test_compat.py` | Todos os nomes públicos (`qb.destruiçao`, `qb.funçoes.edo`...) continuam existindo; versão do pacote. |
| `test_exemplos.py` | Os scripts de `exemplos/` rodam do início ao fim (precisa de matplotlib). |
| `test_readme.py` | Os blocos ```` ```python ```` do `README.md` rodam. |
| `test_bugs_conhecidos.py` | Um teste para cada bug da seção 1.2 do `PLANO_DE_TRABALHO.md` (B2–B20, P7). |
| `auxiliares.py`, `conftest.py` | Funções auxiliares e fixtures. |

## Bugs conhecidos (`xfail`)

Os testes de `test_bugs_conhecidos.py` (e o do README) descrevem o comportamento
**correto** e estão marcados com `@pytest.mark.xfail`: aparecem como `XFAIL` no
relatório enquanto o bug existir. Como `xfail_strict = true` no `pyproject.toml`, quando
um bug for corrigido o teste "passa inesperadamente" (`XPASS`) e a suíte falha: é o
sinal para remover a marcação `xfail`, e o teste vira um teste normal de regressão.

## Como rodar

```bash
pip install -e ".[test]"
pytest                                      # todos os testes
pytest --cov=qbasic --cov-report=term-missing   # com cobertura (mínimo exigido: 90%)
pytest tests/test_estados.py -q             # um arquivo
pytest -k coerente                          # testes cujo nome contém "coerente"
pytest --runxfail tests/test_bugs_conhecidos.py   # mostra o erro real de cada bug
```

Os avisos (`warnings`) são tratados como erros (`filterwarnings = ["error"]` no
`pyproject.toml`), para que problemas silenciosos apareçam cedo.
