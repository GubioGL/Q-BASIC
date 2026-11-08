# Plano de trabalho — reestruturação do Q-BASIC

> **Status (08/11/2026):** Fases 1 a 5 concluídas (versão 0.1.0 pronta, ainda não
> publicada no PyPI). As decisões estão registradas na seção 2.
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
| D7 | Paper | **Os dois**: RBEF (LaTeX, português) + JOSS (`paper.md`, inglês). Autor único: **Gubio Gomes de Lima**; afiliação em branco por enquanto. |
| D8 | Licença | **MIT** (`LICENSE` criado). ✅ |
| D9 | Python mínimo | **3.10+**, testado de 3.10 a 3.14. Obs.: o Python 3.10 chegou ao fim do suporte em out/2026; vale subir o mínimo para 3.11 numa versão futura. ✅ |
| D10 | Layout do pacote | **`src/qbasic/`**. ✅ |
| D11 | PyPI | Nome **`Q-BASIC`** mantido (o nome `qbasic` também está livre, se um dia precisar). Publicação **automática** ao criar uma release no GitHub. ✅ — falta a configuração única no PyPI descrita em `docs/publicacao.md`. |
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
│   │   ├── docs.yml             # gera o site HTML e publica no GitHub Pages
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
├── docs/                        # Sphinx → site HTML
│   ├── source/ (conf.py, index, guia, conceitos, tutoriais, api, _static/)
│   ├── publicacao.md            # ✅ como lançar uma versão no PyPI
│   ├── Makefile, make.bat, requirements.txt
├── tutoriais/
│   ├── simulador/               # Aulas renomeadas e numeradas (00_introducao.ipynb, ...)
│   ├── computacao_quantica/
│   └── indice.yml               # ordem e títulos dos capítulos (usado pelo script LaTeX e pelos docs)
├── tutorial_latex/              # modelo LaTeX do livro + saída gerada (build/ ignorado no git)
├── scripts/
│   └── gerar_tutorial_latex.py  # notebooks → livro LaTeX/PDF
├── paper/                       # artigo científico (LaTeX + bib + figuras)
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
- [ ] 3.5 (opcional) Job que **executa os notebooks dos tutoriais** (`nbmake`) — fica para a Fase 7, porque os notebooks dependem do QuTiP e precisam ser atualizados antes.
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
- [ ] 6.1 `tensor()` ✅ (feito na Fase 5), `comutador()`, `anticomutador()`.
- [ ] 6.2 Traço parcial, fidelidade, entropia de von Neumann, pureza.
- [ ] 6.3 Portas quânticas (H, S, T, CNOT, rotações) e estados de n qubits — ponte com o tutorial de computação quântica. *(Estados de n qubits já feitos: `ket("0110")`.)*
- [ ] 6.4 Equação mestra de Lindblad (sistemas abertos, matriz densidade).
- [ ] 6.5 Funções de visualização (esfera de Bloch, distribuição de Fock, função de Wigner).
- [ ] 6.6 Backends GPU (PyTorch/CuPy) — conforme D5.

### Fase 7 — Tutoriais
- [ ] 7.1 Renomear e numerar sem acento (`tutoriais/simulador/00_introducao.ipynb`, ...); corrigir os títulos internos ("Aula 7" dentro da `Aula_9`, etc.).
- [ ] 7.2 Decidir o que fazer com `Aula_1` × `Aula_1V2` (juntar) e com os notebooks quase vazios (`Aula_12`, `EXTRA_numba`, `EXTRA_Cupy`): completar ou mover para "em construção".
- [ ] 7.3 Criar `tutoriais/indice.yml` (ordem, título e parte de cada capítulo) — usado pelos docs e pelo script LaTeX.
- [ ] 7.4 Atualizar os notebooks para a API nova (sem quebrar a didática "construindo a classe do zero"). *Hoje eles funcionam, mas mostram avisos de nomes obsoletos (`destruiçao`, `edo.solve`, `class_tijolo`...).*
- [ ] 7.5 QuTiP como dependência opcional (`[tutorial]`), só para comparação.
- [ ] 7.6 Limpar saídas pesadas e padronizar metadados (o `Aula_9` tem 390 KB de saída).
- [ ] 7.7 `tutoriais/README.md` com o índice das aulas.

### Fase 8 — Documentação HTML (site da biblioteca)
- [ ] 8.1 Sphinx + tema **Furo** (o mesmo do REPAQ), `autodoc` + `napoleon` (API gerada das docstrings), `sphinx-copybutton`, `sphinx-design`.
- [ ] 8.2 `myst-nb` para os **tutoriais aparecerem como páginas do site** (sem reexecutar).
- [ ] 8.3 Páginas: Início, Instalação, Guia rápido, Conceitos (estados, operadores, dinâmica, denso × esparso), Tutoriais, Referência da API, Como contribuir, Como citar, Changelog.
- [ ] 8.4 Identidade visual: logo (`Bra.png`), cores, favicon.
- [ ] 8.5 `.github/workflows/docs.yml`: gera o site a cada push na `main` e publica no **GitHub Pages** (você precisa ativar o Pages nas configurações do repositório — eu explico o passo).
- [ ] 8.6 `docs/README.md` com como gerar localmente (`make docs`).

