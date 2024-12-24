import numpy as np
import scipy as sp
from .class_tijolo import ObjQuantico,ObjQuantico_esparso
from .operador import destruiçao



def bases(N:int, n:int, sparsa=False):
    """
    Gera um vetor de estado quântico.
    
    Parâmetros:
    N (int): A dimensão do vetor de estado.
    n (int): O índice do estado base a ser inicializado.
    sparsa (bool, opcional): Se True, usa uma representação esparsa para o vetor de estado. Padrão é False.
    
    Retorna:
    ObjQuantico ou ObjQuantico_esparso: Um objeto que representa o estado quântico denso ou esparso.
    """
    
    if N <= 0 or n < 0:
        raise ValueError("N deve ser um inteiro positivo e n deve ser um inteiro não negativo.")
    
    if sparsa == False:
        estadoinicial = np.zeros(shape=(N, 1),dtype=complex)
        estadoinicial[n, 0] = 1
        return ObjQuantico(estadoinicial) 
    else:
        estadoinicial = sp.sparse.lil_array((N, 1),dtype=complex)
        estadoinicial[n:n+1] =  1 
        return ObjQuantico_esparso(estadoinicial) 
  
def ket(entrada,sparsa=False):
    """
    Retorna o estado ket |entrada> no espaço vetorial de dimens o 2.
    
    Parameters
    ----------
    entrada (str or array_like):
        O estado ket |entrada>. 
        Se `entrada` for uma string, deve ser '0' ou '1'.
        Se for um array_like, deve ser uma coluna com 2 elementos.
    
    Returns
    -------
    ObjQuantico
        O estado ket |entrada>.
    """
    if isinstance(entrada, (int, float)) or (isinstance(entrada, str) and entrada in ('0', '1')):
        
        latex_representation = rf"$$ \ket{entrada} $$"
        
        if sparsa == False:
            dados = bases(N=2,n=int(entrada),sparsa=sparsa).full()
            return ObjQuantico(dados, latex_representation)
        else:
            dados = bases(N=2,n=int(entrada),sparsa=sparsa).full_sparsa()
            return ObjQuantico_esparso(dados, latex_representation)
    else:
        print("Entrada invalida / tente usar outra função( sugestão bases) ")
    
def bra(entrada,sparsa=False):
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
    if isinstance(entrada, (int, float)) or (isinstance(entrada, str) and entrada in ('0', '1')):
        
        latex_representation = rf"$$ \bra{entrada} $$"
        
        if sparsa == False:
            dados = bases(N=2,n=int(entrada),sparsa=sparsa).dag().full()
            return ObjQuantico(dados, latex_representation)
        else:
            dados = bases(N=2,n=int(entrada),sparsa=sparsa).dag().full_sparsa()
            return ObjQuantico_esparso(dados, latex_representation)
    else:
        print("Entrada invalida / tente usar outra função( sugestão bases) ")
            
def Fock(N, n=0,sparsa=False):
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
    return bases(N, n,sparsa)

def coerente(N,alpha,metodo ="operador",sparsa = False):
    """
    Gera um estado coerente no espaço vetorial de dimensão N.

    Parameters
    ----------
    N (int) :        Dimensão do espaço vetorial.
    alpha (complex) :     Coeficiente complexo do estado coerente.
    metodo : str, optional
        Método para gerar o estado coerente, por padrão "operador".

    Returns
    -------
    ObjQuantico
        O estado coerente correspondente.
    """
    
    if metodo == "operador" :
        estado  = bases(N,0,sparsa) # estado inicinal no vacuo
        D       = alpha * destruiçao(N,sparsa).dag() - np.conj(alpha) * destruiçao(N,sparsa)
        D       = D.expM()
        return D*estado
        
    elif metodo == "analitico":    # implementar o metodo de matrizes esparsas
        if sparsa ==False:
            estado  = np.zeros(shape=(N,1),dtype=complex)
            n       = np.arange(N)
            estado[:,0] = np.exp(-(abs(alpha) ** 2 )/ 2.0) * (alpha**n)/np.sqrt(sp.special.factorial(n))
            return ObjQuantico(estado)     
        else:
            estado = sp.sparse.lil_array((N, 1),dtype=complex)
            estado[:] = np.exp(-(abs(alpha) ** 2 )/ 2.0) * (alpha**np.arange(N))/np.sqrt(sp.special.factorial(np.arange(N)))
            return ObjQuantico_esparso(estado)   
    else:
        raise TypeError(
            "A opção de método tem as seguintes opções :'operador' ou 'analitico'")