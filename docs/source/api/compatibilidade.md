# Nomes antigos (compatibilidade)

A versão 0.1.0 passou a usar nomes sem acento e em minúsculas. Os nomes da versão 0.0.x
continuam funcionando, mas emitem um `DeprecationWarning` com o nome novo e serão
removidos numa versão futura.

| Antigo (0.0.x) | Novo (0.1.0) |
|---|---|
| `qb.destruiçao(N)` | {func}`qb.destruicao(N) <qbasic.destruicao>` |
| `qb.criaçao(N)` | {func}`qb.criacao(N) <qbasic.criacao>` |
| `qb.Identidade(N)` | {func}`qb.identidade(N) <qbasic.identidade>` |
| `qb.Fock(N, n)` | {func}`qb.fock(N, n) <qbasic.fock>` |
| `qb.matrizdensidade(probabilities, estados, puro)` | {func}`qb.matriz_densidade(estados, probabilidades) <qbasic.matriz_densidade>` |
| `qb.ObjQuantico_esparso(dados)` | `qb.ObjQuantico(dados, formato="esparso")` |
| `qb.edo.solve(H, tempos, psi0)` | {func}`qb.resolver_schrodinger(H, psi0, tempos, observaveis) <qbasic.resolver_schrodinger>` |
| `qb.Valor_esperado(estados, observaveis)` | {func}`qb.valores_esperados(estados, observaveis) <qbasic.valores_esperados>` |
| `A.traço()` | `A.traco()` |
| `A.Autovalores()`, `A.Autovetores()` | `A.autovalores()`, `A.autovetores()` |
| `A.AutoValor_Vetor()` | `A.autoestados()` |
| `A.expM()` | `A.expm()` |
| módulo `qbasic.class_tijolo` | {mod}`qbasic.objeto` |
| módulo `qbasic.operador` | {mod}`qbasic.operadores` |
| módulo `qbasic.funçoes` | {mod}`qbasic.dinamica` e {mod}`qbasic.medidas` |

Para encontrar usos antigos no seu código, rode o Python com os avisos ligados:

```bash
python -W error::DeprecationWarning meu_script.py
```
