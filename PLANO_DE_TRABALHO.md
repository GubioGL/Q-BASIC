# Plano de trabalho — reestruturação do Q-BASIC

> Documento de planejamento. **Nada foi alterado na biblioteca ainda.**
> Para executar, é só pedir pelo número: *"faça a Fase 1"*, *"faça os itens 4.1 a 4.5"*,
> *"responda D3 com a opção B"*. Vou marcando `[x]` conforme cada item for concluído.

Legenda: `[ ]` a fazer · `[x]` feito · `(opcional)` só se você quiser · **D#** = decisão sua.

---

## 1. Diagnóstico — o que existe hoje

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

| # | Onde | Problema | Efeito |
|---|---|---|---|
| B1 | `README.md:41-48` | O exemplo usa `estado_zero`, `estado_um` e `X`, que **não existem** no pacote. | Quem copia o exemplo recebe `ImportError`. |
| B2 | `class_tijolo.py:56` | `dim()` usa `len(dados)` → um **bra** de dimensão 4 retorna `1`. | Dimensão errada para bras/vetores-linha. |
| B3 | `class_tijolo.py:103-112` | `AutoValor_Vetor()` (denso) retorna **só os autovetores**, apesar do nome; a versão esparsa retorna os dois. | Comportamento diferente entre denso e esparso. |
| B4 | `class_tijolo.py:117-122` | `__repr__` chama `display()` do IPython e converte a matriz inteira para SymPy. | Fora do Jupyter imprime `<IPython...Math object>`; com matrizes grandes fica **muito lento**; IPython vira dependência obrigatória (e não está no `setup.py`). |
| B5 | `class_tijolo.py:263` | `print("Aqui !")` de depuração esquecido no `__mul__` esparso. | Polui a saída (aparece até ao criar estado coerente esparso). |
| B6 | `class_tijolo.py:140-172` | `+`/`-` não aceitam escalar; `/` não aceita número complexo nem escalar NumPy; não existe `-A` (`__neg__`) nem `__radd__`. | `H + 1`, `A / 1j`, `-A` dão `TypeError`. |
| B7 | `class_tijolo.py:168-172` | `2 / A` faz divisão **elemento a elemento** (gera `inf`). | Operação sem sentido físico (deveria ser erro ou inversa). |
| B8 | `class_tijolo.py` (geral) | Não dá para misturar denso com esparso (`A_denso * B_esparso` → `TypeError`). | Usuário tem de escolher um formato para tudo. |
| B9 | `class_tijolo.py:70-79` | `traço()` descarta a parte imaginária silenciosamente. | Traço de operador não-hermitiano fica errado. |
| B10 | `class_tijolo.py:58-68` | `dag()` perde a representação LaTeX. | Pequeno, mas inconsistente. |
| B11 | `estados.py:49-60, 77-88` | `ket('2')` só faz `print` e retorna `None`; `ket(1.5)` é aceito. | Erros silenciosos, aparecem depois em outro lugar. |
| B12 | `estados.py:21` | `bases(2, 5)` não valida `n < N` → `IndexError` genérico. | Mensagem de erro ruim. |
| B13 | `funçoes.py:16` | `if t_span == None` quebra quando `t_span` é array NumPy. | `ValueError` ao passar `t_span=np.array([0, 1])`. |
| B14 | `funçoes.py:13-31` | Tolerâncias padrão do RK45 (`rtol=1e-3`) → a norma do estado não se conserva: ⟨σz⟩ chegou a **1.00048** (> 1, fisicamente impossível). | Resultados de dinâmica imprecisos. |
| B15 | `funçoes.py:28` | O solver chama `.full()` no Hamiltoniano → **matriz esparsa vira densa**. | O modo esparso não traz ganho nenhum na dinâmica. |
| B16 | `funçoes.py:6` | `class edo(ObjQuantico)` herda de `ObjQuantico` sem motivo. | Design confuso. |
| B17 | `setup.py:10` | `torch==2.5.1+cu118` não existe no PyPI; `numpy`, `IPython` e `matplotlib` não estão listados; tudo fixado com `==`. | `pip install` **falha**. |
| B18 | `README.md` | Badge de licença aponta para `LICENSE` inexistente; `requirements.txt` inexistente; URL de clone é placeholder; e-mails diferentes no README e no `setup.py`. | Aparência pouco profissional. |

