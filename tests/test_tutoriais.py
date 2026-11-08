"""Consistência dos tutoriais (a execução dos notebooks é feita no CI com nbmake)."""

import json
import re
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

PASTA = Path(__file__).resolve().parents[1] / "tutoriais"
INDICE = yaml.safe_load((PASTA / "indice.yml").read_text(encoding="utf-8"))
CAPITULOS = [
    (parte["pasta"], capitulo) for parte in INDICE["partes"] for capitulo in parte["capitulos"]
]
NOTEBOOKS = sorted(PASTA.glob("*/*.ipynb"))
PUBLICADOS = [nb for nb in NOTEBOOKS if nb.parent.name != "em_construcao"]

# Nomes da API antiga (0.0.x) que os tutoriais não devem mais usar.
OBSOLETOS = {
    "destruiçao",
    "criaçao",
    "Identidade",
    "Fock",
    "matrizdensidade",
    "edo",
    "Valor_esperado",
    "ObjQuantico_esparso",
    "funçoes",
    "operador",
    "class_tijolo",
}


def carregar(caminho):
    return json.loads(caminho.read_text(encoding="utf-8"))


def codigo(notebook):
    return [
        "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
        for c in notebook["cells"]
        if c["cell_type"] == "code"
    ]


def test_indice_lista_todos_os_notebooks_publicados():
    listados = {PASTA / pasta / cap["arquivo"] for pasta, cap in CAPITULOS}
    assert listados == set(PUBLICADOS)


@pytest.mark.parametrize(("pasta", "capitulo"), CAPITULOS, ids=[c["arquivo"] for _, c in CAPITULOS])
def test_titulo_do_notebook_igual_ao_indice(pasta, capitulo):
    notebook = carregar(PASTA / pasta / capitulo["arquivo"])
    primeira = notebook["cells"][0]
    texto = "".join(primeira["source"])
    assert primeira["cell_type"] == "markdown"
    assert texto.strip() == f"# {capitulo['titulo']}"


@pytest.mark.parametrize("caminho", PUBLICADOS, ids=lambda p: p.name)
def test_um_unico_titulo_de_nivel_1(caminho):
    # Títulos "# ..." extras viram páginas soltas no menu da documentação.
    celulas = carregar(caminho)["cells"]
    for celula in celulas[1:]:
        if celula["cell_type"] == "markdown":
            texto = "".join(celula["source"])
            assert not re.search(r"^# ", texto, re.M), f"{caminho.name}: {texto[:60]!r}"


@pytest.mark.parametrize("caminho", PUBLICADOS, ids=lambda p: p.name)
def test_nao_usa_nomes_obsoletos_da_biblioteca(caminho):
    for fonte in codigo(carregar(caminho)):
        usados = set(re.findall(r"\bqb\.(\w+)", fonte))
        for linha in re.findall(r"^\s*from qbasic(?:\.(\w+))? import ([^\n#]+)", fonte, re.M):
            usados |= {linha[0]} | {n.strip() for n in linha[1].replace("(", "").split(",")}
        usados |= set(re.findall(r"^\s*import qbasic\.(\w+)", fonte, re.M))
        assert not (usados & OBSOLETOS), f"{caminho.name}: {usados & OBSOLETOS}"


@pytest.mark.parametrize("caminho", NOTEBOOKS, ids=lambda p: p.name)
def test_metadados_padronizados(caminho):
    notebook = carregar(caminho)
    assert notebook["metadata"]["kernelspec"]["name"] == "python3"
    assert set(notebook["metadata"]) == {"kernelspec", "language_info"}


@pytest.mark.parametrize("caminho", PUBLICADOS, ids=lambda p: p.name)
def test_erros_salvos_sao_intencionais(caminho):
    for celula in carregar(caminho)["cells"]:
        tem_erro = any(o.get("output_type") == "error" for o in celula.get("outputs", []))
        if tem_erro:
            assert "raises-exception" in celula["metadata"].get("tags", [])


@pytest.mark.parametrize("caminho", NOTEBOOKS, ids=lambda p: p.name)
def test_saidas_sem_caminhos_locais(caminho):
    texto = caminho.read_text(encoding="utf-8")
    for padrao in ("/home/", "/tmp/", "C:\\\\Users", "site-packages"):
        assert padrao not in texto, f"{caminho.name} contém {padrao!r}"
