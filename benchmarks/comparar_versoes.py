"""
Compara o desempenho de uma versão antiga do Q-BASIC com a versão atual.

Extrai o pacote de um commit antigo (``git archive``), roda ``bench_nucleo.py`` com cada
versão em processos separados e escreve uma tabela em Markdown.

Uso (a partir da raiz do repositório, com o pacote atual instalado)::

    python benchmarks/comparar_versoes.py                    # antes = e61545c
    python benchmarks/comparar_versoes.py --antes <commit> --saida benchmarks/resultados.md

A versão 0.0.x precisa de ``ipython`` e ``sympy`` instalados (usados no seu ``repr``).
"""

from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BENCH = RAIZ / "benchmarks" / "bench_nucleo.py"
# Último commit antes da reestruturação das Fases 4 e 5.
ANTES_PADRAO = "e61545c"


def extrair_versao(ref: str, destino: Path) -> Path:
    """Extrai o pacote ``qbasic`` do commit ``ref`` e devolve a pasta a pôr no PYTHONPATH."""
    arquivo = subprocess.run(
        ["git", "archive", "--format=tar", ref], cwd=RAIZ, check=True, capture_output=True
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(arquivo)) as tar:
        membros = [m for m in tar.getmembers() if "/qbasic/" in f"/{m.name}"]
        opcoes = {"filter": "data"} if hasattr(tarfile, "data_filter") else {}
        tar.extractall(destino, members=membros, **opcoes)
    for pasta in (destino / "src", destino):
        if (pasta / "qbasic" / "__init__.py").exists():
            return pasta
    raise RuntimeError(f"o commit {ref} não contém o pacote qbasic")


def rodar(pythonpath: Path | None) -> dict:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    if pythonpath is not None:
        env["PYTHONPATH"] = str(pythonpath)
    saida = subprocess.run(
        [sys.executable, str(BENCH), "--json"],
        cwd=tempfile.gettempdir(),  # evita importar o pacote da pasta atual por engano
        env=env,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return json.loads(saida.strip().splitlines()[-1])


def tabela(antes: dict, depois: dict, ref: str) -> str:
    linhas = [
        f"| Caso | Antes (`{ref}`) | Depois (v{depois['qbasic']}) | Ganho |",
        "|---|---:|---:|---:|",
    ]
    for nome, caso in depois["casos"].items():
        t_depois = caso["segundos"]
        if nome in antes["casos"]:
            t_antes = antes["casos"][nome]["segundos"]
            ganho = f"{t_antes / t_depois:,.1f}×"
            celula_antes = f"{1e3 * t_antes:,.2f} ms"
        else:
            ganho, celula_antes = "—", "não existe"
        linhas.append(
            f"| {caso['descricao']} | {celula_antes} | {1e3 * t_depois:,.2f} ms | {ganho} |"
        )
    ambiente = (
        f"Python {depois['python']}, NumPy {depois['numpy']}, SciPy {depois['scipy']}, "
        f"{depois['plataforma']}. Menor tempo de 3 repetições."
    )
    return "\n".join(linhas) + f"\n\n{ambiente}\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compara duas versões do Q-BASIC.")
    parser.add_argument("--antes", default=ANTES_PADRAO, help="commit da versão antiga")
    parser.add_argument("--saida", type=Path, help="arquivo Markdown para salvar a tabela")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as pasta:
        antes = rodar(extrair_versao(args.antes, Path(pasta)))
    depois = rodar(None)
    if Path(antes["arquivo"]).resolve() == Path(depois["arquivo"]).resolve():
        raise RuntimeError("as duas medições usaram o mesmo pacote; confira a instalação")

    resultado = tabela(antes, depois, args.antes)
    print(resultado)
    if args.saida:
        args.saida.write_text(resultado, encoding="utf-8")


if __name__ == "__main__":
    main()