### 1.3 Problemas de performance (otimização)

| # | Onde | Hoje | Proposta |
|---|---|---|---|
| P1 | `funçoes.py:47-71` | `Valor_esperado` faz laço Python sobre cada instante de tempo. | Uma única chamada vetorizada (`np.einsum`) — ordens de grandeza mais rápido. |
| P2 | `class_tijolo.py:174-182` | `A**n` faz `n` multiplicações num laço. | `np.linalg.matrix_power` (exponenciação binária, `log n` produtos). |
| P3 | `class_tijolo.py:199` | Esparso guardado em **COO**, que precisa ser convertido a cada operação. | Guardar em **CSR** (formato certo para produtos e somas). |
| P4 | `class_tijolo.py:212, 227-233` | `dim()`, autovalores e `__repr__` do esparso convertem para denso. | Usar `shape`; `eigsh`/`eigh` quando possível. |
| P5 | `class_tijolo.py:81-101` | `eigvals`/`eig` genéricos. | `eigvalsh`/`eigh` para operadores hermitianos (mais rápidos e precisos). |
| P6 | `funçoes.py` | Só `solve_ivp`. | Para H independente do tempo: `expm_multiply` (exato e funciona com esparso). |
| P7 | `estados.py:136` | `factorial(n)` estoura para n > 170 e `alpha**n` pode estourar. | Calcular em log (`gammaln`) — estável para qualquer N. |

### 1.4 Problemas de organização

- Nomes com acento em arquivos e funções (`funçoes.py`, `destruiçao`, `criaçao`, `traço`, pastas `Tutorial_computação_quantica`, `Aula_0_introdução`) — funcionam no Python 3, mas dão problema em Windows, Sphinx, LaTeX, links e alguns terminais.
- Tutoriais com numeração inconsistente: `Aula_9` tem título "Aula 7", `Aula_11` diz "Aula 10", `Aula_12` e `EXTRA_numba` dizem "Aula 11", `EXTRA_Cupy` diz "Aula 10"; existem `Aula_1` e `Aula_1V2`; `Aula_12`, `EXTRA_numba` e `EXTRA_Cupy` estão praticamente vazias.
- Vários tutoriais importam **QuTiP**, que não é dependência do projeto.
- `Aula_9_Dinamica.ipynb` tem ~390 KB de saídas salvas.
- `Bra.png` solto na raiz.
- O README fala de um segundo pacote, **BRa**, que não está no repositório.
- Não há tipagem, docstrings em formato padronizado, linter nem formatação automática.

---

## 2. Decisões que preciso de você antes de começar

Coloquei minha recomendação em cada uma. Se você disser apenas *"siga as recomendações"*, uso todas.

- **D1 — Nomes com acento** (`destruiçao`, `traço`, `funçoes`...)
  - **A (recomendado):** passar para nomes sem acento (`destruicao`, `traco`, `funcoes`) e **manter os antigos como apelidos** com aviso de *deprecated* → nada que você já escreveu quebra.
  - B: manter tudo como está.
- **D2 — Significado dos operadores** (hoje `*` = produto matricial e `@` = produto tensorial)
  - **A (recomendado):** manter (assim os tutoriais continuam válidos) e adicionar a função explícita `tensor(A, B, ...)`.
  - B: seguir o padrão NumPy/QuTiP 5 (`@` = produto matricial) — quebra os tutoriais atuais.
- **D3 — Denso × esparso**
  - **A (recomendado):** **uma única classe** `ObjQuantico` com `formato="denso" | "esparso"`, que aceita misturar os dois; `ObjQuantico_esparso` continua existindo como apelido.
  - B: manter as duas classes separadas, só corrigindo bugs.
