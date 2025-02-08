import numpy as np
import sympy as sy
import scipy as sp

from scipy.linalg import expm
from IPython.display import display, Math

class ObjQuantico:

    def __init__(self, data,latex_representation=None):
        """
            Initializer for the class.

            Parameters
            ----------
            data : numpy.ndarray or scipy.sparse.csr_matrix
                The data to be stored in the object.
            latex_representation : str, optional
                A LaTeX representation of the object, by default None
        """        
        
        self.dados = data
        self.latex_representation = latex_representation

    def definir_dados(self, data):
        """
            Define os dados do objeto.
        
            Parameters
            ----------
            data : numpy.ndarray or scipy.sparse.csr_matrix
                Os dados a serem armazenados no objeto.
        """
        self.dados = data

    def full(self):
        """
            Retorna a matriz de dados completa.

            Returns
            -------
            numpy.ndarray or scipy.sparse.csr_matrix
                A matriz de dados completa.
        """
        return self.dados
    
    def dim(self):
        """
            Retorna a dimens o do sistema quantico.

            Returns
            -------
            int
                A dimens o do sistema quantico.
        """
        return len(self.dados)
    
    def dag(self):
        """
        Calcula o conjugado transposto (dagger) dos dados quânticos.

        Returns
        -------
        ObjQuantico
            Uma nova instância de ObjQuantico contendo o conjugado transposto
            dos dados armazenados.
        """
        return ObjQuantico(np.conjugate(self.dados.T))
    
    def traço(self):
        """
        Calcula o traço dos da matriz.

        Returns
        -------
        float
            O valor real do traço da matriz de dados.
        """
        return np.trace(self.dados).real
    
    def Autovalores(self):
        """
        Calcula os autovalores da matriz de dados, usando numpy.linalg.eigvals

        Returns
        -------
        numpy.ndarray
            Um array contendo os autovalores da matriz de dados.
        """
        return np.linalg.eigvals(self.dados)
    
    def Autovetores(self):
        """
        Calcula os autovetores da matriz de dados, usando numpy.linalg.eig

        Returns
        -------
        numpy.ndarray
            Um array contendo os autovetores da matriz de dados.
        """
        return np.linalg.eig(self.dados)[1]
    
    def AutoValor_Vetor(self):
        """
        Calcula os auto valor e vetor da matriz  using numpy.linalg.eig.

        Returns
        -------
        numpy.ndarray
            An array containing the eigenvectors of the data matrix.
        """
        return np.linalg.eig(self.dados)[1]
    
    def expM(self):
        return ObjQuantico(expm(self.dados)) 

    def __repr__(self):
        if self.latex_representation:
            display(Math(self.latex_representation))
        else:
            display(Math(sy.latex(sy.Matrix(self.dados))))
        return f"ObjQuantico: dim ={self.dim()} , shape = {self.dados.shape}" 
    
    def __mul__(self, other):
        # Multiplicação para diferentes tipos
        if isinstance(other, ObjQuantico):  
            # Multiplicação matricial com outra instância de ObjQuantico
            return ObjQuantico(np.dot(self.dados, other.dados))
        elif np.isscalar(other):  # Multiplicação por escalar
            return ObjQuantico(self.dados * other)
        else:
            raise TypeError(f"Multiplicação não suportada entre {type(other)} e ObjQuantico")

    def __rmul__(self, other):
        if np.isscalar(other):  # Multiplicação reversa por escalar
            return ObjQuantico(self.dados * other)
        else:
            raise TypeError(f"Multiplicação não suportada entre {type(other)} e ObjQuantico")
               
    def __add__(self, other):
        if isinstance(other, ObjQuantico):  
            # Soma os dados de dois objetos ObjQuantico
            return ObjQuantico(self.dados + other.dados)
        else:
            raise TypeError(f"Soma não suportada entre {type(other)} e ObjQuantico")
        
    def __sub__(self, other):
        if isinstance(other, ObjQuantico):  
            # Subtração entre duas instâncias de ObjQuantico
            return ObjQuantico(self.dados - other.dados)
        elif isinstance(other, np.ndarray):  # Subtração com arrays NumPy
            return ObjQuantico(self.dados - other)
        else:
            raise TypeError(f"Subtração não suportada entre {type(other)} e ObjQuantico")
    
    def __rsub__(self, other):
        if isinstance(other, np.ndarray):  # Subtração com arrays NumPy (comutada)
            return ObjQuantico(other - self.dados)
        else:
            raise TypeError(f"Subtração não suportada entre {type(other)} e ObjQuantico")   

    def __truediv__(self, other):
        if isinstance(other, (int, float)):  # Divisão por um número escalar
            return ObjQuantico(self.dados / other)
        else:
            raise TypeError(f"Divisão não suportada entre {type(other)} e ObjQuantico")
    
    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):  # Divisão invertida por um número escalar
            return ObjQuantico(other / self.dados)
        else:
            raise TypeError(f"Divisão não suportada entre {type(other)} e ObjQuantico")     
    
    def __pow__(self, power):
        if not isinstance(power, int) or power < 0:
            raise ValueError("A potência deve ser um inteiro não negativo.")    
        # Caso base: potência 0 retorna identidade
        result = np.eye(len(self.dados))  # Matriz identidade do mesmo tamanho
        for _ in range(power):
            result = np.dot(result, self.dados)  # Multiplicação iterativa

        return ObjQuantico(result)
    
    @property
    def T(self):
        """Propriedade para acessar a transposta de um ObjQuantico."""
        return self.dados.T
    
    def __matmul__(self, other):
        """Implementa o operador @ para o produto tensorial."""
        if isinstance(other, ObjQuantico):
            return ObjQuantico(np.kron(self.full(), other.full()))
        else:
            raise TypeError(f"Operador @ não suportado entre {type(self)} e {type(other)}")
    
