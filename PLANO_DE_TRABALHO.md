# Plano de trabalho — reestruturação do Q-BASIC

> **Status (09/11/2026):** Fases 1 a 10 concluídas (versão 0.1.0 pronta, ainda não
> publicada no PyPI). Falta a Fase 11 (acabamento).
> O projeto tem dois produtos: o **livro** (curso que ensina a construir um simulador
> quântico) e a **biblioteca** (produto final das aulas), descrita no **artigo para o
> JOSS**. O artigo em português foi removido; o que falta para submeter está em
> `paper/JOSS.md`.
> Para executar, é só pedir pelo número: *"faça a Fase 1"*, *"faça os itens 4.1 a 4.5"*,
> *"responda D3 com a opção B"*. Vou marcando `[x]` conforme cada item for concluído.

Legenda: `[ ]` a fazer · `[x]` feito · `(opcional)` só se você quiser · **D#** = decisão sua.

---

## 1. Diagnóstico — como o projeto estava antes da Fase 1

### 1.1 Inventário

| Item | Situação atual |
|---|---|
| `qbasic/class_tijolo.py` | Duas classes quase duplicadas: `ObjQuantico` (denso, NumPy) e `ObjQuantico_esparso` (SciPy COO). ~300 linhas, muita repetição. |
| `qbasic/operador.py` | Identidade, destruição, criação, X/P, Pauli X/Y/Z, matriz densidade. |
| `qbasic/estados.py` | `bases`, `ket`, `bra`, `Fock`, `coerente` (operador e analítico). |
| `qbasic/funçoes.py` | `edo.solve` (Schrödinger via `solve_ivp`), `valor_esperado`, `Valor_esperado`. |
| `setup.py` | Versão 0.0.4, dependências fixadas de forma que **impede a instalação** (ver 1.3). |
| `Testes/` | 2 scripts (Jaynes-Cummings) e 1 notebook de GPU. **Não são testes unitários** (sem `assert`, abrem `plt.show()`). |
| `Tutorial_simulador/` | 17 notebooks (Aula 0 a 12 + extras Numba/CuPy). |
| `Tutorial_computação_quantica/` | 1 notebook (primeiro simulador de qubits). |
| `.github/` | Não existe mais (o `python-publish.yml` foi apagado no commit `6d92f51`). |
| `README.md` | Bom visual, mas o exemplo de código não funciona e há links quebrados. |
| `LICENSE`, `.gitignore`, `pyproject.toml`, docs, CI | **Não existem.** |

### 1.2 Bugs confirmados (executei a biblioteca para verificar)

**✅ Todos corrigidos nas Fases 4 e 5 (versão 0.1.0).** Cada um tem um teste de regressão
em `tests/test_regressoes.py` (o B1, em `tests/test_readme.py`). Os caminhos abaixo são os
da versão antiga, antes da reestruturação.

