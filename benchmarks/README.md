# benchmarks — medições de desempenho

Medições de tempo do Q-BASIC. Os resultados alimentam a seção de desempenho do artigo
(pasta `paper/`).

| Arquivo | O que faz |
|---|---|
| [`bench_nucleo.py`](bench_nucleo.py) | Mede operações do núcleo (valor esperado, potência, Hamiltoniano esparso, solver, estado coerente, `repr`). Usa só a API comum às versões 0.0.x e 0.1.x. |
| [`comparar_versoes.py`](comparar_versoes.py) | Roda `bench_nucleo.py` com uma versão antiga (extraída de um commit) e com a atual, e gera a tabela de antes × depois. |
| [`resultados.md`](resultados.md) | Última tabela gerada. |
| [`resultados.json`](resultados.json) | As mesmas medições em JSON (usadas nas figuras e na tabela do artigo). |
| [`teste_gpu_pytorch.ipynb`](teste_gpu_pytorch.ipynb) | Teste exploratório de multiplicação de matrizes com PyTorch na CPU e na GPU. |

## Como rodar

```bash
pip install -e ".[dev]" ipython sympy     # ipython e sympy: só para rodar a versão antiga
python benchmarks/bench_nucleo.py         # versão atual
python benchmarks/comparar_versoes.py --saida benchmarks/resultados.md --json benchmarks/resultados.json
```

## Resultados da reestruturação (0.0.x → 0.1.0)

Ver a tabela completa em [`resultados.md`](resultados.md). Os principais ganhos vêm de:

- **valor esperado vetorizado** (`np.einsum` em vez de um laço Python por instante): ~20×;
- **solver sem densificar o Hamiltoniano esparso** (o antigo chamava `H.full()`): ~25× com
  as mesmas tolerâncias, e o novo `resolver_schrodinger` (evolução exata com
  `expm_multiply`) é ~150× mais rápido que o solver antigo no mesmo sistema;
- **potência por exponenciação binária** (`matrix_power`): ~10×;
- **`repr` sem SymPy/IPython**: ~100×.

### Por que `expm` é o método padrão do solver

Para Hamiltonianos independentes do tempo, `resolver_schrodinger(..., metodo="expm")`
calcula exp(−iHt)|ψ₀⟩ com `scipy.sparse.linalg.expm_multiply`: o erro fica
na precisão de máquina (~1e-13), contra ~1e-7 dos integradores RK com `rtol=1e-8`. Nos
testes com estados que ocupam muitos níveis (estado coerente, evolução livre) ele foi tão
rápido ou mais rápido que `RK45`/`DOP853`. Os integradores só ganham quando o estado vive
num subespaço pequeno (por exemplo, uma única excitação no Jaynes-Cummings) — nesses
casos, use `metodo="DOP853"`.