- **D4 — Pacote BRa** (citado no README): criar neste repositório, ou tirar do README por enquanto? *(recomendo tirar do README e deixar como item futuro)*
- **D5 — Backends PyTorch / CuPy / Numba:** implementar agora ou deixar no roadmap? *(recomendo deixar como dependência opcional e roadmap — o foco agora é qualidade do núcleo)*
- **D6 — Idioma da documentação HTML:** português, inglês ou os dois? *(recomendo português primeiro; a API já é em português)*
- **D7 — Paper:** qual o destino?
  - **A:** artigo didático em português para a **Revista Brasileira de Ensino de Física (RBEF)** — combina com o perfil do projeto.
  - **B:** artigo curto em inglês para o **Journal of Open Source Software (JOSS)** — dá DOI e é o padrão para citar software.
  - **C (recomendado):** preparar os dois na pasta `paper/` (RBEF em LaTeX + JOSS em `paper.md`).
  - Também preciso da **lista de autores e afiliações**.
- **D8 — Licença:** o README diz MIT. Confirma MIT? (vou criar o arquivo `LICENSE`)
- **D9 — Python mínimo:** recomendo **3.10+** (testado no CI em 3.10, 3.11, 3.12 e 3.13).
- **D10 — Layout do pacote:**
  - **A (recomendado):** layout `src/qbasic/` (padrão do Scientific Python / PyPA; garante que os testes rodem contra o pacote instalado).
  - B: manter `qbasic/` na raiz (como no REPAQ).
- **D11 — Publicação no PyPI:** quer um workflow que publique automaticamente ao criar uma *release* no GitHub? Qual nome no PyPI (`qbasic`, `q-basic`...)? *(precisa verificar se o nome está livre)*
- **D12 — E-mail/contato oficial** para README, `pyproject.toml` e `CITATION.cff` (hoje aparecem `gubio@ufscar.br` e `gubiofisikal@gmail.com`).

---

## 3. Estrutura alvo do repositório

Baseada no REPAQ (zip enviado) + guias da comunidade (Scientific Python Development Guide, PyPA, pyOpenSci):

```text
Q-BASIC/
├── .github/
│   ├── workflows/
│   │   ├── testes.yml           # pytest + lint em TODO push e pull request
│   │   ├── docs.yml             # gera o site HTML e publica no GitHub Pages
│   │   ├── tutorial-pdf.yml     # (opcional) gera o PDF do tutorial LaTeX
│   │   ├── paper.yml            # (opcional) compila o paper
│   │   └── publicar.yml         # (opcional) publica no PyPI ao criar release
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
├── pyproject.toml               # substitui o setup.py
├── Makefile                     # atalhos: make test, make docs, make tutorial, make paper
├── README.md, LICENSE, CITATION.cff, CHANGELOG.md, CONTRIBUTING.md
└── .gitignore, .pre-commit-config.yaml
```

---

## 4. Tarefas por fase

A ordem importa: **os testes vêm antes da refatoração**, para garantir que nada da física muda enquanto o código é reorganizado.

### Fase 1 — Base do projeto (empacotamento e organização)
- [ ] 1.1 Criar `pyproject.toml` (PEP 621) no lugar do `setup.py`, com dependências corretas e sem versões travadas com `==`: `numpy`, `scipy`, `sympy`, `matplotlib`.
- [ ] 1.2 Extras opcionais: `[test]` (pytest, pytest-cov), `[docs]` (sphinx...), `[tutorial]` (jupyter, nbconvert...), `[dev]` (ruff, pre-commit), `[gpu]` (torch/cupy — conforme D5). IPython deixa de ser obrigatório.
- [ ] 1.3 Mover para o layout escolhido em D10 (`src/qbasic/`), preservando o histórico com `git mv`.
- [ ] 1.4 Definir `__version__` (versão 0.1.0) e a API pública em `__init__.py` (`__all__`).
- [ ] 1.5 Criar `.gitignore` (Python, Jupyter, LaTeX, builds de docs).
- [ ] 1.6 Criar `LICENSE` (D8).
- [ ] 1.7 Mover `Bra.png` para `docs/source/_static/` e ajustar o README.
- [ ] 1.8 Mover `Testes/*.py` para `exemplos/` (são exemplos, não testes) e `testGPU.ipynb` para `benchmarks/`.
- [ ] 1.9 Configurar `ruff` (lint + formatação) e `pre-commit`.
- [ ] 1.10 `Makefile` com atalhos (`make install`, `make test`, `make lint`, `make docs`, `make tutorial`, `make paper`).

