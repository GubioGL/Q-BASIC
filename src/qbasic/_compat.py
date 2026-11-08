"""Ferramentas internas para manter nomes antigos funcionando (com aviso de obsolescência).

Na versão 0.1.0 os nomes públicos passaram a ser escritos sem acento e em minúsculas
(por exemplo, ``destruiçao`` → ``destruicao``). Os nomes antigos continuam funcionando,
mas emitem um :class:`DeprecationWarning` indicando o nome novo.
"""

from __future__ import annotations

import importlib
import warnings
from collections.abc import Callable
from typing import Any

__all__ = ["avisar_obsoleto", "getattr_obsoleto", "importar_sem_aviso"]


def avisar_obsoleto(nome_antigo: str, nome_novo: str, nivel: int = 3) -> None:
    """Emite o aviso padrão de nome obsoleto."""
    warnings.warn(
        f"'{nome_antigo}' está obsoleto e será removido numa versão futura; use '{nome_novo}'.",
        DeprecationWarning,
        stacklevel=nivel,
    )


def getattr_obsoleto(
    nome_modulo: str, mapa: dict[str, tuple[str, Callable[[], Any]]]
) -> Callable[[str], Any]:
    """Cria um ``__getattr__`` de módulo (PEP 562) para nomes obsoletos.

    ``mapa`` associa cada nome antigo a ``(nome_novo, carregar)``, onde ``carregar()``
    devolve o objeto. O aviso é emitido a cada acesso ao nome antigo.
    """

    def __getattr__(nome: str) -> Any:
        if nome in mapa:
            nome_novo, carregar = mapa[nome]
            avisar_obsoleto(f"{nome_modulo}.{nome}", nome_novo)
            return carregar()
        raise AttributeError(f"o módulo '{nome_modulo}' não tem o atributo '{nome}'")

    return __getattr__


def importar_sem_aviso(nome_modulo: str) -> Any:
    """Importa um módulo de compatibilidade sem repetir o aviso do próprio módulo."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        return importlib.import_module(nome_modulo)
