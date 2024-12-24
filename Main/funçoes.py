from scipy.integrate import solve_ivp
from .class_tijolo import ObjQuantico

import numpy as np

class edo(ObjQuantico):
    @staticmethod
    def ODE_Schrodinger_vector(t, y, H_matrix):
        dydt = -1j * H_matrix @ y  # Equação de Schrödinger
        return dydt

    @staticmethod
    def solve(H_matrix, t_eval, y0, method='RK45', t_span=None, dense_output=False, 
               events=None, vectorized=False, **options):
        
        if t_span == None:
            t_span = (t_eval[0], t_eval[-1])  # Intervalo de tempo como tupla
        
        resultado = solve_ivp(
            edo.ODE_Schrodinger_vector,
            t_span,
            y0.full().flatten(),
            method      = method,
            t_eval      = t_eval,
            dense_output=dense_output,
            events      = events,
            vectorized  = vectorized,
            args        = (H_matrix.full(),),
            **options
        )
        return resultado
   
def valor_esperado( state, observable):
    """
    Calcula o valor esperado de uma observável dado o estado.
    
    Args:
        state (ndarray): Vetor de estado no instante de tempo (shape (4,)).
        observable (ndarray): Matriz da observável (shape (4, 4)).
    
    Returns:
        float: Valor esperado.
    """
    state_conj = np.conjugate(state)
    return np.real(state_conj @ (observable @ state)) 
  
def Valor_esperado(state, observables):
    """
    Calcula os valores esperados de uma lista de observáveis ao longo do tempo.
    
    Args:
        observables (list): Lista de objetos observáveis (cada um sendo uma matriz ou um operador).
    
    Returns:
        list: Lista de listas de valores esperados para cada observável ao longo do tempo.
    """
    resultados = []

    # Para cada observável na lista, calcula os valores esperados ao longo do tempo
    for observable in observables:
        observable_matrix = observable.full()  # Convertendo o operador para matriz
        data = []

        # Calcula o valor esperado para cada instante de tempo
        for t_idx in range(state.shape[1]):
            state_t = state[:, t_idx]
            data.append(float(valor_esperado(state_t, observable_matrix)))
        
        resultados.append(data)

    return resultados