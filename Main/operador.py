from .class_tijolo import ObjQuantico,ObjQuantico_esparso

import numpy as np
import scipy as sp

def Identidade(N,sparsa=False):
    """
    Creates an identity matrix of size NxN.

    Parameters:
    N (int): The size of the identity matrix.
    sparsa (bool): If True, returns a sparse identity matrix. Defaults to False.

    Returns:
    ObjQuantico or ObjQuantico_esparso: An object containing the identity matrix.
    """
    if sparsa ==True:
        matriz = sp.sparse.identity(N)
        return ObjQuantico_esparso(matriz)
    else:
        matriz = np.identity(N)
        return ObjQuantico(matriz) 

def destruiçao(N,sparsa=False):
    """Retorna o operador de destruição  que aniquila um foton no estado |n>
    
    Parameters:
    N (int): dimensão do espa o de Hilbert
    
    Returns:
        ObjQuantico: dt
    """
    if sparsa ==True:
        subdiag = np.sqrt(np.arange(1, N))
        matriz  = sp.sparse.diags(subdiag,offsets=1)
        return ObjQuantico_esparso(matriz)
    else:
        subdiag = np.sqrt(np.arange(1, N)) # Monta os elementos na subdiagonal
        matriz  = np.diag(subdiag, k=1) # Operador de destruição
        return ObjQuantico(matriz) 

def criaçao(N,sparsa=False):
    """Retorna o operador de criaçao  que cria um foton no estado |n>
    
    Parameters:
    N (int): dimensão do espa o de Hilbert
    
    Returns:
        ObjQuantico: dt
    """
    return  destruiçao(N,sparsa=sparsa).dag()    
   
def operador_p(N,sparsa=False):
    """Retorna o operador de momento
    
    Parameters:
    N (int): dimensão do espa o de Hilbert
    
    Returns:
        ObjQuantico: operador de momento
    """
    return  -1j*(destruiçao(N,sparsa) - criaçao(N,sparsa))/np.sqrt(2)   
 
def operador_x(N,sparsa=False):
    """Retorna o operador de posição
    
    Parameters:
    N (int): dimens o do espa o de Hilbert
    
    Returns:
        ObjQuantico: operador de posição
    """
    return (destruiçao(N,sparsa) + criaçao(N,sparsa))/np.sqrt(2) 
   
def pauliX(sparsa=False):
    """Retorna a matriz de Pauli X
     
     Parameters:
     None
    
     Returns:
         ObjQuantico: Objeto que representa a matriz de Pauli X
    """
    latex_representation = r"$$ \hat{\sigma_x} $$"
    if sparsa ==  False:
        m = np.array([[ 0, 1 ],[ 1, 0 ]])
        return ObjQuantico(m,latex_representation)
    else:
        # Criando a matriz diretamente no formato esparso COO
        data = [1, 1]
        row = [0, 1]
        col = [1, 0]
        m   = sp.sparse.coo_array((data, (row, col)), shape=(2, 2))
        return ObjQuantico_esparso(m,latex_representation) 

def pauliY(sparsa=False):
    """Retorna a matriz de Pauli Y
     
     Parameters:
     None
    
     Returns:
         ObjQuantico: Objeto que representa a matriz de Pauli Y
    """
    latex_representation = r"$$ \hat{\sigma_y} $$"
    
    if sparsa:
        # Criando a matriz diretamente no formato esparso COO
        data = [-1j, 1j]
        row = [0, 1]
        col = [1, 0]
        m   = sp.sparse.coo_array((data, (row, col)), shape=(2, 2))
        return ObjQuantico_esparso(m, latex_representation)
    else:
        # Criando a matriz no formato denso
        m = np.array([[0, -1j], [1j, 0]])
        return ObjQuantico(m, latex_representation)

def pauliZ(sparsa=False):
    """Retorna a matriz de Pauli Z
     
    Parameters:
    None
    
    Returns:
        ObjQuantico: Objeto que representa a matriz de Pauli Z
    """
    latex_representation = r"$$ \hat{\sigma_z} $$"
    
    if sparsa:
        # Criando a matriz diretamente no formato esparso COO
        data = [1, -1]
        row = [0, 1]
        col = [0, 1]
        m   =  sp.sparse.coo_array((data, (row, col)), shape=(2, 2))
        return ObjQuantico_esparso(m, latex_representation)
    else:
        # Criando a matriz no formato denso
        m = np.array([[1, 0], [0, -1]])
        return ObjQuantico(m, latex_representation)
    
def matrizdensidade(probabilities=None, estados=None, puro=True,sparsa=False):
    
    """
    Calcula a matriz densidade de um sistema quântico.

    Args:
        probabilities (list, optional): Lista de probabilidades para os estados mistos. Deve somar 1.
        states (list, optional): Lista de estados quânticos. Cada estado deve estar normalizado.
        puro (bool, optional): Indica se o estado é puro. Se True, calcula a matriz densidade para um estado puro.

    Returns:
        ObjQuantico: Objeto que representa a matriz densidade do sistema.
        
    Raises:
        ValueError: Se as probabilidades não somarem 1 ou se algum estado não estiver normalizado.
    """
    if puro == True:
        rho = estados*estados.dag()
        if sparsa==True:
            return ObjQuantico_esparso(sp.sparse.coo_array(rho.full()))
        else:
            return rho
    
    else:    
        # Verificar se as probabilidades somam 1
        if not np.isclose(sum(probabilities), 1):
            raise ValueError("As probabilidades devem somar 1.")
        
        # Verificar se cada estado está normalizado
        for state in estados:
            if not np.isclose(np.linalg.norm(state.full()), 1):
                raise ValueError("Todos os estados devem ser normalizados.")
             
        # Criar a matriz densidade
        dimensao = estados[0].full().shape[0] # pega o primeiro estado, em seguida a dimensao do estado
        rho = np.zeros((dimensao, dimensao), dtype=complex)
        for p, state in zip(probabilities, estados):
            rho += p * np.outer(state.full(), state.dag().full())  # |ψ⟩⟨ψ|
            
        if sparsa == True:
            return ObjQuantico_esparso(sp.sparse.coo_array(rho))
        else:
            return ObjQuantico(rho)
