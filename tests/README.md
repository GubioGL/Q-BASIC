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
| `test_objeto.py` | Classe `ObjQuantico`: formatos denso/esparso e conversões, `dims`, `tipo`, aritmética (escalares, mistura de formatos, erros de forma), potência, adjunto, traço, autovalores/autoestados (inclusive os `k` menores no esparso), exponencial, normas, interoperabilidade com NumPy, `repr` e LaTeX. |
| `test_operadores.py` | Pauli (`σ² = I`, `σxσy = iσz`, anticomutação), criação/destruição (`a\|n⟩ = √n\|n−1⟩`), operador número, `[a, a†]`, posição e momento (`[x, p] = i`), identidade, `tensor`. |
| `test_estados.py` | `bases`, `ket`/`bra` (inclusive vários qubits, `ket("0110")`), `fock` e estado coerente (normalização, Poisson, `⟨n⟩ = \|α\|²`, `a\|α⟩ = α\|α⟩`, estabilidade para N grande). |
| `test_matriz_densidade.py` | `matriz_densidade`: estados puros e mistos, traço 1, hermiticidade, positividade, pureza e validação das entradas. |
| `test_dinamica.py` | `resolver_schrodinger` (métodos `expm`, `RK45`, `DOP853`) contra soluções analíticas (Rabi, Jaynes-Cummings) e contra `exp(−iHt)`; conservação da norma; tempos não uniformes; `Resultado`; o Hamiltoniano esparso não é convertido para denso; valores esperados. |
| `test_portas.py` | Portas de 1 e vários qubits (unitariedade, identidades como `HXH = Z`, tabela-verdade de CNOT/Toffoli, qubits não vizinhos), circuito de Bell, estados de Bell, GHZ e W. |
| `test_medidas.py` | Probabilidades, amostragem, traço parcial, pureza, entropia, fidelidade (inclusive a fórmula fechada para qubits), vetor de Bloch, comutadores. |
| `test_lindblad.py` | Equação mestra: emissão espontânea, oscilador amortecido, defasagem, equivalência com Schrödinger sem colapso, traço/hermiticidade/positividade, Liouvilliano. |
| `test_visualizacao.py` | Função de Wigner (vácuo, Fock, coerente, normalização e comparação com a definição por paridade) e os gráficos. |
| `test_tutoriais.py` | Tutoriais: índice × arquivos, títulos, um único título de nível 1, nomes obsoletos, metadados, erros salvos só nas células marcadas. |
| `test_esparso.py` | Equivalência numérica entre os formatos denso e esparso em todas as construções e operações. |
| `test_compat.py` | Os nomes da versão 0.0.x (`destruiçao`, `Identidade`, `Fock`, `edo.solve`, `Valor_esperado`, `traço()`, módulos `operador`/`funçoes`/`class_tijolo`...) continuam funcionando e avisam o nome novo; o código antigo dos tutoriais roda. |
| `test_regressoes.py` | Um teste por bug corrigido na 0.1.0 (B2–B20, P7 da seção 1.2 do `PLANO_DE_TRABALHO.md`). |
| `test_exemplos.py` | Os scripts de `exemplos/` rodam do início ao fim (precisa de matplotlib). |
| `test_readme.py` | Os blocos ```` ```python ```` do `README.md` rodam (bug B1). |
| `auxiliares.py`, `conftest.py` | Funções auxiliares e fixtures. |

Além disso, os exemplos das docstrings (`>>> ...`) são executados como *doctests*
(`make doctest`), também no CI.

## Como rodar

```bash
pip install -e ".[test]"
pytest                                      # todos os testes
pytest --cov=qbasic --cov-report=term-missing   # com cobertura (mínimo exigido: 90%)
pytest tests/test_estados.py -q             # um arquivo
pytest -k coerente                          # testes cujo nome contém "coerente"
```

Os avisos (`warnings`) são tratados como erros (`filterwarnings = ["error"]` no
`pyproject.toml`), para que problemas silenciosos apareçam cedo.