| # | Onde (`src/qbasic/`) | Problema | Efeito |
|---|---|---|---|
| B1 | `README.md` (Demonstração Rápida) | O exemplo usa `estado_zero`, `estado_um` e `X`, que **não existem** no pacote. | Quem copia o exemplo recebe `ImportError`. |
| B2 | `class_tijolo.py` — `dim()` | `dim()` usa `len(dados)` → um **bra** de dimensão 4 retorna `1`. | Dimensão errada para bras/vetores-linha. |
| B3 | `class_tijolo.py` — `AutoValor_Vetor()` | A versão densa retorna **só os autovetores**, apesar do nome; a versão esparsa retorna os dois. | Comportamento diferente entre denso e esparso. |
| B4 | `class_tijolo.py` — `__repr__` | Chama `display()` do IPython e converte a matriz inteira para SymPy. | Fora do Jupyter imprime `<IPython...Math object>`; com matrizes grandes fica **muito lento**; IPython vira dependência obrigatória. |
| B5 | `class_tijolo.py` — `ObjQuantico_esparso.__mul__` | `print("Aqui !")` de depuração esquecido. | Polui a saída (aparece até ao criar estado coerente esparso). |
| B6 | `class_tijolo.py` — `__add__`, `__sub__`, `__truediv__` | `+`/`-` não aceitam escalar; `/` não aceita número complexo nem escalar NumPy; não existe `-A` (`__neg__`) nem `__radd__`. | `H + 1`, `A / 1j`, `-A` dão `TypeError`. |
| B7 | `class_tijolo.py` — `__rtruediv__` | `2 / A` faz divisão **elemento a elemento** (gera `inf`). | Operação sem sentido físico (deveria ser erro ou inversa). |
| B8 | `class_tijolo.py` (geral) | Não dá para misturar denso com esparso (`A_denso * B_esparso` → `TypeError`). | Usuário tem de escolher um formato para tudo. |
| B9 | `class_tijolo.py` — `traço()` | Descarta a parte imaginária silenciosamente. | Traço de operador não-hermitiano fica errado. |
| B10 | `class_tijolo.py` — `dag()` | Perde a representação LaTeX. | Pequeno, mas inconsistente. |
| B11 | `estados.py` — `ket()`, `bra()` | `ket('2')` só faz `print` e retorna `None`; `ket(1.5)` é aceito. | Erros silenciosos, aparecem depois em outro lugar. |
| B12 | `estados.py` — `bases()` | Não valida `n < N`: no denso dá `IndexError` genérico; no **esparso devolve um vetor nulo sem avisar**. | Mensagem de erro ruim / resultado errado silencioso. |
| B13 | `funçoes.py` — `edo.solve` | `if t_span == None` quebra quando `t_span` é array NumPy. | `ValueError` ao passar `t_span=np.array([0, 1])`. |
| B14 | `funçoes.py` — `edo.solve` | Tolerâncias padrão do RK45 (`rtol=1e-3`) → a norma do estado não se conserva: ⟨σz⟩ chegou a **1.00048** (> 1, fisicamente impossível). | Resultados de dinâmica imprecisos. |
| B15 | `funçoes.py` — `edo.solve` | Chama `.full()` no Hamiltoniano → **matriz esparsa vira densa**. | O modo esparso não traz ganho nenhum na dinâmica. |
| B16 | `funçoes.py` — `class edo` | Herda de `ObjQuantico` sem motivo. | Design confuso. |
| B17 | `setup.py` (removido) | `torch==2.5.1+cu118` não existe no PyPI; `numpy`, `IPython` e `matplotlib` não estavam listados; tudo fixado com `==`. | `pip install` falhava. **✅ Resolvido na Fase 1** (`pyproject.toml`). |
| B18 | `README.md` | Badge de licença apontava para `LICENSE` inexistente; `requirements.txt` inexistente; URL de clone placeholder; e-mails diferentes. | **✅ Resolvido na Fase 1** (falta só o B1). |
| B19 | `operador.py` — `matrizdensidade()` | Com listas de tamanhos diferentes, o `zip` ignora o que sobra (ex.: 2 probabilidades e 1 estado → traço 0,5). | Matriz densidade errada sem aviso. *(encontrado pelo linter na Fase 1)* |
| B20 | `estados.py` — `ket()`, `bra()` | A f-string engole as chaves: o LaTeX sai `\ket0` em vez de `\ket{0}`. | Só funciona para rótulos de um caractere. *(encontrado pelos testes na Fase 2)* |

### 1.3 Problemas de performance (otimização)

**✅ Todos resolvidos na Fase 5.** Medições em `benchmarks/resultados.md`.

| # | Onde (`src/qbasic/`) | Hoje | Proposta |
|---|---|---|---|
| P1 | `funçoes.py` — `Valor_esperado` | `Valor_esperado` faz laço Python sobre cada instante de tempo. | Uma única chamada vetorizada (`np.einsum`) — ordens de grandeza mais rápido. |
| P2 | `class_tijolo.py` — `__pow__` | `A**n` faz `n` multiplicações num laço. | `np.linalg.matrix_power` (exponenciação binária, `log n` produtos). |
| P3 | `class_tijolo.py` — `ObjQuantico_esparso.__init__` | Esparso guardado em **COO**, que precisa ser convertido a cada operação. | Guardar em **CSR** (formato certo para produtos e somas). |
| P4 | `class_tijolo.py` — `dim()`, autovalores e `__repr__` do esparso | `dim()`, autovalores e `__repr__` do esparso convertem para denso. | Usar `shape`; `eigsh`/`eigh` quando possível. |
| P5 | `class_tijolo.py` — `Autovalores()`, `Autovetores()` | `eigvals`/`eig` genéricos. | `eigvalsh`/`eigh` para operadores hermitianos (mais rápidos e precisos). |
| P6 | `funçoes.py` — `edo.solve` | Só `solve_ivp`. | Para H independente do tempo: `expm_multiply` (exato e funciona com esparso). |
| P7 | `estados.py` — `coerente(metodo="analitico")` | `factorial(n)` estoura para n > 170 e `alpha**n` pode estourar. | Calcular em log (`gammaln`) — estável para qualquer N. |

