#from class_tijolo import ObjQuantico
import numpy as np

def destruiçao(N):
    """Retorna o operador de destruição  que aniquila um foton no estado |n>
    
    Parameters:
    N (int): dimensão do espa o de Hilbert
    
    Returns:
        ObjQuantico: dt
    """
    subdiag = np.sqrt(np.arange(1, N))# Monta os elementos na subdiagonal
    dt      = np.diag(subdiag, k=1) # Operador de destruição
    return ObjQuantico(dt)

def criaçao(N):
    """Retorna o operador de criaçao  que cria um foton no estado |n>
    
    Parameters:
    N (int): dimensão do espa o de Hilbert
    
    Returns:
        ObjQuantico: dt
    """
    return  destruiçao(N).dag()    
   
def operador_p(N):
    """Retorna o operador de momento
    
    Parameters:
    N (int): dimensão do espa o de Hilbert
    
    Returns:
        ObjQuantico: operador de momento
    """
    return -1j*(destruiçao(N) - criaçao(N))/np.sqrt(2)   
 
def operador_x(N):
    """Retorna o operador de posição
    
    Parameters:
    N (int): dimens o do espa o de Hilbert
    
    Returns:
        ObjQuantico: operador de posição
    """
    return (destruiçao(N) + criaçao(N))/np.sqrt(2) 
   
def pauliX():
    """Retorna a matriz de Pauli X
     
     Parameters:
     None
    
     Returns:
         ObjQuantico: Objeto que representa a matriz de Pauli X
    """
    m = np.array([[ 0, 1 ],[ 1, 0 ]])
    latex_representation = r"$$ \hat{\sigma_x} $$"
    return ObjQuantico(m,latex_representation)

def pauliY():
    """Retorna a matriz de Pauli Y
     
     Parameters:
     None
    
     Returns:
         ObjQuantico: Objeto que representa a matriz de Pauli Y
    """
    m = np.array([[ 0, -1j ],[ 1j, 0 ]])
    latex_representation = r"$$ \hat{\sigma_y} $$"  
    return ObjQuantico(m,latex_representation)

def pauliZ():
    """Retorna a matriz de Pauli Z
     
    Parameters:
    None
    
    Returns:
        ObjQuantico: Objeto que representa a matriz de Pauli Z
    """
    m = np.array([[ 1, 0 ],[ 0, -1 ]])
    latex_representation = r"$$ \hat{\sigma_z} $$"  
    return ObjQuantico(m,latex_representation)


def matrizdensidade(probabilities=None, states=None, puro=True):
    
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
        return state*state.dag()
    
    else:   
        # Verificar se as probabilidades somam 1
        if not np.isclose(sum(probabilities), 1):
            raise ValueError("As probabilidades devem somar 1.")
        
        # Verificar se cada estado está normalizado
        for state in states:
            if not np.isclose(np.linalg.norm(state.full()), 1):
                raise ValueError("Todos os estados devem ser normalizados.")
             
        # Criar a matriz densidade
        rho = np.zeros((states[0].full().shape[0], states[0].full().shape[0]), dtype=complex)
        
        for p, state in zip(probabilities, states):
            rho += p * np.outer(state.full(), state.dag().full())  # |ψ⟩⟨ψ|
    
    return rho
