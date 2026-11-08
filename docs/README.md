# docs — documentação do Q-BASIC

Site gerado com [Sphinx](https://www.sphinx-doc.org/), tema
[Furo](https://pradyunsg.me/furo/) e [MyST-NB](https://myst-nb.readthedocs.io/) (páginas em
Markdown e notebooks). Publicado automaticamente no GitHub Pages a cada push na `main`
(`.github/workflows/docs.yml`).

## Gerar localmente

```bash
pip install -e ".[docs]"
make docs                         # ou: python -m sphinx -W --keep-going -b html docs/source docs/_build/html
```

Abra `docs/_build/html/index.html` no navegador.

## Organização

| Caminho | Conteúdo |
|---|---|
| `source/conf.py` | configuração; copia os tutoriais de `tutoriais/` na ordem de `tutoriais/indice.yml` |
| `source/index.md` | página inicial |
| `source/instalacao.md`, `source/guia_rapido.md` | primeiros passos |
| `source/guia/` | guia do usuário (páginas executadas ao gerar o site) |
| `source/api/` | referência gerada das docstrings (`automodule`) |
| `source/desenvolvimento/` | como contribuir e como publicar versões |
| `source/_static/` | logo, favicon, banner e CSS |

As páginas do guia têm `mystnb: execution_mode: force` no cabeçalho: o código delas é
executado a cada geração do site, então as saídas mostradas são sempre as da versão atual
da biblioteca. Os tutoriais usam as saídas salvas nos notebooks.

## Primeira publicação (uma vez só)

No GitHub, em **Settings → Pages → Build and deployment**, escolha **Source: GitHub
Actions**. Depois do próximo push na `main`, o site fica em
<https://gubiogl.github.io/Q-BASIC/>.
