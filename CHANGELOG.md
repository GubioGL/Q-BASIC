# Changelog

Todas as mudanças relevantes do Q-BASIC. O formato segue o
[Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e as versões seguem o
[versionamento semântico](https://semver.org/lang/pt-BR/).

## [0.1.0] — ainda não publicada

Reestruturação completa da biblioteca: pacote profissional, testes automáticos, núcleo
reescrito e mais rápido, e nomes sem acento. **O código escrito para a 0.0.x continua
funcionando** (com avisos de obsolescência; veja a tabela de migração abaixo).

### Adicionado

- Classe única `ObjQuantico` com dois formatos, `"denso"` (NumPy) e `"esparso"`
  (SciPy CSR), que podem ser misturados nas operações. Novos atributos e métodos:
  `formato`, `shape`, `dims` (subsistemas de sistemas compostos), `tipo`
  (`"ket"`, `"bra"`, `"operador"`), `para_denso()`, `para_esparso()`, `conj()`,
  `transposta()`, `eh_hermitiano()`, `autoestados(k=...)`, `norma()`, `normalizar()`,
  conversão para NumPy (`np.asarray(A)`) e indexação (`A[i, j]`).
- `resolver_schrodinger(H, psi0, tempos, observaveis)`, que devolve um `Resultado`
  (`tempos`, `vetores`, `estados`, `valores_esperados`). O método padrão (`"expm"`) é
  exato e trabalha direto com matrizes esparsas; os integradores do `solve_ivp`
  (`"RK45"`, `"DOP853"`...) continuam disponíveis.
- `valores_esperados(estados, observaveis)` e `valor_esperado` aceitando kets, bras,
  matrizes densidade, listas de kets, matrizes `(N, T)` e `Resultado`.
- `tensor(A, B, ...)` para o produto tensorial (o mesmo que `A @ B`).
- `ket("0110")` / `bra("0110")`: estados de vários qubits.
- `matriz_densidade(estados, probabilidades)`.
- Exibição em LaTeX no Jupyter (`_repr_latex_`), com matrizes grandes resumidas.
- Aritmética com escalares: `A + c` (= `A + c·I`), `c - A`, `-A`, `A / 1j`.
- Autovalores dos `k` menores níveis de operadores esparsos grandes
  (`A.autovalores(k=3)`), sem converter para denso.
- Pacote com `pyproject.toml`, testes (pytest, cobertura de 99 %), integração contínua
  no GitHub Actions, publicação automática no PyPI, exemplos e benchmarks.

### Alterado

- Dependências obrigatórias reduzidas a **NumPy e SciPy**. IPython e SymPy passaram para
  o extra `tutorial` (`pip install "Q-BASIC[tutorial]"`); PyTorch, para o extra `gpu`.
- `repr()`/`print()` mostram o objeto em texto (tipo, forma, formato e a matriz), sem
  depender do IPython.
- Autovalores agora vêm em ordem crescente; para operadores hermitianos são reais
  (calculados com `eigh`).
- `traco()` devolve `complex` quando o traço tem parte imaginária (antes era descartada).
- O solver antigo (`edo.solve`) usa tolerâncias `rtol=1e-8`, `atol=1e-10` por padrão.
- `coerente(..., metodo="outro")` gera `ValueError` (antes, `TypeError`).
- Pauli: o símbolo LaTeX passou de `\hat{\sigma_x}` para `\hat{\sigma}_x`.

### Corrigido

- O exemplo do README usava funções que não existiam (B1).
- `dim()` de um bra retornava 1 (B2).
- `AutoValor_Vetor()` (denso) retornava só os autovetores (B3).
- `repr` imprimia `<IPython.core.display.Math object>` fora do Jupyter e era lento (B4).
- `print("Aqui !")` esquecido no produto esparso (B5).
- `A + 1`, `A / 1j` e `-A` geravam `TypeError` (B6); `2 / A` fazia divisão elemento a
  elemento (B7); não era possível misturar denso e esparso (B8).
- `traço()` descartava a parte imaginária (B9); `dag()` perdia o LaTeX (B10).
- `ket('2')` só imprimia uma mensagem e retornava `None` (B11); `bases(2, 5)` dava
  `IndexError` ou, no formato esparso, um vetor nulo silencioso (B12).
- Solver: `t_span` como array quebrava (B13); a norma do estado não se conservava com as
  tolerâncias padrão (B14); o Hamiltoniano esparso era convertido para denso (B15);
  `edo` herdava de `ObjQuantico` sem motivo (B16).
- A instalação falhava por causa de `torch==2.5.1+cu118` (B17).
- `matrizdensidade` ignorava estados ou probabilidades sobrando (B19); o LaTeX de
  `ket`/`bra` perdia as chaves (B20).
- Estado coerente analítico gerava `nan` para mais de ~170 níveis (P7).

### Desempenho

Comparado com a 0.0.x (detalhes em `benchmarks/resultados.md`): valor esperado ao longo
do tempo ~20× mais rápido; solver com Hamiltoniano esparso ~25× (e
`resolver_schrodinger` ~150×); potências de operadores ~10×; `repr` ~100×.

### Obsoleto — guia de migração

Os nomes antigos continuam funcionando, mas emitem `DeprecationWarning` e serão
removidos numa versão futura.

| Antigo (0.0.x) | Novo (0.1.0) |
|---|---|
| `qb.destruiçao(N)` | `qb.destruicao(N)` |
| `qb.criaçao(N)` | `qb.criacao(N)` |
| `qb.Identidade(N)` | `qb.identidade(N)` |
| `qb.Fock(N, n)` | `qb.fock(N, n)` |
| `qb.matrizdensidade(probabilities, estados, puro)` | `qb.matriz_densidade(estados, probabilidades)` |
| `qb.ObjQuantico_esparso(dados)` | `qb.ObjQuantico(dados, formato="esparso")` |
| `qb.edo.solve(H, tempos, psi0)` | `qb.resolver_schrodinger(H, psi0, tempos, observaveis)` |
| `qb.Valor_esperado(estados, observaveis)` | `qb.valores_esperados(estados, observaveis)` |
| `A.traço()` | `A.traco()` |
| `A.Autovalores()` / `A.Autovetores()` | `A.autovalores()` / `A.autovetores()` |
| `A.AutoValor_Vetor()` | `A.autoestados()` |
| `A.expM()` | `A.expm()` |
| `import qbasic.class_tijolo` | `import qbasic.objeto` (ou `qb.ObjQuantico`) |
| `import qbasic.operador` | `import qbasic.operadores` |
| `import qbasic.funçoes` | `qbasic.dinamica` e `qbasic.medidas` |

Não mudaram: `ObjQuantico`, `bases`, `ket`, `bra`, `coerente`, `operador_x`,
`operador_p`, `pauliX`, `pauliY`, `pauliZ`, `valor_esperado`, o parâmetro `sparsa=True`
e as convenções `A * B` (produto matricial) e `A @ B` (produto tensorial).

## [0.0.3] — 2024-12-24

Primeira versão publicada no PyPI.