### 1.4 Problemas de organização

- Nomes com acento em arquivos e funções (`funçoes.py`, `destruiçao`, `criaçao`, `traço`, pastas `Tutorial_computação_quantica`, `Aula_0_introdução`) — funcionam no Python 3, mas dão problema em Windows, Sphinx, LaTeX, links e alguns terminais.
- Tutoriais com numeração inconsistente: `Aula_9` tem título "Aula 7", `Aula_11` diz "Aula 10", `Aula_12` e `EXTRA_numba` dizem "Aula 11", `EXTRA_Cupy` diz "Aula 10"; existem `Aula_1` e `Aula_1V2`; `Aula_12`, `EXTRA_numba` e `EXTRA_Cupy` estão praticamente vazias.
- Vários tutoriais importam **QuTiP**, que não é dependência do projeto.
- `Aula_9_Dinamica.ipynb` tem ~390 KB de saídas salvas.
- `Bra.png` solto na raiz.
- O README fala de um segundo pacote, **BRa**, que não está no repositório.
- Não há tipagem, docstrings em formato padronizado, linter nem formatação automática.

---

## 2. Decisões (respondidas: "siga as recomendações")

| # | Decisão | Escolha |
|---|---|---|
| D1 | Nomes com acento (`destruiçao`, `traço`, `funçoes`) | Passar para nomes sem acento na **Fase 5**, mantendo os antigos como apelidos com aviso de *deprecated*. |
| D2 | `*` = produto matricial, `@` = produto tensorial | **Manter** e adicionar a função `tensor()` (Fase 5). |
| D3 | Denso × esparso | **Uma única classe** `ObjQuantico` com formato denso/esparso; `ObjQuantico_esparso` vira apelido (Fase 5). |
| D4 | Pacote BRa | Retirado do README como pacote existente; agora aparece no **Roadmap**. ✅ |
| D5 | Backends PyTorch/CuPy/Numba | Dependência opcional (`pip install "Q-BASIC[gpu]"`) e roadmap. ✅ |
| D6 | Idioma da documentação | **Português** primeiro. |
| D7 | Paper | **Só o JOSS** (`paper.md`, inglês), sobre a biblioteca; o artigo em português (RBEF) foi descartado. O livro vai para o arXiv. Como o JOSS ainda não é possível (falta uso em pesquisa e histórico distribuído), o plano é: DOI no Zenodo + preprint da biblioteca no arXiv agora e JOSS depois (ver `paper/JOSS.md`, seção 9). Autor único: **Gubio Gomes de Lima**; afiliação em branco por enquanto. |
| D8 | Licença | **MIT** (`LICENSE` criado). ✅ |
| D9 | Python mínimo | **3.10+**, testado de 3.10 a 3.14. Obs.: o Python 3.10 chegou ao fim do suporte em out/2026; vale subir o mínimo para 3.11 numa versão futura. ✅ |
| D10 | Layout do pacote | **`src/qbasic/`**. ✅ |
| D11 | PyPI | Nome **`Q-BASIC`** mantido (o nome `qbasic` também está livre, se um dia precisar). Publicação **automática** ao criar uma release no GitHub. ✅ — falta a configuração única no PyPI descrita em `docs/source/desenvolvimento/publicacao.md`. |
| D12 | Contato oficial | `gubiofisikal@gmail.com`. ✅ |

---

## 3. Estrutura alvo do repositório

Baseada no REPAQ (zip enviado) + guias da comunidade (Scientific Python Development Guide, PyPA, pyOpenSci):

