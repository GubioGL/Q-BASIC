"""Obsoleto: use :mod:`qbasic.objeto`.

Mantido para que códigos antigos (``from qbasic.class_tijolo import ObjQuantico``)
continuem funcionando.
"""

import warnings

from .objeto import ObjQuantico, ObjQuantico_esparso

__all__ = ["ObjQuantico", "ObjQuantico_esparso"]

warnings.warn(
    "'qbasic.class_tijolo' está obsoleto e será removido numa versão futura; "
    "use 'qbasic.objeto' (ou simplesmente 'qbasic.ObjQuantico').",
    DeprecationWarning,
    stacklevel=2,
)