### Fase 2 — Testes unitários (pytest)
Testes baseados em **resultados físicos conhecidos**, que continuam válidos depois da refatoração:
- [ ] 2.1 `tests/conftest.py` com fixtures (tolerâncias, dimensões, estados comuns) e parametrização denso/esparso.
- [ ] 2.2 `test_objeto.py`: soma, subtração, produto por escalar, produto matricial, tensorial, `dag`, traço, potência, `expM`, autovalores, erros de tipo.
- [ ] 2.3 `test_operadores.py`: álgebra de Pauli (σx² = I, σxσy = iσz, anticomutadores), `a|n⟩ = √n|n−1⟩`, `a†|n⟩ = √(n+1)|n+1⟩`, `[a, a†] = I` (fora do último nível truncado), hermiticidade de X e P, `[x, p] = i`.
- [ ] 2.4 `test_estados.py`: normalização, ortogonalidade das bases, validação de entradas, estado coerente (⟨n⟩ = |α|², distribuição de Poisson, `a|α⟩ ≈ α|α⟩`), método "operador" = método "analítico".
- [ ] 2.5 `test_matriz_densidade.py`: traço 1, hermiticidade, positividade, pureza `Tr(ρ²)` (puro = 1, misto < 1).
- [ ] 2.6 `test_dinamica.py`: oscilação de Rabi contra a solução analítica, conservação da norma, Jaynes-Cummings (troca de excitação átomo↔cavidade), comparação com `expm`.
- [ ] 2.7 `test_esparso.py`: toda operação densa = mesma operação esparsa.
- [ ] 2.8 `test_compat.py`: nomes antigos continuam funcionando (D1).
- [ ] 2.9 Testes dos bugs B1–B16 (escritos antes da correção — falham agora, passam depois).
- [ ] 2.10 Meta de cobertura ≥ 90 % e `tests/README.md` explicando o que cada arquivo cobre (como no REPAQ).

### Fase 3 — GitHub Actions (CI)
- [ ] 3.1 `.github/workflows/testes.yml`: roda em **todo push (qualquer branch) e todo pull request**.
- [ ] 3.2 Matriz: Python 3.10, 3.11, 3.12, 3.13 no Ubuntu + um job no Windows (por causa dos acentos/caminhos).
- [ ] 3.3 Passos: instalar `.[test]`, rodar `ruff`, rodar `pytest --cov`, publicar relatório de cobertura como artefato.
- [ ] 3.4 Badge de status dos testes e de cobertura no README.
- [ ] 3.5 (opcional) Job que **executa os notebooks dos tutoriais** (`nbmake`) para garantir que continuam rodando.
- [ ] 3.6 (opcional) Dependabot para atualizar as versões das Actions.

### Fase 4 — Correção dos bugs (seção 1.2)
- [ ] 4.1 B1 — README com exemplo que funciona (e adicionar `estado_zero`/`estado_um` como atalhos, se fizer sentido).
- [ ] 4.2 B2 — `dim()` correto para kets, bras e operadores (e guardar `dims` de sistemas compostos, necessário para traço parcial).
- [ ] 4.3 B3, B5, B9, B10 — `AutoValor_Vetor`, print de depuração, traço complexo, LaTeX no `dag`.
- [ ] 4.4 B4 — trocar o `__repr__` com `display()` por `_repr_latex_` (o Jupyter renderiza sozinho; fora dele, imprime texto) e limitar o tamanho da matriz exibida.
- [ ] 4.5 B6, B7, B8 — aritmética completa e consistente (escalares complexos/NumPy, `-A`, `A + c·I`, mistura denso/esparso, mensagens de erro claras).
- [ ] 4.6 B11, B12 — validação de entradas com `ValueError` claro.
- [ ] 4.7 B13, B14, B15, B16 — solver: `t_span`, tolerâncias corretas (`rtol`/`atol` adequados), não densificar matrizes esparsas.
- [ ] 4.8 B17, B18 — dependências e README (resolvidos junto com a Fase 1 e a Fase 10).

