"""Obsoleto: use :mod:`qbasic.dinamica` e :mod:`qbasic.medidas`.

=========================  ==================================================
Antigo                     Novo
=========================  ==================================================
``edo.solve(H, t, psi0)``  ``resolver_schrodinger(H, psi0, t, observaveis)``
``Valor_esperado``         ``valores_esperados``
``valor_esperado``         ``valor_esperado`` (agora aceita ObjQuantico)
=========================  ==================================================
"""

import warnings

import numpy as np
from scipy.integrate import solve_ivp

from .dinamica import ATOL_PADRAO, RTOL_PADRAO
from .medidas import valor_esperado, valores_esperados

__all__ = ["Valor_esperado", "edo", "valor_esperado"]

warnings.warn(
    "'qbasic.funçoes' está obsoleto e será removido numa versão futura; use "
    "'qbasic.resolver_schrodinger' e 'qbasic.valores_esperados'.",
    DeprecationWarning,
    stacklevel=2,
)


class edo:
    """Obsoleto: use :func:`qbasic.resolver_schrodinger`.

    ``edo.solve`` devolve o mesmo objeto do :func:`scipy.integrate.solve_ivp`
    (com ``.t`` e ``.y``), como nas versões anteriores.
    """

    @staticmethod
    def ODE_Schrodinger_vector(t, y, H_matrix):
        """Lado direito da equação de Schrödinger, ``-i H y``."""
        return -1j * (H_matrix @ y)

    @staticmethod
    def solve(
        H_matrix,
        t_eval,
        y0,
        method="RK45",
        t_span=None,
        dense_output=False,
        events=None,
        vectorized=False,
        **options,
    ):
        """Integra a equação de Schrödinger com ``solve_ivp`` (sem densificar ``H``)."""
        options.setdefault("rtol", RTOL_PADRAO)
        options.setdefault("atol", ATOL_PADRAO)
        if t_span is None:
            t_span = (t_eval[0], t_eval[-1])
        return solve_ivp(
            edo.ODE_Schrodinger_vector,
            t_span,
            y0.full().ravel().astype(complex),
            method=method,
            t_eval=t_eval,
            dense_output=dense_output,
            events=events,
            vectorized=vectorized,
            args=(H_matrix.dados,),
            **options,
        )


def Valor_esperado(state, observables):
    """Obsoleto: use :func:`qbasic.valores_esperados`.

    Mantém o retorno antigo: uma lista de listas de ``float`` (parte real).
    """
    return [
        [float(v) for v in np.real(np.atleast_1d(valores))]
        for valores in valores_esperados(state, list(observables))
    ]