class ObjQuantico_esparso:
    def __init__(self, data,latex_representation=None):
        # Convertendo para uma matriz esparsa
        self.dados = sp.sparse.coo_array(data)
        self.latex_representation = latex_representation

    def definir_dados(self, data):
        self.dados = data

    def full(self):
        return self.dados.todense()
    
    def full_sparsa(self):
        return self.dados
    
    def dim(self):
        return len(self.dados.todense())
    
    def expM(self):
        # Convertendo para csc matriz pq é mais eficiente
        matrix = sp.sparse.csc_matrix(self.dados)
        matrix = sp.sparse.linalg.expm(matrix)
        return ObjQuantico_esparso(matrix) 
    
    def dag(self):
        return ObjQuantico_esparso(self.dados.transpose().conjugate())
    
    def traço(self):
        return float(self.dados.trace().real)
    
    def Autovalores(self):
        return np.linalg.eigvals(self.dados.todense())
    
    def Autovetores(self):
        return np.linalg.eig(self.dados.todense())[1]
    
    def AutoValor_Vetor(self):
        return np.linalg.eig(self.dados.todense())
    
    def __repr__(self):
        if self.latex_representation:
            display(Math(self.latex_representation))
        else:
            display(Math(sy.latex(sy.Matrix(self.dados.todense()))))
        return f"ObjQuantico: dim ={self.dim()} , shape = {self.dados.todense().shape}" 
                
    def __add__(self, other):
        if isinstance(other, ObjQuantico_esparso):  
            # Soma os dados de dois objetos ObjQuantico_esparso
            data = self.dados + other.dados
            data = sp.sparse.coo_array(data)
            return ObjQuantico_esparso(data)
        else:
            raise TypeError(f"Soma não suportada entre {type(other)} e ObjQuantico")
        
    def __sub__(self, other):
        if isinstance(other, ObjQuantico_esparso):  
            # Subtração entre duas instâncias de ObjQuantico
            data = self.dados - other.dados
            #data = sp.sparse.coo_array(data)
            return ObjQuantico_esparso(data)
        else:
            raise TypeError(f"Subtração não suportada entre {type(other)} e ObjQuantico")
    
    def __mul__(self, other):
        # Multiplicação para diferentes tipos
        if isinstance(other, ObjQuantico_esparso):  
            print("Aqui !")
            # Multiplicação matricial com outra instância de ObjQuantico
            return ObjQuantico_esparso(self.dados.dot(other.dados))
        elif np.isscalar(other):  # Multiplicação por escalar
            return ObjQuantico_esparso(self.dados * other)
        else:
            raise TypeError(f"Multiplicação não suportada entre {type(other)} e ObjQuantico")

    def __rmul__(self, other):
        if np.isscalar(other):  # Multiplicação reversa por escalar
            return ObjQuantico_esparso(self.dados * other)
        else:
            raise TypeError(f"Multiplicação não suportada entre {type(other)} e ObjQuantico")
    
    def __truediv__(self, other):
        if isinstance(other, (int, float)):  # Divisão por um número escalar
            return ObjQuantico_esparso(self.dados / other)
        else:
            raise TypeError(f"Divisão não suportada entre {type(other)} e ObjQuantico")
    
    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):  # Divisão invertida por um número escalar
            return ObjQuantico_esparso(other / self.dados)
        else:
            raise TypeError(f"Divisão não suportada entre {type(other)} e ObjQuantico")     
         
    def __pow__(self, power):
        if not isinstance(power, int) or power < 0:
            raise ValueError("A potência deve ser um inteiro não negativo.")
        
        # Obter a matriz identidade no formato esparso
        size = self.dados.shape[0]  # Número de linhas
        result = sp.sparse.identity(size, format='csr')  # Identidade esparsa no formato CSR
        
        # Multiplicação iterativa
        for _ in range(power):
            result = result @ self.dados  # Multiplicação esparsa eficiente
        return ObjQuantico_esparso(result)
    
    def __matmul__(self, other):
        """Implementa o operador @ para o produto tensorial."""
        if isinstance(other, ObjQuantico_esparso):
            return ObjQuantico_esparso(sp.sparse.kron(self.full_sparsa(), other.full_sparsa()))
        else:
            raise TypeError(f"Operador @ não suportado entre {type(self)} e {type(other)}")