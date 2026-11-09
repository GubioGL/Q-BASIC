# tutorial_latex — os tutoriais como livro (LaTeX/PDF)

O script [`scripts/gerar_tutorial_latex.py`](../scripts/gerar_tutorial_latex.py) transforma
os notebooks de [`tutoriais/`](../tutoriais/) num livro: **"Simulação e computação quântica
com o Q-BASIC"**. A ordem e os títulos dos capítulos vêm de
[`tutoriais/indice.yml`](../tutoriais/indice.yml), então o livro, o site e os notebooks
ficam sempre iguais.

## Como gerar

```bash
pip install -e ".[livro]"                        # inclui o pandoc (pypandoc_binary)
python scripts/gerar_tutorial_latex.py           # gera tutorial_latex/build/tutorial.tex
python scripts/gerar_tutorial_latex.py --pdf     # também compila o PDF
make livro                                       # atalho para a linha acima
```

O PDF precisa de uma distribuição LaTeX com **XeLaTeX** e **latexmk**, e das fontes
**DejaVu**. No Ubuntu/Debian:

```bash
sudo apt-get install texlive-xetex texlive-latex-recommended texlive-latex-extra \
  texlive-lang-portuguese texlive-fonts-recommended texlive-science latexmk lmodern \
  fonts-dejavu-core fonts-dejavu-extra
```

No Windows e no macOS, o MiKTeX ou o MacTeX servem.

O PDF também é gerado automaticamente no GitHub Actions (workflow **Livro dos
tutoriais**): baixe-o em *Actions → Livro dos tutoriais → Artifacts*. Em cada release ele é
anexado aos arquivos da versão.

## Como funciona

1. Cada notebook vira um capítulo. A primeira célula, com o título, é trocada pelo título
   do índice.
2. As células de Markdown passam por ajustes para o pandoc:
   - `\begin{equation}` vira `$$...$$`;
   - `$ x $` (com espaços, aceito pelo MathJax) vira `$x$`;
   - os títulos descem um nível: no livro, `#` é a parte e `##` é o capítulo.
3. As células de código ganham destaque de sintaxe. As saídas são tratadas assim:
   - texto: num bloco com uma barra cinza à esquerda;
   - erros propositais: em vermelho;
   - matrizes exibidas em LaTeX: como equações, reduzidas se forem largas;
   - gráficos: salvos em `build/figuras/`.
4. O pandoc converte tudo para LaTeX com o modelo de [`modelo/`](modelo/), e o XeLaTeX gera
   o PDF.

| Arquivo | Conteúdo |
|---|---|
| `modelo/metadados.yml` | classe do documento, fontes, margens, idioma, sumário |
| `modelo/preambulo.tex` | pacotes e estilos (notação de Dirac, blocos de código e de saída, cabeçalho) |
| `modelo/capa.tex` | capa (versão e data preenchidas pelo script) |
| `modelo/prefacio.md` | prefácio |
| `build/` | saída gerada (`tutorial.md`, `tutorial.tex`, `figuras/`, `tutorial.pdf`); fora do git |

Para mudar o conteúdo do livro, edite os notebooks; para mudar a aparência, edite os
arquivos de `modelo/`.
