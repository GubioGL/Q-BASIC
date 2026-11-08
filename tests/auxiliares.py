"""Funções auxiliares compartilhadas pelos testes."""

import numpy as np

# Tolerância absoluta padrão para comparações numéricas.
ATOL = 1e-10


def densa(obj) -> np.ndarray:
    """Matriz NumPy densa de um ``ObjQuantico`` ou ``ObjQuantico_esparso``."""
    return np.asarray(obj.full())


def comutador(A, B) -> np.ndarray:
    """Comutador ``[A, B] = AB - BA`` como matriz densa."""
    return densa(A * B) - densa(B * A)


def escalar(obj) -> complex:
    """Valor de um objeto 1x1 (por exemplo, o resultado de ``bra * ket``)."""
    matriz = densa(obj)
    assert matriz.shape == (1, 1)
    return complex(matriz[0, 0])