### Fase 9 — Script: tutoriais → livro em LaTeX
- [ ] 9.1 `scripts/gerar_tutorial_latex.py`, que:
  - lê `tutoriais/indice.yml` (ordem dos capítulos);
  - **Parte I — Simulação quântica** (`tutoriais/simulador/`) e **Parte II — Computação quântica** (`tutoriais/computacao_quantica/`);
  - converte células Markdown → LaTeX (preservando as equações `$...$`), código → `listings` com destaque de sintaxe, saídas de texto → `verbatim`, gráficos → arquivos em `figuras/` com `\includegraphics`, saídas LaTeX (`display(Math)`) → equações;
  - gera `tutorial_latex/build/tutorial.tex` (+ um `.tex` por capítulo).
- [ ] 9.2 Modelo do livro (`tutorial_latex/modelo/`): capa, sumário, prefácio, formatação em português (`babel`), estilo dos códigos.
- [ ] 9.3 Opção `--pdf` que compila com `latexmk`. Comandos finais:
  ```bash
  python scripts/gerar_tutorial_latex.py          # gera o .tex
  python scripts/gerar_tutorial_latex.py --pdf    # gera o .tex e compila o PDF
  make tutorial                                   # atalho
  ```
- [ ] 9.4 Usar `pypandoc_binary` (pandoc já embutido, instala via pip) para não exigir instalação manual do pandoc.
- [ ] 9.5 Testes do próprio script (gera o `.tex` a partir de um notebook pequeno de exemplo).
- [ ] 9.6 (opcional) `.github/workflows/tutorial-pdf.yml`: gera o PDF no CI e deixa para download.

### Fase 10 — Paper / artigo científico (`paper/`)
- [ ] 10.1 Estrutura: `paper/main.tex`, `paper/referencias.bib`, `paper/figuras/`, `paper/README.md` (como compilar).
- [ ] 10.2 Conteúdo proposto: Introdução e motivação (ensino de física/computação quântica no Brasil); trabalhos relacionados (QuTiP, Qiskit, QuantumOptics.jl); arquitetura do Q-BASIC (classe base, denso/esparso, solver); exemplos físicos (qubit e Rabi, estado coerente, Jaynes-Cummings) com figuras geradas por script; validação (testes contra soluções analíticas e QuTiP); desempenho (benchmarks da Fase 5); uso didático (os tutoriais); conclusão e trabalhos futuros.
- [ ] 10.3 Scripts que geram as figuras do paper a partir da própria biblioteca (reprodutível).
- [ ] 10.4 Versão JOSS (`paper/joss/paper.md` + `paper.bib`) — conforme D7.
- [ ] 10.5 (opcional) `.github/workflows/paper.yml` para compilar o PDF a cada mudança em `paper/`.

### Fase 11 — Acabamento profissional
- [ ] 11.1 *(parcial: badges, instalação e estrutura já atualizados na Fase 1)* README novo: badges (testes, cobertura, docs, Python, licença), instalação real, exemplo que funciona, links para docs/tutoriais/paper, como citar.
- [ ] 11.2 `CITATION.cff` (botão "Cite this repository" do GitHub).
- [ ] 11.3 `CHANGELOG.md` ✅ (criado na Fase 5, com o guia de migração) e `CONTRIBUTING.md` (como rodar testes, estilo de código, como abrir PR).
- [ ] 11.4 Modelos de issue e de pull request.
- [x] 11.5 `publicar.yml`: ao publicar uma release no GitHub, roda todos os testes, confere se a tag bate com a versão, gera o pacote e envia ao PyPI (*Trusted Publishing*, sem senha no repositório). Guia em `docs/publicacao.md`. ⚠️ **Você precisa fazer a configuração única no PyPI** (passo a passo no guia).
- [ ] 11.6 (opcional, você faz no site) ligar o repositório ao **Zenodo** para ter DOI a cada release.
- [ ] 11.7 Apagar este `PLANO_DE_TRABALHO.md` (ou movê-lo para `docs/`) quando tudo estiver concluído.

---

## 5. Ordem sugerida de execução

| Etapa | Fases | Por quê |
|---|---|---|
| 1 ✅ | Decisões D1–D12 | Mudam nomes, estrutura e API. |
| 2 ✅ | Fase 1 → Fase 2 → Fase 3 | Projeto instalável + testes + CI: rede de segurança antes de mexer no código. |
| 3 ✅ | Fase 4 → Fase 5 | Corrigir e otimizar com os testes garantindo a física. |
| 4 | Fase 6 (se quiser) | Novas funcionalidades sobre uma base estável. |
| 5 | Fase 7 → Fase 8 → Fase 9 | Tutoriais atualizados alimentam o site e o livro LaTeX. |
| 6 | Fase 10 → Fase 11 | O paper usa os benchmarks e os tutoriais; o acabamento fecha a versão 0.1.0. |

Cada fase vira um ou mais commits na branch `claude/vibrant-faraday-ucinuf`, com os testes passando antes de seguir para a próxima.

---

## 6. Referências usadas para a estrutura

- Projeto REPAQ (`qrng-ppe`, zip enviado): `pyproject.toml`, `tests/` com pytest, workflow de testes, Sphinx + Furo, `CITATION.cff`, READMEs por pasta.
- Scientific Python Library Development Guide — https://learn.scientific-python.org/development/
- Python Packaging User Guide (PyPA) — https://packaging.python.org/
- pyOpenSci Python Package Guide — https://www.pyopensci.org/python-package-guide/
- QuTiP (referência de API para simulação quântica em Python) — https://qutip.org/
- Journal of Open Source Software — https://joss.readthedocs.io/
