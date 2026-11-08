"""Funções auxiliares compartilhadas pelos testes."""

import numpy as np

import qbasic as qb

# Tolerância absoluta padrão para comparações numéricas.
ATOL = 1e-10


def densa(obj) -> np.ndarray:
    """Matriz NumPy densa de um ``ObjQuantico``."""
    return np.asarray(obj.full())


def criar(matriz, sparsa: bool) -> qb.ObjQuantico:
    """Cria um ``ObjQuantico`` no formato denso ou esparso."""
    return qb.ObjQuantico(matriz, formato="esparso" if sparsa else "denso")


def comutador(A, B) -> np.ndarray:
    """Comutador ``[A, B] = AB - BA`` como matriz densa."""
    return densa(A * B) - densa(B * A)


def escalar(obj) -> complex:
    """Valor de um objeto 1x1 (por exemplo, o resultado de ``bra * ket``)."""
    matriz = densa(obj)
    assert matriz.shape == (1, 1)
    return complex(matriz[0, 0])