### Fase 5 — Otimização e reorganização do núcleo
- [ ] 5.1 Classe base única `ObjQuantico` com formato denso/esparso (D3), sem código duplicado.
- [ ] 5.2 Esparso em CSR; conversões só quando necessário (P3, P4).
- [ ] 5.3 `matrix_power`, `eigh`/`eigvalsh` para hermitianos, `expm_multiply` (P2, P5, P6).
- [ ] 5.4 Valor esperado vetorizado (P1).
- [ ] 5.5 Estado coerente analítico numericamente estável (P7).
- [ ] 5.6 Solver novo com interface mais clara, ex.: `resolver_schrodinger(H, psi0, tempos, observaveis=[...])` devolvendo um objeto `Resultado` (`.tempos`, `.estados`, `.valores_esperados`); `edo.solve` antigo continua funcionando.
- [ ] 5.7 Nomes sem acento + apelidos antigos com aviso (D1); função `tensor()` (D2).
- [ ] 5.8 Type hints e docstrings no padrão NumPy em todas as funções públicas (vão direto para a documentação HTML).
- [ ] 5.9 `benchmarks/`: medir antes × depois (denso vs. esparso, tempo do solver, valor esperado) — esses números entram no paper.

### Fase 6 — Funcionalidades novas (opcional, você escolhe quais)
- [ ] 6.1 `tensor()`, `comutador()`, `anticomutador()`.
- [ ] 6.2 Traço parcial, fidelidade, entropia de von Neumann, pureza.
- [ ] 6.3 Portas quânticas (H, S, T, CNOT, rotações) e estados de n qubits — ponte com o tutorial de computação quântica.
- [ ] 6.4 Equação mestra de Lindblad (sistemas abertos, matriz densidade).
- [ ] 6.5 Funções de visualização (esfera de Bloch, distribuição de Fock, função de Wigner).
- [ ] 6.6 Backends GPU (PyTorch/CuPy) — conforme D5.

### Fase 7 — Tutoriais
- [ ] 7.1 Renomear e numerar sem acento (`tutoriais/simulador/00_introducao.ipynb`, ...); corrigir os títulos internos ("Aula 7" dentro da `Aula_9`, etc.).
- [ ] 7.2 Decidir o que fazer com `Aula_1` × `Aula_1V2` (juntar) e com os notebooks quase vazios (`Aula_12`, `EXTRA_numba`, `EXTRA_Cupy`): completar ou mover para "em construção".
- [ ] 7.3 Criar `tutoriais/indice.yml` (ordem, título e parte de cada capítulo) — usado pelos docs e pelo script LaTeX.
- [ ] 7.4 Atualizar os notebooks para a API nova (sem quebrar a didática "construindo a classe do zero").
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
- [ ] 11.1 README novo: badges (testes, cobertura, docs, Python, licença), instalação real, exemplo que funciona, links para docs/tutoriais/paper, como citar.
- [ ] 11.2 `CITATION.cff` (botão "Cite this repository" do GitHub).
- [ ] 11.3 `CHANGELOG.md` (começando na 0.1.0) e `CONTRIBUTING.md` (como rodar testes, estilo de código, como abrir PR).
- [ ] 11.4 Modelos de issue e de pull request.
- [ ] 11.5 (opcional) `publicar.yml`: publica no PyPI ao criar release (*Trusted Publishing*, sem senha no repositório) — D11.
- [ ] 11.6 (opcional, você faz no site) ligar o repositório ao **Zenodo** para ter DOI a cada release.
- [ ] 11.7 Apagar este `PLANO_DE_TRABALHO.md` (ou movê-lo para `docs/`) quando tudo estiver concluído.

---

## 5. Ordem sugerida de execução

| Etapa | Fases | Por quê |
|---|---|---|
| 1 | Decisões D1–D12 | Mudam nomes, estrutura e API. |
| 2 | Fase 1 → Fase 2 → Fase 3 | Projeto instalável + testes + CI: rede de segurança antes de mexer no código. |
| 3 | Fase 4 → Fase 5 | Corrigir e otimizar com os testes garantindo a física. |
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