```text
Q-BASIC/
├── .github/
│   ├── workflows/
│   │   ├── testes.yml           # ✅ pytest + lint em TODO push e pull request
│   │   ├── publicar.yml         # ✅ publica no PyPI ao criar release
│   │   ├── docs.yml             # ✅ gera o site HTML e publica no GitHub Pages
│   │   ├── tutorial-pdf.yml     # (opcional) gera o PDF do tutorial LaTeX
│   │   └── paper.yml            # (opcional) compila o paper
│   ├── dependabot.yml           # ✅ atualiza as versões das Actions
│   ├── ISSUE_TEMPLATE/          # modelos de bug report / pedido de funcionalidade
│   └── pull_request_template.md
├── src/qbasic/
│   ├── __init__.py              # API pública + __version__
│   ├── objeto.py                # ObjQuantico (classe base única, denso/esparso)
│   ├── estados.py               # bases, ket, bra, fock, coerente, ...
│   ├── operadores.py            # identidade, destruicao, criacao, pauli, x, p, ...
│   ├── dinamica.py              # solver de Schrödinger (+ Lindblad, se quiser)
│   ├── medidas.py               # valor esperado, fidelidade, entropia, traço parcial
│   ├── visualizacao.py          # representação LaTeX, gráficos
│   └── _compat.py               # apelidos antigos (destruiçao, funçoes, edo...) com aviso
├── tests/                       # testes unitários (pytest)
├── docs/                        # ✅ Sphinx → site HTML
│   ├── source/ (conf.py, index, guia/, api/, desenvolvimento/, _static/)
│   ├── publicacao.md            # ✅ como lançar uma versão no PyPI
│   ├── Makefile, make.bat, requirements.txt
├── tutoriais/
│   ├── simulador/               # Aulas renomeadas e numeradas (00_introducao.ipynb, ...)
│   ├── computacao_quantica/
│   └── indice.yml               # ✅ ordem e títulos dos capítulos (usado pelo script LaTeX e pelos docs)
├── tutorial_latex/              # ✅ modelo LaTeX do livro + saída gerada (build/ ignorado no git)
├── scripts/
│   └── gerar_tutorial_latex.py  # ✅ notebooks → livro LaTeX/PDF
├── paper/                       # ✅ artigo do JOSS (joss/), guia JOSS.md e gerar_figuras.py
├── exemplos/                    # scripts prontos (ex.: Jaynes-Cummings, vindo de Testes/)
├── benchmarks/                  # medições de desempenho (alimentam o paper)
├── pyproject.toml               # ✅ substitui o setup.py
├── MANIFEST.in                  # ✅ inclui tests/ e exemplos/ no pacote-fonte
├── Makefile                     # atalhos: make test, make docs, make tutorial, make paper
├── README.md, LICENSE, CITATION.cff, CHANGELOG.md, CONTRIBUTING.md
└── .gitignore, .pre-commit-config.yaml
```

---

## 4. Tarefas por fase

A ordem importa: **os testes vêm antes da refatoração**, para garantir que nada da física muda enquanto o código é reorganizado.

### Fase 1 — Base do projeto (empacotamento e organização)
- [x] 1.1 `pyproject.toml` (PEP 621) no lugar do `setup.py`. Dependências: `numpy>=1.23`, `scipy>=1.10`, `sympy>=1.11`, `ipython>=8.0` (limites mínimos testados no CI). O `matplotlib` foi para o extra `[plot]`, porque a biblioteca não o usa.
- [x] 1.2 Extras opcionais: `[plot]`, `[gpu]` (torch), `[test]`, `[docs]`, `[tutorial]` (jupyterlab, matplotlib, qutip), `[dev]`. **Obs.:** o IPython continua obrigatório até a Fase 4 (item 4.4), porque o `__repr__` atual depende dele.
- [x] 1.3 Pacote movido para `src/qbasic/` com `git mv` (histórico preservado).
- [x] 1.4 `__version__ = "0.1.0"` em `src/qbasic/_version.py` (fonte única) e `__all__` em `__init__.py`.
- [x] 1.5 `.gitignore` (Python, Jupyter, LaTeX, builds de docs).
- [x] 1.6 `LICENSE` (MIT).
- [x] 1.7 `Bra.png` movido para `docs/source/_static/`; README atualizado (badges, instalação, estrutura, contato, BRa no roadmap).
- [x] 1.8 `Testes/*.py` → `exemplos/jaynes_cummings.py` e `exemplos/jaynes_cummings_esparso.py` (com docstring e READMEs); `testGPU.ipynb` → `benchmarks/teste_gpu_pytorch.ipynb`.
- [x] 1.9 `ruff` (lint + formatação, linha de 100) e `pre-commit`. Código formatado; os bugs B13 e B19 ficaram marcados com `# noqa` até a Fase 4. Notebooks fora do lint até a Fase 7.
- [x] 1.10 `Makefile` com `help`, `install`, `install-dev`, `test`, `cov`, `lint`, `format`, `build`, `clean`. (`docs`, `tutorial` e `paper` entram nas fases 8, 9 e 10.)

