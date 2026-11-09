"""Testes do script que gera o livro em LaTeX a partir dos tutoriais."""

import base64
import importlib.util
import json
import shutil
import struct
import zlib
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SCRIPT = RAIZ / "scripts" / "gerar_tutorial_latex.py"


def _png_1x1() -> str:
    """PNG válido de 1x1 pixel, em base64 (como nas saídas dos notebooks)."""

    def bloco(tipo: bytes, dados: bytes) -> bytes:
        crc = zlib.crc32(tipo + dados) & 0xFFFFFFFF
        return struct.pack(">I", len(dados)) + tipo + dados + struct.pack(">I", crc)

    cabecalho = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)  # 1x1, RGB, 8 bits
    imagem = zlib.compress(b"\x00\x5e\x17\xeb")  # filtro 0 + um pixel roxo
    png = (
        b"\x89PNG\r\n\x1a\n"
        + bloco(b"IHDR", cabecalho)
        + bloco(b"IDAT", imagem)
        + bloco(b"IEND", b"")
    )
    return base64.b64encode(png).decode()


PNG = _png_1x1()


@pytest.fixture(scope="module")
def livro():
    spec = importlib.util.spec_from_file_location("gerar_tutorial_latex", SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def celula(tipo, fonte, saidas=None, tags=None):
    dados = {"cell_type": tipo, "metadata": {"tags": tags} if tags else {}, "source": fonte}
    if tipo == "code":
        dados.update(outputs=saidas or [], execution_count=1)
    return dados


class TestMarkdown:
    def test_equation_vira_dolar_duplo(self, livro):
        texto = livro.preparar_markdown("antes\n\\begin{equation}\n a = b\n\\end{equation}\ndepois")
        assert "\\begin{equation}" not in texto
        assert "$$\na = b\n$$" in texto

    def test_matematica_com_espacos(self, livro):
        texto = livro.preparar_markdown("O operador $ \\hat{a} $ age em $|n\\rangle$.")
        assert "$\\hat{a}$" in texto
        assert "$|n\\rangle$" in texto

    def test_dolar_duplo_e_dolar_escapado_nao_mudam(self, livro):
        assert livro.preparar_markdown("$$ x = 1 $$") == "$$ x = 1 $$"
        assert livro.preparar_markdown("custa \\$5") == "custa \\$5"

    def test_titulos_descem_um_nivel(self, livro):
        assert livro.preparar_markdown("## Seção\n### Sub") == "### Seção\n#### Sub"

    def test_corrigir_arrays(self, livro):
        corrigido = livro.corrigir_arrays(r"\begin{array}{cc}1 & 2 & 3\\4 & 5 & 6\end{array}")
        assert corrigido.startswith(r"\begin{array}{ccc}")
        certo = r"\begin{array}{cc}1 & 2\\3 & 4\end{array}"
        assert livro.corrigir_arrays(certo) == certo


class TestSaidas:
    def test_texto_longo_e_truncado(self, livro):
        bloco = livro.bloco_saida("\n".join(str(i) for i in range(100)), max_linhas=10)
        assert "90 linhas omitidas" in bloco
        assert "\\begin{saida}" in bloco

    def test_tipos_de_saida(self, livro, tmp_path):
        figuras = livro.Figuras(tmp_path, "cap")
        saidas = [
            {"output_type": "stream", "name": "stdout", "text": "olá\n"},
            {"output_type": "stream", "name": "stderr", "text": "aviso\n"},
            {
                "output_type": "display_data",
                "data": {"image/png": PNG, "text/plain": "<Figure size 640x480>"},
            },
            {
                "output_type": "execute_result",
                "data": {"text/latex": "$$\\hat{\\sigma}_x$$", "text/plain": "x"},
            },
            {
                "output_type": "execute_result",
                "data": {"text/plain": "[<matplotlib.lines.Line2D at 0x7f>]"},
            },
            {"output_type": "execute_result", "data": {"text/plain": "array([1, 2])"}},
            {
                "output_type": "error",
                "ename": "TypeError",
                "evalue": "não suportado",
                "traceback": [],
            },
        ]
        partes = livro.converter_saidas(
            celula("code", "x", saidas, tags=["raises-exception"]), figuras
        )
        texto = "\n".join(partes)
        assert "olá" in texto
        assert "aviso" not in texto  # stderr fica de fora
        assert (tmp_path / "cap_01.png").exists()
        assert "\\includegraphics" in texto
        assert "$\\displaystyle \\hat{\\sigma}_x$" in texto
        assert "Line2D" not in texto  # representação de objeto do matplotlib é ruído
        assert "array([1, 2])" in texto
        assert "\\begin{saidaerro}" in texto
        assert "erro proposital" in texto

    def test_codigo_com_crases(self, livro):
        assert livro.bloco_codigo("x = '```'").startswith("````python")


def test_converter_notebook_troca_o_titulo(livro, tmp_path):
    caminho = tmp_path / "simulador" / "01_teste.ipynb"
    caminho.parent.mkdir()
    notebook = {
        "cells": [
            celula("markdown", "# Título antigo"),
            celula("markdown", "## Seção\nTexto com $ x $."),
            celula(
                "code", "print(1)", [{"output_type": "stream", "name": "stdout", "text": "1\n"}]
            ),
            celula("code", ""),
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    caminho.write_text(json.dumps(notebook), encoding="utf-8")
    texto = livro.converter_notebook(caminho, "Aula 1 — Teste", livro.Figuras(tmp_path, "x"))
    assert texto.startswith("## Aula 1 — Teste {#cap-simulador-01-teste}")
    assert "Título antigo" not in texto
    assert "### Seção" in texto
    assert "```python\nprint(1)\n```" in texto


def test_gera_o_livro(livro, tmp_path):
    try:
        livro.caminho_pandoc()
    except SystemExit:
        pytest.skip("pandoc não disponível (instale com pip install -e '.[livro]')")
    pasta = tmp_path / "tutoriais"
    (pasta / "simulador").mkdir(parents=True)
    notebook = {
        "cells": [
            celula("markdown", "# Aula 0 — Teste"),
            celula(
                "markdown", "Texto com $\\alpha$ e\n\\begin{equation}\nE = mc^2\n\\end{equation}"
            ),
            celula(
                "code",
                "import qbasic as qb\nqb.pauliX()",
                [{"output_type": "execute_result", "data": {"text/latex": "$$\\hat{\\sigma}_x$$"}}],
            ),
            celula("code", "plot()", [{"output_type": "display_data", "data": {"image/png": PNG}}]),
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    (pasta / "simulador" / "00_teste.ipynb").write_text(json.dumps(notebook), encoding="utf-8")
    (pasta / "indice.yml").write_text(
        "partes:\n  - titulo: Parte I — Teste\n    pasta: simulador\n    capitulos:\n"
        "      - arquivo: 00_teste.ipynb\n        titulo: Aula 0 — Teste\n",
        encoding="utf-8",
    )
    tex = livro.gerar(pasta / "indice.yml", tmp_path / "build", data="01/01/2026")
    conteudo = tex.read_text(encoding="utf-8")
    assert "\\part{Parte I --- Teste}" in conteudo
    assert "\\chapter{Aula 0 --- Teste}" in conteudo
    assert "\\chapter*{Prefácio}" in conteudo
    assert "\\begin{Shaded}" in conteudo
    assert "\\includegraphics" in conteudo
    assert "E = mc^2" in conteudo
    assert "gerado em 01/01/2026" in (tmp_path / "build" / "capa.tex").read_text(encoding="utf-8")
    assert (tmp_path / "build" / "figuras" / "simulador_00_teste_01.png").exists()

    if shutil.which("xelatex"):
        pdf = livro.compilar_pdf(tex)
        assert pdf.exists()
