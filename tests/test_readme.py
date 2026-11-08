"""Os exemplos de código do README devem rodar."""

import re
from pathlib import Path

import pytest

README = Path(__file__).resolve().parents[1] / "README.md"


def blocos_python(texto):
    """Blocos de código marcados como ```python no Markdown."""
    return re.findall(r"```python\n(.*?)```", texto, flags=re.DOTALL)


@pytest.mark.xfail(
    reason="B1: o exemplo do README usa estado_zero e X, que não existem (Fase 4, item 4.1)"
)
def test_exemplos_do_readme_executam():
    blocos = blocos_python(README.read_text(encoding="utf-8"))
    assert blocos, "o README não tem exemplos em ```python"
    for codigo in blocos:
        exec(compile(codigo, str(README), "exec"), {})