### Fase 2 — Testes unitários (pytest)
Testes baseados em **resultados físicos conhecidos**, que continuam válidos depois da refatoração:
- [x] 2.1 `tests/conftest.py` com fixtures (tolerâncias, dimensões, estados comuns) e parametrização denso/esparso.
- [x] 2.2 `test_objeto.py`: soma, subtração, produto por escalar, produto matricial, tensorial, `dag`, traço, potência, `expM`, autovalores, erros de tipo.
- [x] 2.3 `test_operadores.py`: álgebra de Pauli (σx² = I, σxσy = iσz, anticomutadores), `a|n⟩ = √n|n−1⟩`, `a†|n⟩ = √(n+1)|n+1⟩`, `[a, a†] = I` (fora do último nível truncado), hermiticidade de X e P, `[x, p] = i`.
- [x] 2.4 `test_estados.py`: normalização, ortogonalidade das bases, validação de entradas, estado coerente (⟨n⟩ = |α|², distribuição de Poisson, `a|α⟩ ≈ α|α⟩`), método "operador" = método "analítico".
- [x] 2.5 `test_matriz_densidade.py`: traço 1, hermiticidade, positividade, pureza `Tr(ρ²)` (puro = 1, misto < 1).
- [x] 2.6 `test_dinamica.py`: oscilação de Rabi contra a solução analítica, conservação da norma, Jaynes-Cummings (troca de excitação átomo↔cavidade), comparação com `expm`.
- [x] 2.7 `test_esparso.py`: toda operação densa = mesma operação esparsa.
- [x] 2.8 `test_compat.py`: todos os nomes públicos atuais (`qb.destruiçao`, `qb.funçoes.edo`...) continuam existindo — é a garantia de compatibilidade para a renomeação da Fase 5.
- [x] 2.9 `test_bugs_conhecidos.py` + `test_readme.py`: um teste `xfail` estrito por bug (B1–B20 e P7). Extras: `test_exemplos.py` roda os scripts de `exemplos/`.
- [x] 2.10 Cobertura de **98 %** (mínimo exigido: 90 %, `fail_under` no `pyproject.toml`) e `tests/README.md`. Resultado: 365 testes passando + 39 falhas esperadas (bugs). Avisos viram erro (`filterwarnings = error`).

### Fase 3 — GitHub Actions (CI)
- [x] 3.1 `.github/workflows/testes.yml`: roda em **todo push (qualquer branch) e todo pull request** (e pode ser disparado à mão).
- [x] 3.2 Matriz: Python 3.10, 3.11, 3.12, 3.13 e 3.14 no Ubuntu + Python 3.13 no Windows e no macOS.
- [x] 3.3 Jobs: **lint** (todos os hooks do pre-commit), **testes** (`pytest --cov`, resumo de cobertura na página da execução e `coverage.xml` como artefato), **dependências mínimas** (instala as versões mais antigas aceitas com `uv --resolution lowest-direct`) e **pacote** (gera sdist + wheel, `twine check` e roda os testes contra o wheel instalado num ambiente limpo).
- [x] 3.4 Badge de status dos testes e da versão no PyPI no README. *(Badge de cobertura exige um serviço externo como o Codecov; por enquanto a cobertura aparece no resumo de cada execução.)*
- [x] 3.5 Job **tutoriais** que executa todos os notebooks com `nbmake` (feito na Fase 7).
- [x] 3.6 Dependabot para atualizar as versões das Actions (`.github/dependabot.yml`, mensal).

### Fase 4 — Correção dos bugs (seção 1.2)
- [x] 4.1 B1 — README com exemplos que funcionam (porta X, estado de Bell, oscilação de Rabi), testados por `tests/test_readme.py`. Não foi preciso criar `estado_zero`/`estado_um`: `ket("0")` já cobre.
- [x] 4.2 B2 — `dim()` correto para kets, bras e operadores; `dims` guarda os subsistemas (ex.: `[[2, 2], [1, 1]]` para dois qubits), base para o traço parcial.
- [x] 4.3 B3, B5, B9, B10 — `autoestados()` devolve `(valores, vetores)`; print removido; `traco()` complexo quando preciso; `dag()` mantém o LaTeX (`\ket{x}` ↔ `\bra{x}`).
- [x] 4.4 B4 — `repr` em texto (sem IPython) e `_repr_latex_` próprio, com matrizes grandes resumidas. IPython e SymPy deixaram de ser dependências.
- [x] 4.5 B6, B7, B8 — `A + c` (= `A + c·I`), `c - A`, `-A`, divisão por qualquer escalar, `2 / A` gera `TypeError`, denso e esparso misturáveis, `ValueError` claro para formas incompatíveis.
- [x] 4.6 B11, B12 — `ValueError` com mensagem clara para entradas inválidas.
- [x] 4.7 B13, B14, B15, B16 — solver novo e `edo.solve` antigo corrigidos (`t_span is None`, `rtol=1e-8`/`atol=1e-10`, sem densificar, `edo` não herda mais de `ObjQuantico`).
- [x] 4.8 B17, B18 — dependências e README (resolvidos na Fase 1).
- [x] 4.9 B19, B20 — `matriz_densidade` exige listas do mesmo tamanho; LaTeX `\ket{0}`.
- [x] 4.10 Marcações `xfail` removidas: `test_bugs_conhecidos.py` virou `test_regressoes.py`.

