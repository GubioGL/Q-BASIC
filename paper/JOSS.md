# Guia para submeter o Q-BASIC ao JOSS

Este guia resume o que o [*Journal of Open Source Software*](https://joss.theoj.org/) (JOSS)
exige, compara com o estado atual do repositório e lista o que falta fazer antes da
submissão. O rascunho do artigo está em [`joss/paper.md`](joss/paper.md).

> Fontes: documentação oficial do JOSS (`paper.md`, `submitting.md`,
> `review_criteria.md` e `review_checklist.md` em
> [github.com/openjournals/joss](https://github.com/openjournals/joss/tree/main/docs)),
> consultada em novembro de 2026. As regras mudam; confira de novo antes de submeter.

## 1. A ideia do projeto: livro + biblioteca

| Produto | O que é | Onde publicar |
|---|---|---|
| **Livro** (`tutoriais/` → `tutorial_latex/`) | Curso que ensina a construir, do zero, um simulador quântico, para aprender física quântica, sistemas quânticos e computação quântica. | Livro/apostila próprio; candidato natural ao **JOSE** (seção 9). |
| **Biblioteca** (`src/qbasic/`) | O produto final das aulas: o simulador pronto, testado e documentado. | **Artigo no JOSS** (este guia). |

O artigo do JOSS é sobre o **software**, não sobre o curso nem sobre resultados de
física. O curso entra no artigo como contexto e como parte da justificativa.

## 2. O que o artigo precisa ter

Entre **750 e 1750 palavras**. O rascunho atual tem cerca de 1650, contando os marcadores
TODO. Ao preencher o impacto, encurte outras seções (por exemplo, o exemplo do gato ou o
*Software design*) para continuar abaixo de 1750.

| Seção (obrigatória) | O que a revista pede | No `paper.md` |
|---|---|---|
| **Metadados** | Título, autores com ORCID, afiliações, data ("9 November 2026"), `paper.bib`. | ⚠️ falta ORCID e afiliação (TODO) |
| **Summary** | Para um público **não especialista**: o que o software faz e para quê. | ✅ |
| **Statement of need** | Que problema resolve, **para quem** (público-alvo) e relação com outros trabalhos. | ✅ |
| **State of the field** | Comparação com pacotes usados na área e justificativa **"build vs. contribute"**: por que criar um software novo em vez de contribuir com QuTiP, QuantumOptics.jl ou Qiskit. | ✅ (legibilidade, curso que vira a biblioteca, idioma; reutiliza o SciPy) |
| **Software design** | Trade-offs, arquitetura escolhida e **por que** importa. Não basta descrever pastas. | ✅ (classe única densa/esparsa, notação `*`/`@`, expm × Runge-Kutta, Liouvilliano, portas por permutação, compatibilidade) |
| **Research impact statement** | Evidência **concreta**: publicações, uso externo, integrações; ou significância próxima (benchmarks, materiais reprodutíveis, sinais da comunidade). **Promessas de uso futuro não valem.** | ❌ **falta o principal** (TODO): uso em pesquisa |
| **AI usage disclosure** | Ferramentas/modelos **e versões**, onde foram usados, natureza e escopo, e confirmação de revisão humana. | ⚠️ falta o modelo/versão (TODO); confirmar a revisão |
| **Acknowledgements** | Agradecimentos e **todo apoio financeiro**. | ⚠️ TODO |
| **References** | Lista completa, com nomes completos das revistas, incluindo os softwares relacionados. | ✅ 19 referências conferidas |

Também é pedido que o artigo mencione projetos de pesquisa e publicações que usaram o
software. **Não** deve trazer documentação da API (essa fica no site).

## 3. Os quatro "portões" da pré-avaliação

Antes da revisão, os editores filtram as submissões. Falhar em **qualquer** item gera
rejeição imediata (*desk rejection*), que pode ser um "ainda não": dá para corrigir e
reenviar depois de seis meses ou mais.

| Portão | Exigência do JOSS | Situação do Q-BASIC |
|---|---|---|
| **1. Histórico público** | Repositório público há **mais de 6 meses**, com desenvolvimento ativo nesse período. "Um *dump* de repositório não é um histórico"; a distribuição dos commits é verificada automaticamente. | ⚠️ Há commits desde janeiro de 2024 (2024-01, 2024-11/12, 2025-02/03, 2025-07/08), mas há um intervalo de cerca de 15 meses (agosto de 2025 a novembro de 2026), e quase toda a versão 0.1.0 entrou em **dois dias** (8 e 9 de novembro de 2026). Confirme desde quando o repositório é público. |
| **2. Impacto em pesquisa** | **Precisa haver evidência de uso em pesquisa**, no mínimo pelo próprio autor: artigos ou preprints que usaram o software, adoção por outros grupos, uso em fluxos de pesquisa. | ❌ Nenhuma evidência registrada ainda. **É o ponto mais importante.** |
| **3. Boas práticas** | Para autor único, **vários** indicadores: histórico de commits ao longo do tempo, releases com tag ou CHANGELOG, testes e CI, documentação, arquivo CONTRIBUTING e regras de suporte/governança. | ⚠️ Há licença MIT, testes (98% de cobertura), CI, documentação, CHANGELOG e CITATION.cff. Faltam CONTRIBUTING, código de conduta, canal de suporte, releases com tag no GitHub (só há a 0.0.3 no PyPI) e o site no ar (ativar o GitHub Pages). |
| **4. Desenvolvimento iterativo** | O histórico deve mostrar refinamento ao longo do tempo, não uma rajada de commits. | ⚠️ Mesmo problema do portão 1: a reestruturação foi uma rajada. |

**Sinal positivo (não obrigatório, mas pesa):** issues, PRs ou discussões de pessoas de
fora. Hoje o repositório tem 0 issues e 1 PR (o da reestruturação).

## 4. Como justificar o artigo

O JOSS publica **software de pesquisa**. "É didático" sozinho não basta: notebooks não
estão no escopo, e o JOSS não publica artigos "para anunciar software que ainda não é
usado em pesquisa". O argumento do artigo precisa ter três partes.

1. **Necessidade real.** Problemas de sistemas quânticos pequenos (átomo + cavidade,
   poucos qubits, oscilador amortecido) aparecem o tempo todo em iniciação científica,
   TCCs, dissertações e na checagem de contas analíticas. Esses problemas pedem código
   **confiável e legível**, não código de alto desempenho.
2. **Por que não contribuir com o QuTiP.** A contribuição é o próprio código como objeto
   de estudo: pequeno (cerca de 2300 linhas), legível, escrito na mesma ordem do curso e
   em português. Isso não cabe dentro de um pacote grande em inglês. Mesmo assim, o
   Q-BASIC **reutiliza** o ecossistema (SciPy, comparação com o QuTiP), algo que o JOSS
   valoriza explicitamente.
3. **Evidência, não promessa.** É aqui que o artigo ainda é fraco. Exemplos de evidência
   aceita, do mais forte para o mais fraco:
   - artigos, preprints, dissertações ou teses (suas ou de alunos) com resultados obtidos
     com o Q-BASIC; cite-os no `paper.bib`;
   - outros grupos, professores ou alunos usando a biblioteca (com nomes ou links);
   - disciplinas e minicursos em que o curso foi aplicado (instituição, semestre, número
     de alunos);
   - apresentações em eventos (Encontro de Física, eventos da SBF, Python Brasil...);
   - benchmarks e materiais reprodutíveis. Esses o Q-BASIC já tem: 821 testes, todos os
     notebooks executados no CI e ganhos de 26× e 177× medidos sobre a versão 0.0.x.

   Sem pelo menos um item dos três primeiros, o portão 2 provavelmente não passa.

## 5. O que investir antes de submeter

### Agora (Fase 11 do plano)

- [ ] Ativar o **GitHub Pages** (Settings → Pages → Source: GitHub Actions).
- [ ] Configurar o *trusted publisher* no PyPI e publicar a **v0.1.0** com **tag e
      release** no GitHub. O livro em PDF é anexado automaticamente.
- [ ] Ligar o repositório ao **Zenodo**, para que cada release ganhe um DOI. O DOI é
      exigido no aceite.
- [ ] Criar um **ORCID** e definir a **afiliação**.
- [ ] Criar o `CONTRIBUTING.md` (como contribuir, rodar os testes e abrir PRs), o
      `CODE_OF_CONDUCT.md`, uma seção de **suporte** (onde pedir ajuda: issues,
      Discussions, e-mail) e uma frase de **governança** (quem decide e como).
- [ ] Criar modelos de issue (bug, nova funcionalidade, dúvida) e ativar o
      **Discussions**.
- [ ] Opcional: um `.mailmap` que una as identidades do git (Masterchief-Gamer,
      Breniak-Desktop, Quantum Master Chief → Gubio Gomes de Lima), **se** forem todas
      você. Assim o histórico mostra o mesmo autor de 2024 a 2026.

### Nos próximos 6 meses ou mais (o que convence os editores)

- [ ] **Usar o Q-BASIC na sua pesquisa** e publicar, nem que seja um preprint no arXiv,
      citando a biblioteca. Esse é o item que mais pesa.
- [ ] **Aplicar o curso**: disciplina, minicurso ou grupo de estudos. Registre a
      instituição, as datas e o número de alunos.
- [ ] Desenvolver **em público e aos poucos**: abrir issues para o roadmap (por exemplo,
      Hamiltonianos dependentes do tempo, trajetórias quânticas, mais portas e
      algoritmos), resolver via PRs e lançar versões pequenas e frequentes (0.1.1,
      0.2.0...) com CHANGELOG.
- [ ] Atrair **usuários externos**: divulgar o livro e a biblioteca para alunos e
      colegas; pedir que abram issues quando encontrarem problemas.
- [ ] Pedir a **um colega que instale e teste** a biblioteca do zero. O JOSS recomenda
      isso para software novo.
- [ ] Coautoria: se alunos ou colegas contribuíram de verdade (código, testes, uso no
      curso), avalie incluí-los. O JOSS vê a lista de autores como sinal de trabalho
      colaborativo. Contribuição só financeira não conta.

**Data realista para submeter:** só depois de pelo menos seis meses de desenvolvimento
público contínuo após a reestruturação (por volta de **maio de 2027** ou depois) e com
evidência concreta de uso em pesquisa.

## 6. Declaração de uso de IA

O JOSS permite IA, mas exige uma declaração completa. Omitir ou ser vago é tratado como
**falta ética** e pode levar a rejeição ou retratação.

- **O que declarar:** a ferramenta e o modelo **com versão** (preencha o TODO no
  `paper.md`), onde a IA foi usada (código, testes, documentação, tutoriais, livro,
  artigo) e de que forma (geração de código, refatoração, testes, redação).
- **O que você precisa afirmar (e cumprir):** que **revisou, editou e validou** tudo o
  que foi gerado com IA e que **tomou as decisões centrais de design**. Antes de
  submeter, leia o código da versão 0.1.0, rode os testes e os notebooks e ajuste o que
  não concordar. O texto atual diz que isso foi feito: mantenha-o só se for verdade.
- Os commits feitos com IA estão marcados como coautoria no histórico do git. A
  declaração deve ser coerente com isso.
- Na conversa com editores e revisores, a IA **não** pode ser usada, exceto para
  tradução.

## 7. Checklist que os revisores vão preencher

| Item | Situação |
|---|---|
| Conflito de interesse e código de conduta (do revisor) | — |
| Repositório com o código | ✅ |
| Licença OSI em texto puro (`LICENSE`) | ✅ MIT |
| Autoria: o autor é contribuidor principal; a lista de autores é completa | ✅ (avaliar coautores) |
| Escopo e significância (impacto em pesquisa) | ❌ falta evidência |
| Linha do tempo: desenvolvimento por 6 meses ou mais, não rajada recente | ⚠️ |
| Desenvolvimento aberto: releases, issues e PRs públicos | ⚠️ sem releases no GitHub e sem issues |
| Esforço colaborativo | ⚠️ autor único; compensar no artigo com o uso por outras pessoas |
| Boas práticas (licença, docs, testes, releases, caminhos de contribuição) | ⚠️ faltam CONTRIBUTING, suporte e releases |
| Instalação como documentada (`pip install`) | ✅ (publicar a 0.1.0 no PyPI) |
| Funcionalidade confirmada | ✅ testes e notebooks |
| Desempenho: as alegações podem ser reproduzidas | ✅ `benchmarks/comparar_versoes.py` |
| Declaração de necessidade na documentação | ✅ (reforçar no README) |
| Dependências listadas e instalação automática | ✅ `pyproject.toml` |
| Exemplos de uso | ✅ guia, tutoriais e `exemplos/` |
| Documentação da API | ✅ site Sphinx |
| Testes automatizados | ✅ 821 testes + CI |
| Diretrizes da comunidade: contribuir, relatar problemas, pedir suporte | ❌ falta |
| Seções do artigo (Summary … AI disclosure) | ✅ escritas; ❌ impacto em pesquisa e TODOs |
| Qualidade do texto e referências | ✅ (revisar após preencher os TODOs) |

## 8. Como compilar o artigo

- No GitHub: o workflow **Artigo** refaz a figura com a biblioteca e gera o PDF com a
  ferramenta oficial do JOSS a cada mudança em `paper/`. O PDF fica nos *Artifacts* da
  execução.
- Localmente, com Docker: `make artigo`.

## 9. E o livro? Considere o JOSE

O [*Journal of Open Source Education*](https://jose.theoj.org/) (JOSE), revista irmã do
JOSS, publica **módulos de aprendizagem computacionais** (recursos educacionais abertos)
e **software educacional**. O livro que ensina a construir o simulador se encaixa nesse
perfil, e a exigência central do JOSS (impacto em pesquisa) não é o foco ali. O artigo do
JOSE é curto (cerca de 1000 palavras) e escrito para não especialistas.

Caminho sugerido:

1. **JOSE**, para o curso/livro, depois de aplicá-lo pelo menos uma vez com alunos (a
   experiência de uso é um argumento forte);
2. **JOSS**, para a biblioteca, quando houver uso em pesquisa e histórico suficiente.

Antes de submeter aos dois, confira as regras atuais do JOSE para módulos de
aprendizagem e pergunte aos editores se os dois artigos podem coexistir. São
contribuições diferentes (curso × software), mas o material se sobrepõe.
