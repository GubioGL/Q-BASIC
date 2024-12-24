import numpy as np
import scipy
from .class_tijolo import ObjQuantico

def bases(N,n):
    
    """
    Gera um estado de base no espaço o vetorial de dimençao N, com o estado 1
    na posicao n.
    
    Parameters
    ----------
    N : int
        Dimens o do espa o vetorial.
    n : int
        Posi o do estado 1.
    
    Returns
    -------
    ObjQuantico
        O estado de base.
    """
    estadoinicial = np.zeros(shape=(N, 1))*(0+0j)
    estadoinicial[n, 0] = 1
    
    return ObjQuantico(estadoinicial) 
  
def ket(entrada):
    """
    Retorna o estado ket |entrada> no espaço vetorial de dimens o 2.
    
    Parameters
    ----------
    entrada : str or array_like
        O estado ket |entrada>. Se `entrada` for uma string, deve ser '0' ou '1'.
        Se for um array_like, deve ser uma coluna com 2 elementos.
    
    Returns
    -------
    ObjQuantico
        O estado ket |entrada>.
    """
    if isinstance(entrada, str) and entrada in ('0', '1'):
        dados = np.zeros((2, 1))
        dados[int(entrada), 0] = 1
        latex_representation = rf"$$ \ket{entrada} $$"
        return ObjQuantico(dados, latex_representation)
    try:
        return ObjQuantico(entrada)
    except ValueError:
        print("Entrada invalida.")
    
def bra(entrada):
    """
    Retorna o estado bra <entrada| no espaço vetorial de dimensão 2.

    Parameters
    ----------
    entrada : str or array_like
        O estado bra <entrada|. Se `entrada` for uma string, deve ser '0' ou '1'.
        Se for um array_like, deve ser uma coluna com 2 elementos.

    Returns
    -------
    ObjQuantico
        O estado bra <entrada|.
    """
    if isinstance(entrada, str):
        if entrada == '0':
            return ObjQuantico(np.array([[1], [0]]), r"$$ \bra{0} $$")
        elif entrada == '1':
            return ObjQuantico(np.array([[0], [1]]), r"$$ \bra{1} $$")
    else:
        return ObjQuantico(entrada)
            
def Fock(N, n=0):
    """
    Gera um estado de Fock no espaço vetorial de dimensão N.

    Parameters
    ----------
    N : int
        Dimensão do espaço vetorial.
    n : int, optional
        Número de partículas no estado Fock, por padrão 0.

    Returns
    -------
    ObjQuantico
        O estado Fock correspondente.
    """
    # Utiliza a função 'bases' para gerar o estado de Fock
    return bases(N, n)

def coerente(N,alpha,metodo ="operador"):
    """
    Gera um estado coerente no espaço vetorial de dimensão N.

    Parameters
    ----------
    N : int
        Dimensão do espaço vetorial.
    alpha : complex
        Coeficiente complexo do estado coerente.
    metodo : str, optional
        Método para gerar o estado coerente, por padrão "operador".

    Returns
    -------
    ObjQuantico
        O estado coerente correspondente.
    """
    if metodo == "operador" :
        estado  = bases(N,0) # estado inicinal no vacuo
        D       = alpha * destruiçao(N).dag() - np.conj(alpha) * destruiçao(N)
        D       = D.expM()
        return D*estado
    
    elif metodo == "analitico":    
        estado  = np.zeros(shape=(N,1),dtype=complex)
        n       = np.arange(N)
        estado[:,0] = np.exp(-(abs(alpha) ** 2 )/ 2.0) * (alpha**n)/np.sqrt(scipy.special.factorial(n))
        return estado
    else:
        raise TypeError(
            "A opção de método tem as seguintes opções :'operador' ou 'analitico'")
        