### Fase 5 — Otimização e reorganização do núcleo
- [x] 5.1 Classe única `ObjQuantico` (`objeto.py`) com `formato="denso" | "esparso"`; `ObjQuantico_esparso(...)` virou apelido (e `isinstance(A, ObjQuantico_esparso)` continua funcionando).
- [x] 5.2 Esparso em CSR (`csr_array`); conversões só quando necessário (P3, P4). `dim()`, `shape` e o `repr` não convertem mais para denso.
- [x] 5.3 `matrix_power`/exponenciação binária, `eigh`/`eigvalsh` para hermitianos, `eigsh` para os `k` menores autovalores no esparso, `expm_multiply` (P2, P5, P6).
- [x] 5.4 Valor esperado vetorizado com `einsum` (P1); aceita kets, matrizes densidade, listas e `Resultado`.
- [x] 5.5 Estado coerente analítico em escala logarítmica (`gammaln`), estável para qualquer N (P7).
- [x] 5.6 `resolver_schrodinger(H, psi0, tempos, observaveis)` → `Resultado` (`.tempos`, `.vetores`, `.estados`, `.valores_esperados`, e `.t`/`.y` como no `solve_ivp`). Método padrão `"expm"` (exato); `"RK45"`, `"DOP853"`, etc. também. `edo.solve` continua funcionando.
- [x] 5.7 Nomes sem acento e em minúsculas, com os antigos como apelidos que emitem `DeprecationWarning` (tabela no `CHANGELOG.md`); módulos `operadores`, `medidas`, `dinamica`, `visualizacao`; `class_tijolo`, `operador` e `funçoes` viraram módulos de compatibilidade; `tensor()`.
- [x] 5.8 Type hints e docstrings NumPy nas funções públicas; os exemplos das docstrings rodam como doctests no CI.
- [x] 5.9 `benchmarks/bench_nucleo.py` e `benchmarks/comparar_versoes.py` (antes × depois). Ganhos: valor esperado ~20×, solver esparso ~25× (`resolver_schrodinger` ~150×), potência ~10×, `repr` ~100×.

### Fase 6 — Funcionalidades novas (opcional, você escolhe quais)
- [x] 6.1 `tensor()`, `comutador()`, `anticomutador()` e `numero()`.
- [x] 6.2 `traco_parcial`, `fidelidade` (Uhlmann-Jozsa, entre 0 e 1), `entropia_von_neumann` (em bits), `pureza`; também `probabilidades`, `amostrar` (simula medidas) e `vetor_bloch`.
- [x] 6.3 Módulo `portas`: `hadamard`, `porta_s`, `porta_t`, `fase`, `rx`/`ry`/`rz`, `cnot`, `cz`, `swap`, `toffoli`, `porta_controlada` e `porta_em` (porta em qubits quaisquer, inclusive não vizinhos); estados `bell`, `ghz`, `w` e `ket("0110")`.
- [x] 6.4 `resolver_lindblad` (equação mestra; método exato `expm` ou RK) e `liouvilliano`; testado com emissão espontânea, oscilador amortecido e defasagem.
- [x] 6.5 `wigner` (validada contra a definição por paridade deslocada), `plotar_wigner`, `plotar_fock`, `plotar_valores_esperados` e `esfera_bloch`.
- [ ] 6.6 Backends GPU (PyTorch/CuPy) — fica no roadmap, conforme D5 (os rascunhos estão em `tutoriais/em_construcao/`).

