"""Configuração do Sphinx para a documentação do Q-BASIC.

Gerar o site:  make docs   (ou: python -m sphinx -b html docs/source docs/_build/html)
"""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml

import qbasic

RAIZ = Path(__file__).resolve().parents[2]
FONTE = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Projeto
# ---------------------------------------------------------------------------
project = "Q-BASIC"
author = "Gubio Gomes de Lima"
copyright = "2024–2026, Gubio Gomes de Lima"
release = qbasic.__version__
version = ".".join(release.split(".")[:2])
language = "pt_BR"

# ---------------------------------------------------------------------------
# Extensões
# ---------------------------------------------------------------------------
extensions = [
    "myst_nb",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.mathjax",
    "sphinx_copybutton",
    "sphinx_design",
]

# Docstrings no padrão NumPy
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_rtype = False
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_typehints_format = "short"
autodoc_default_options = {
    "members": True,
    "show-inheritance": False,
    # Nomes antigos (obsoletos) ficam fora da referência; ver a página de compatibilidade.
    "exclude-members": "traço, Autovalores, Autovetores, AutoValor_Vetor, expM",
}

# MyST (Markdown) e MyST-NB (notebooks)
myst_enable_extensions = ["colon_fence", "dollarmath", "amsmath", "deflist", "fieldlist"]
myst_heading_anchors = 3
# Os tutoriais usam as saídas salvas; as páginas do guia são executadas na hora
# (elas pedem isso no próprio cabeçalho, com "mystnb: execution_mode: force").
nb_execution_mode = "off"
nb_execution_timeout = 300
nb_execution_raise_on_error = True
nb_merge_streams = True

# Notação de Dirac no MathJax
mathjax3_config = {
    "tex": {
        "macros": {
            "ket": [r"\left|#1\right\rangle", 1],
            "bra": [r"\left\langle#1\right|", 1],
            "braket": [r"\left\langle#1\middle|#2\right\rangle", 2],
        }
    }
}

copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
copybutton_exclude = ".linenos, .gp, .go"

templates_path = ["_templates"]
exclude_patterns = ["_build", "**.ipynb_checkpoints"]
# Os notebooks antigos pulam níveis de título (# e depois ###); isso não é um erro aqui.
suppress_warnings = ["myst.header"]

# ---------------------------------------------------------------------------
# HTML (tema Furo)
# ---------------------------------------------------------------------------
html_theme = "furo"
html_title = f"Q-BASIC {release}"
html_logo = "_static/logo_qbasic.png"
html_favicon = "_static/favicon.png"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_theme_options = {
    "source_repository": "https://github.com/GubioGL/Q-BASIC/",
    "source_branch": "main",
    "source_directory": "docs/source/",
    "navigation_with_keys": True,
    "light_css_variables": {
        "color-brand-primary": "#5e17eb",
        "color-brand-content": "#4b12c0",
    },
    "dark_css_variables": {
        "color-brand-primary": "#b69cff",
        "color-brand-content": "#c9b6ff",
    },
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/GubioGL/Q-BASIC",
            "html": "GitHub",
            "class": "",
        }
    ],
}


# ---------------------------------------------------------------------------
# Tutoriais: copiados de tutoriais/ na ordem de tutoriais/indice.yml
# ---------------------------------------------------------------------------
def preparar_tutoriais() -> None:
    origem = RAIZ / "tutoriais"
    destino = FONTE / "tutoriais"
    indice = yaml.safe_load((origem / "indice.yml").read_text(encoding="utf-8"))
    shutil.rmtree(destino, ignore_errors=True)
    destino.mkdir()
    linhas = [
        "# Tutoriais",
        "",
        "Notebooks Jupyter, do zero até a computação quântica. Cada página mostra as saídas "
        "salvas; para rodar no seu computador, baixe o notebook (botão no topo da página) e "
        'instale as dependências com `pip install "Q-BASIC[tutorial]"`.',
        "",
    ]
    for parte in indice["partes"]:
        (destino / parte["pasta"]).mkdir()
        documentos = []
        for capitulo in parte["capitulos"]:
            arquivo = Path(parte["pasta"]) / capitulo["arquivo"]
            shutil.copy2(origem / arquivo, destino / arquivo)
            documentos.append(arquivo.with_suffix("").as_posix())
        linhas += [
            f"## {parte['titulo']}",
            "",
            parte.get("descricao", ""),
            "",
            "```{toctree}",
            ":maxdepth: 1",
            "",
            *documentos,
            "```",
            "",
        ]
    (destino / "index.md").write_text("\n".join(linhas), encoding="utf-8")


preparar_tutoriais()
