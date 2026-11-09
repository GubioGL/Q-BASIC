# paper — artigo científico sobre o Q-BASIC

Duas versões do mesmo trabalho:

| Pasta | Versão | Formato |
|---|---|---|
| [`artigo/`](artigo/) | Artigo completo em **português**, pensado para uma revista de ensino de física (como a *Revista Brasileira de Ensino de Física*). | LaTeX (`main.tex`) + BibTeX (`referencias.bib`) |
| [`joss/`](joss/) | Versão curta em **inglês** para o [*Journal of Open Source Software*](https://joss.theoj.org/) (JOSS). | Markdown (`paper.md`) + BibTeX (`paper.bib`) |

Autor: Gubio Gomes de Lima.

## Figuras e números reprodutíveis

Todas as figuras e os números citados no artigo são gerados pela própria biblioteca:

```bash
pip install -e ".[plot]"
python paper/gerar_figuras.py
```

O script grava em [`figuras/`](figuras/):

- as figuras em PDF;
- a tabela de desempenho, lida de `benchmarks/resultados.json`;
- `valores.tex`, com os erros e os tempos citados no texto (macros como `\ErroExpm`).

Grava também, em `joss/figura_qbasic.png`, a figura da versão para o JOSS.

Para atualizar as medições de desempenho antes de regenerar as figuras:

```bash
make bench        # gera benchmarks/resultados.md e benchmarks/resultados.json
```

## Compilar

```bash
make artigo                               # figuras + PDF do artigo em português
cd paper/artigo && latexmk -pdf main.tex  # só o PDF (pdfLaTeX + BibTeX)
```

O workflow **Artigo** do GitHub Actions compila as duas versões a cada mudança em
`paper/` e deixa os PDFs nos *Artifacts* da execução. A versão do JOSS usa a ferramenta
oficial de rascunhos da revista (`openjournals-draft-action`).

## Antes de submeter

- [ ] Preencher a **afiliação** do autor (marcada com `TODO` em `artigo/main.tex` e em
      `joss/paper.md`).
- [ ] Escrever os **agradecimentos** (e o financiamento, se houver).
- [ ] Revista em português: aplicar o modelo da revista escolhida (o texto usa a classe
      `article` padrão justamente para facilitar essa troca).
- [ ] JOSS: o repositório precisa estar público, ter licença OSI (MIT ✓), documentação
      (✓), testes (✓) e uma versão publicada (release + DOI, por exemplo pelo Zenodo).