### Fase 7 — Tutoriais
- [x] 7.1 Notebooks em `tutoriais/simulador/` (aulas 0 a 12) e `tutoriais/computacao_quantica/`, sem acento, numeração correta e títulos padronizados ("Aula N — ..."); histórico preservado com `git mv`.
- [x] 7.2 `Aula_1` e `Aula_1V2` unidas em `01_classe_base.ipynb`; PyTorch, Numba e CuPy movidos para `tutoriais/em_construcao/` (fora do índice, da documentação e do CI).
- [x] 7.3 `tutoriais/indice.yml` com as partes e os capítulos.
- [x] 7.4 Aulas 10 e 11 na API nova; as aulas 0 a 9 constroem a classe do zero e não usam a biblioteca. **Novos:** Aula 12 (Wigner, gato de Schrödinger, colapso e renascimento, emaranhamento, Lindblad) e Computação quântica 2 (Bloch, portas, medidas, Bell, GHZ/W, teleportação).
- [x] 7.5 QuTiP (e SymPy) no extra `[tutorial]`.
- [x] 7.6 Saídas regeneradas com a versão atual, metadados padronizados, células de erro didático com a tag `raises-exception`, títulos com um único nível 1 por notebook.
- [x] 7.7 `tutoriais/README.md`; `tests/test_tutoriais.py` confere índice, títulos, nomes obsoletos, metadados e erros salvos.

### Fase 8 — Documentação HTML (site da biblioteca)
- [x] 8.1 Sphinx + Furo, `autodoc` + `napoleon` (docstrings NumPy), `sphinx-copybutton`, `sphinx-design`. *(O `intersphinx` ficou de fora para a geração não depender de acesso à internet.)*
- [x] 8.2 `myst-nb`: os tutoriais aparecem com as saídas salvas, copiados na ordem do `indice.yml`; as páginas do guia são **executadas** a cada geração.
- [x] 8.3 Páginas: Início, Instalação, Guia rápido, Guia do usuário (objetos, estados e operadores, dinâmica, medidas, computação quântica, visualização), Tutoriais, Referência da API (um arquivo por módulo + nomes antigos), Changelog, Como citar, Desenvolvimento (+ publicação no PyPI).
- [x] 8.4 Logo e favicon recortados do `Bra.png`; cor principal roxa do "BR" (`#5E17EB`).
- [x] 8.5 `.github/workflows/docs.yml`: gera o site em todo push/PR (avisos = erro) e publica no GitHub Pages a partir da `main`. ⚠️ **Você precisa ativar uma vez:** Settings → Pages → Source: **GitHub Actions**. Endereço: <https://gubiogl.github.io/Q-BASIC/>.
- [x] 8.6 `docs/README.md`, `make docs` (raiz) e `docs/Makefile`/`make.bat`.

### Fase 9 — Script: tutoriais → livro em LaTeX
- [x] 9.1 `scripts/gerar_tutorial_latex.py`: lê `tutoriais/indice.yml`, monta a Parte I (simulador) e a Parte II (computação quântica), converte o Markdown (com as equações), destaca o código, preserva as saídas de texto, as matrizes em LaTeX, os gráficos (em `figuras/`) e os erros propositais (em vermelho), e gera `tutorial_latex/build/tutorial.tex` (mais o `tutorial.md` intermediário). *(Um único `.tex` em vez de um por capítulo: é o que o pandoc gera e é mais simples de compilar.)* Ajustes automáticos: `\begin{equation}` → `$$`, `$ x $` → `$x$`, arrays do QuTiP com colunas a mais.
- [x] 9.2 Modelo em `tutorial_latex/modelo/`: capa (logo, versão e data), sumário, prefácio, classe `book` em português, fontes DejaVu (cobrem ψ, ⟩, ⊗...), blocos de código com fundo e quebra de linha, saídas com barra lateral, cabeçalho com o nome da aula.
- [x] 9.3 `--pdf` compila com XeLaTeX/`latexmk`. Atalho: **`make livro`**. Resultado atual: 124 páginas, sem linhas estourando a margem.
- [x] 9.4 Extra `[livro]` com `pypandoc_binary` (pandoc embutido); funciona também com o pandoc do sistema (testado com o 3.1).
- [x] 9.5 `tests/test_livro.py`: funções de conversão e geração de um livro pequeno, incluindo a compilação do PDF quando há XeLaTeX.
- [x] 9.6 Workflow **Livro dos tutoriais** (`livro.yml`): gera o PDF quando os tutoriais ou o modelo mudam, guarda nos *Artifacts* e **anexa o PDF a cada release**.

