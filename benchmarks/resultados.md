| Caso | Antes (`e61545c`) | Depois (v0.1.0) | Ganho |
|---|---:|---:|---:|
| Valor esperado de a†a em 2000 instantes (N = 200) | 160.98 ms | 10.45 ms | 15.4× |
| Potência x**64 de um operador denso 200×200 | 10.75 ms | 1.41 ms | 7.6× |
| Montar o Hamiltoniano de Jaynes-Cummings esparso (N = 2000) | 3.10 ms | 1.97 ms | 1.6× |
| edo.solve, Jaynes-Cummings esparso (dimensão 400, α = 8, rtol=1e-8) | 18,472.50 ms | 703.71 ms | 26.3× |
| Estado coerente pelo método analítico (N = 150) | 0.03 ms | 0.02 ms | 1.3× |
| repr() de um operador 40×40 (exibição) | 10.68 ms | 0.13 ms | 81.8× |
| resolver_schrodinger (expm, exato), mesmo sistema de solver_esparso | não existe | 104.34 ms | — |

Python 3.13.18, NumPy 2.5.4, SciPy 1.18.1, Linux-6.18.44-fc-v310-x86_64-with-glibc2.39. Menor tempo de 3 repetições.
