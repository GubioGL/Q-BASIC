| Caso | Antes (`e61545c`) | Depois (v0.1.0) | Ganho |
|---|---:|---:|---:|
| Valor esperado de a†a em 2000 instantes (N = 200) | 100.16 ms | 5.28 ms | 19.0× |
| Potência x**64 de um operador denso 200×200 | 7.62 ms | 0.81 ms | 9.4× |
| Montar o Hamiltoniano de Jaynes-Cummings esparso (N = 2000) | 2.22 ms | 1.36 ms | 1.6× |
| edo.solve, Jaynes-Cummings esparso (dimensão 400, α = 8, rtol=1e-8) | 14,586.31 ms | 544.48 ms | 26.8× |
| Estado coerente pelo método analítico (N = 150) | 0.04 ms | 0.02 ms | 2.2× |
| repr() de um operador 40×40 (exibição) | 14.20 ms | 0.10 ms | 139.0× |
| resolver_schrodinger (expm, exato), mesmo sistema de solver_esparso | não existe | 80.48 ms | — |

Python 3.13.18, NumPy 2.5.4, SciPy 1.18.1, Linux-6.18.44-fc-v310-x86_64-with-glibc2.39. Menor tempo de 3 repetições.