### Fase 10 — Paper / artigo científico (`paper/`)
- [x] 10.1 Estrutura: `paper/joss/` (`paper.md`, `paper.bib`, figura), `paper/gerar_figuras.py`, `paper/README.md` e o guia `paper/JOSS.md`. *(O artigo em português em LaTeX foi feito e depois removido, a seu pedido.)*
- [x] 10.2 Artigo do JOSS em inglês (~1650 palavras) com todas as seções obrigatórias: Summary, Statement of need, State of the field (com a justificativa "build vs. contribute"), Software design, Research impact statement, AI usage disclosure, Acknowledgements e References (19 referências conferidas com o pandoc).
- [x] 10.3 `paper/gerar_figuras.py` refaz a figura do artigo (decoerência do gato de Schrödinger) a partir da própria biblioteca.
- [x] 10.4 Workflow **Artigo** (`paper.yml`): refaz a figura e gera o PDF com a ferramenta oficial do JOSS; o PDF fica nos *Artifacts*. Localmente: `make artigo` (Docker).
- [x] 10.5 Guia `paper/JOSS.md`: pontos obrigatórios do artigo, portões da pré-avaliação, checklist dos revisores com o status do repositório, como justificar o artigo e o que investir antes de submeter.
- [ ] 10.6 **Você:** preencher os `TODO` do `paper.md` (ORCID, afiliação, **impacto em pesquisa**, modelo/versão da IA, agradecimentos/financiamento) e cumprir os requisitos do `paper/JOSS.md` antes de submeter.

### Fase 11 — Acabamento profissional
- [ ] 11.1 *(parcial: badges, instalação e estrutura já atualizados na Fase 1)* README novo: badges (testes, cobertura, docs, Python, licença), instalação real, exemplo que funciona, links para docs/tutoriais/paper, como citar.
- [x] 11.2 `CITATION.cff` (botão "Cite this repository" do GitHub) — criado na Fase 8, com a página "Como citar".
- [ ] 11.3 `CHANGELOG.md` ✅ (criado na Fase 5, com o guia de migração) e `CONTRIBUTING.md` (como rodar testes, estilo de código, como abrir PR).
- [ ] 11.4 Modelos de issue e de pull request.
- [ ] 11.4b Exigências do JOSS para boas práticas: `CODE_OF_CONDUCT.md`, onde pedir suporte (issues/Discussions/e-mail) e uma frase de governança (ver `paper/JOSS.md`).
- [x] 11.5 `publicar.yml`: ao publicar uma release no GitHub, roda todos os testes, confere se a tag bate com a versão, gera o pacote e envia ao PyPI (*Trusted Publishing*, sem senha no repositório). Guia em `docs/source/desenvolvimento/publicacao.md`. ⚠️ **Você precisa fazer a configuração única no PyPI** (passo a passo no guia).
- [ ] 11.6 (opcional, você faz no site) ligar o repositório ao **Zenodo** para ter DOI a cada release.
- [ ] 11.7 Apagar este `PLANO_DE_TRABALHO.md` (ou movê-lo para `docs/`) quando tudo estiver concluído.

---

## 5. Ordem sugerida de execução

| Etapa | Fases | Por quê |
|---|---|---|
| 1 ✅ | Decisões D1–D12 | Mudam nomes, estrutura e API. |
| 2 ✅ | Fase 1 → Fase 2 → Fase 3 | Projeto instalável + testes + CI: rede de segurança antes de mexer no código. |
| 3 ✅ | Fase 4 → Fase 5 | Corrigir e otimizar com os testes garantindo a física. |
| 4 ✅ | Fase 6 (se quiser) | Novas funcionalidades sobre uma base estável. |
| 5 ✅ | Fase 7 → Fase 8 → Fase 9 | Tutoriais atualizados alimentam o site e o livro LaTeX. |
| 6 | Fase 10 ✅ → Fase 11 | O paper usa os benchmarks e os tutoriais; o acabamento fecha a versão 0.1.0. |

Cada fase vira um ou mais commits na branch `claude/vibrant-faraday-ucinuf`, com os testes passando antes de seguir para a próxima.

---

## 6. Referências usadas para a estrutura

- Projeto REPAQ (`qrng-ppe`, zip enviado): `pyproject.toml`, `tests/` com pytest, workflow de testes, Sphinx + Furo, `CITATION.cff`, READMEs por pasta.
- Scientific Python Library Development Guide — https://learn.scientific-python.org/development/
- Python Packaging User Guide (PyPA) — https://packaging.python.org/
- pyOpenSci Python Package Guide — https://www.pyopensci.org/python-package-guide/
- QuTiP (referência de API para simulação quântica em Python) — https://qutip.org/
- Journal of Open Source Software — https://joss.readthedocs.io/
