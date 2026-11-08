"""Classe base do Q-BASIC: :class:`ObjQuantico`.

Um ``ObjQuantico`` guarda um vetor de estado (ket ou bra) ou um operador, em formato
**denso** (``numpy.ndarray``) ou **esparso** (``scipy.sparse.csr_array``). Os dois
formatos podem ser misturados livremente nas operações.

Convenção dos operadores (herdada das versões anteriores):

* ``A * B`` — produto matricial (operador × operador, operador × ket, bra × ket...);
* ``A @ B`` — produto tensorial (o mesmo que :func:`qbasic.tensor`);
* ``c * A``, ``A / c``, ``A + c`` — escalares (``A + c`` significa ``A + c·I``).
"""

from __future__ import annotations

import numbers
from typing import Any

import numpy as np
import scipy.linalg as sla
import scipy.sparse as sps
import scipy.sparse.linalg as spla

from ._compat import avisar_obsoleto
from .visualizacao import latex_matriz

__all__ = ["ObjQuantico", "ObjQuantico_esparso"]

FORMATOS = ("denso", "esparso")
# Tolerância usada para decidir se um operador é hermitiano ou se um traço é real.
TOLERANCIA = 1e-12
# Matrizes esparsas com até este número de elementos são mostradas por completo no repr.
LIMITE_REPR_ESPARSO = 10_000


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------
def _eh_escalar(x: Any) -> bool:
    """Número Python/NumPy (int, float, complex) ou array 0-d."""
    if isinstance(x, np.ndarray):
        return x.ndim == 0
    return isinstance(x, numbers.Number)


def _valor_escalar(x: Any) -> complex | float | int:
    return x.item() if isinstance(x, np.ndarray) else x


def _como_denso(dados: Any) -> np.ndarray:
    return dados.toarray() if sps.issparse(dados) else dados


def _como_esparso(dados: Any) -> sps.csr_array:
    return dados if isinstance(dados, sps.csr_array) else sps.csr_array(dados)


def _dims_padrao(shape: tuple[int, int]) -> list[list[int]]:
    return [[int(shape[0])], [int(shape[1])]]


def _validar_dims(dims: Any, shape: tuple[int, int]) -> list[list[int]]:
    try:
        linhas, colunas = ([int(d) for d in parte] for parte in dims)
    except (TypeError, ValueError) as erro:
        raise ValueError(
            "dims deve ter a forma [[dimensões das linhas], [dimensões das colunas]]"
        ) from erro
    if int(np.prod(linhas)) != shape[0] or int(np.prod(colunas)) != shape[1]:
        raise ValueError(f"dims {dims} incompatível com a forma {shape}")
    return [linhas, colunas]


def _ordem_complexa(valores: np.ndarray) -> np.ndarray:
    """Índices que ordenam números complexos pela parte real e depois pela imaginária,
    ignorando ruído numérico (por exemplo, ``1e-17`` é tratado como zero)."""
    escala = max(1.0, float(np.max(np.abs(valores)))) if valores.size else 1.0
    casas = int(10 - np.log10(escala))
    return np.lexsort((np.round(valores.imag, casas), np.round(valores.real, casas)))


def _sem_cifrao(latex: str) -> str:
    return latex.strip().strip("$").strip()


def _latex_adjunto(latex: str | None) -> str | None:
    """LaTeX do adjunto: ``\\ket{x}`` ↔ ``\\bra{x}``; nos demais casos, ``(...)^\\dagger``."""
    if latex is None:
        return None
    corpo = _sem_cifrao(latex)
    for de, para in ((r"\ket{", r"\bra{"), (r"\bra{", r"\ket{")):
        if corpo.startswith(de) and corpo.endswith("}") and corpo.count("{") == 1:
            return f"$$ {para}{corpo[len(de) :]} $$"
    return rf"$$ \left({corpo}\right)^\dagger $$"


# ---------------------------------------------------------------------------
# ObjQuantico
# ---------------------------------------------------------------------------
class ObjQuantico:
    """Estado (ket/bra) ou operador quântico, denso ou esparso.

    Parameters
    ----------
    dados : array_like, matriz esparsa do SciPy ou ObjQuantico
        Os elementos de matriz. Um vetor 1-D é interpretado como ket (coluna).
    latex_representation : str, optional
        Símbolo LaTeX usado para exibir o objeto no Jupyter (por exemplo,
        ``r"$$ \\hat{\\sigma}_x $$"``). Sem ele, a matriz é exibida.
    formato : {"denso", "esparso"}, optional
        Formato de armazenamento. Por padrão, é esparso se ``dados`` for uma matriz
        esparsa do SciPy e denso caso contrário.
    dims : list, optional
        Dimensões dos subsistemas, ``[[linhas...], [colunas...]]``. Por exemplo, um ket
        de dois qubits tem ``dims = [[2, 2], [1, 1]]``. Por padrão, um único sistema.

    Examples
    --------
    >>> import qbasic as qb
    >>> X = qb.ObjQuantico([[0, 1], [1, 0]])
    >>> (X * X).full()
    array([[1, 0],
           [0, 1]])
    >>> qb.ObjQuantico([[0, 1], [1, 0]], formato="esparso").formato
    'esparso'
    """

    # Faz o NumPy delegar as operações mistas (ndarray ⊕ ObjQuantico) para esta classe.
    __array_ufunc__ = None

    def __init__(
        self,
        dados: Any,
        latex_representation: str | None = None,
        *,
        formato: str | None = None,
        dims: Any = None,
    ) -> None:
        if isinstance(dados, ObjQuantico):
            latex_representation = latex_representation or dados.latex_representation
            dims = dims if dims is not None else dados.dims
            formato = formato or dados.formato
            dados = dados.dados
        if formato is not None and formato not in FORMATOS:
            raise ValueError(f"formato deve ser 'denso' ou 'esparso', não {formato!r}")
        if formato is None:
            formato = "esparso" if sps.issparse(dados) else "denso"
        self._formato = formato
        self._dados = self._normalizar(dados, formato)
        self._dims = _dims_padrao(self.shape) if dims is None else _validar_dims(dims, self.shape)
        self.latex_representation = latex_representation

    @staticmethod
    def _normalizar(dados: Any, formato: str) -> np.ndarray | sps.csr_array:
        if sps.issparse(dados):
            if dados.ndim != 2:
                raise ValueError("matrizes esparsas devem ser bidimensionais")
            return _como_esparso(dados) if formato == "esparso" else dados.toarray()
        matriz = np.asarray(dados)
        if matriz.dtype.kind not in "biufc":
            raise TypeError(f"não é possível criar um ObjQuantico a partir de {type(dados)}")
        if matriz.ndim == 0:
            matriz = matriz.reshape(1, 1)
        elif matriz.ndim == 1:
            matriz = matriz.reshape(-1, 1)
        elif matriz.ndim != 2:
            raise ValueError(f"os dados devem ter no máximo 2 dimensões (recebido {matriz.ndim})")
        return sps.csr_array(matriz) if formato == "esparso" else matriz

    def _novo(self, dados: Any, *, dims: Any = None, latex: str | None = None) -> ObjQuantico:
        """Cria um ObjQuantico no formato correspondente ao tipo de ``dados``."""
        formato = "esparso" if sps.issparse(dados) else "denso"
        return ObjQuantico(dados, latex, formato=formato, dims=dims)

    # ------------------------------------------------------------------ dados
    @property
    def dados(self) -> np.ndarray | sps.csr_array:
        """Elementos de matriz (``ndarray`` no formato denso, ``csr_array`` no esparso)."""
        return self._dados

    @dados.setter
    def dados(self, valor: Any) -> None:
        self.definir_dados(valor)

    def definir_dados(self, dados: Any) -> None:
        """Substitui os elementos de matriz (o formato é inferido a partir de ``dados``)."""
        self._formato = "esparso" if sps.issparse(dados) else "denso"
        self._dados = self._normalizar(dados, self._formato)
        self._dims = _dims_padrao(self.shape)

    @property
    def formato(self) -> str:
        """``"denso"`` ou ``"esparso"``."""
        return self._formato

    @property
    def shape(self) -> tuple[int, int]:
        """Forma da matriz, ``(linhas, colunas)``."""
        return tuple(int(n) for n in self._dados.shape)

    @property
    def dims(self) -> list[list[int]]:
        """Dimensões dos subsistemas, ``[[linhas...], [colunas...]]``."""
        return [list(self._dims[0]), list(self._dims[1])]

    @property
    def tipo(self) -> str:
        """``"ket"``, ``"bra"``, ``"escalar"`` (1×1) ou ``"operador"``."""
        linhas, colunas = self.shape
        if linhas == 1 and colunas == 1:
            return "escalar"
        if colunas == 1:
            return "ket"
        if linhas == 1:
            return "bra"
        return "operador"

    def dim(self) -> int:
        """Dimensão do espaço de Hilbert (para kets, bras e operadores)."""
        linhas, colunas = self.shape
        return colunas if linhas == 1 else linhas

    def full(self) -> np.ndarray:
        """Matriz densa (``numpy.ndarray``)."""
        return _como_denso(self._dados)

    def full_sparsa(self) -> sps.csr_array:
        """Matriz esparsa (``scipy.sparse.csr_array``)."""
        return _como_esparso(self._dados)

    def para_denso(self) -> ObjQuantico:
        """Cópia no formato denso."""
        return ObjQuantico(self, formato="denso")

    def para_esparso(self) -> ObjQuantico:
        """Cópia no formato esparso."""
        return ObjQuantico(self, formato="esparso")

    def __array__(self, dtype: Any = None, copy: bool | None = None) -> np.ndarray:
        matriz = self.full()
        return matriz if dtype is None else matriz.astype(dtype)

    def __getitem__(self, indice: Any) -> Any:
        valor = self._dados[indice]
        return valor.toarray() if sps.issparse(valor) else valor

    # --------------------------------------------------------- álgebra linear
    def dag(self) -> ObjQuantico:
        """Adjunto (conjugado transposto), :math:`A^\\dagger`."""
        dados = self._dados.conj().T
        return self._novo(
            dados,
            dims=[self._dims[1], self._dims[0]],
            latex=_latex_adjunto(self.latex_representation),
        )

    def conj(self) -> ObjQuantico:
        """Conjugado complexo (sem transpor)."""
        return self._novo(self._dados.conj(), dims=self._dims)

    def transposta(self) -> ObjQuantico:
        """Transposta (sem conjugar)."""
        return self._novo(self._dados.T, dims=[self._dims[1], self._dims[0]])

    @property
    def T(self) -> np.ndarray | sps.csr_array:
        """Transposta dos dados brutos (compatibilidade; prefira :meth:`transposta`)."""
        return self._dados.T

    def traco(self) -> float | complex:
        """Traço. Retorna ``float`` se for real e ``complex`` caso contrário."""
        valor = complex(self._dados.diagonal().sum())
        if abs(valor.imag) <= TOLERANCIA * max(1.0, abs(valor)):
            return valor.real
        return valor

    def _exigir_quadrada(self, operacao: str) -> None:
        if self.shape[0] != self.shape[1]:
            raise ValueError(f"{operacao} exige um operador quadrado (forma atual: {self.shape})")

    def eh_hermitiano(self, tol: float = 1e-10) -> bool:
        """``True`` se o operador for hermitiano (:math:`A = A^\\dagger`)."""
        if self.shape[0] != self.shape[1]:
            return False
        diferenca = self._dados - self._dados.conj().T
        if sps.issparse(diferenca):
            return diferenca.nnz == 0 or bool(abs(diferenca).max() <= tol)
        return bool(np.all(np.abs(diferenca) <= tol))

    def autovalores(self, k: int | None = None) -> np.ndarray:
        """Autovalores em ordem crescente.

        Usa ``eigvalsh`` (mais rápido e preciso) quando o operador é hermitiano.

        Parameters
        ----------
        k : int, optional
            Só no formato esparso: calcula apenas os ``k`` menores autovalores com o
            método de Lanczos/Arnoldi, sem converter a matriz para densa.
        """
        return self.autoestados(k=k)[0] if k is not None else self._autovalores_densos()

    def _autovalores_densos(self) -> np.ndarray:
        self._exigir_quadrada("autovalores")
        matriz = self.full()
        if self.eh_hermitiano():
            return sla.eigvalsh(matriz)
        valores = sla.eigvals(matriz)
        return valores[_ordem_complexa(valores)]

    def autoestados(self, k: int | None = None) -> tuple[np.ndarray, np.ndarray]:
        """Autovalores (crescentes) e autovetores (colunas), ``(valores, vetores)``.

        Parameters
        ----------
        k : int, optional
            Só no formato esparso: calcula apenas os ``k`` menores autovalores.
        """
        self._exigir_quadrada("autoestados")
        hermitiano = self.eh_hermitiano()
        if k is not None and self.formato == "esparso":
            if hermitiano:
                valores, vetores = spla.eigsh(self._dados, k=k, which="SA")
            else:
                valores, vetores = spla.eigs(self._dados, k=k, which="SR")
        elif hermitiano:
            valores, vetores = sla.eigh(self.full())
        else:
            valores, vetores = sla.eig(self.full())
        if hermitiano:
            valores = valores.real
            ordem = np.argsort(valores, kind="stable")
        else:
            ordem = _ordem_complexa(valores)
        valores, vetores = valores[ordem], vetores[:, ordem]
        if k is not None:
            valores, vetores = valores[:k], vetores[:, :k]
        return valores, vetores

    def autovetores(self) -> np.ndarray:
        """Autovetores (colunas), na mesma ordem de :meth:`autovalores`."""
        return self.autoestados()[1]

    def expm(self) -> ObjQuantico:
        """Exponencial de matriz, :math:`e^{A}` (mantém o formato)."""
        self._exigir_quadrada("expm")
        if self.formato == "esparso":
            dados = sps.csr_array(spla.expm(sps.csc_array(self._dados)))
        else:
            dados = sla.expm(self._dados)
        return self._novo(dados, dims=self._dims)

    def norma(self) -> float:
        """Norma: euclidiana para kets/bras; norma do traço para operadores."""
        if self.tipo in ("ket", "bra", "escalar"):
            if self.formato == "esparso":
                return float(spla.norm(self._dados))
            return float(np.linalg.norm(self._dados))
        return float(np.linalg.norm(self.full(), ord="nuc"))

    def normalizar(self) -> ObjQuantico:
        """Cópia dividida pela :meth:`norma` (kets unitários, matrizes densidade com traço 1)."""
        norma = self.norma()
        if norma == 0:
            raise ZeroDivisionError("não é possível normalizar um objeto nulo")
        return self / norma

    # ------------------------------------------------------------- aritmética
    def _operando(self, outro: Any) -> ObjQuantico | None:
        """Converte arrays/matrizes em ObjQuantico; devolve None se não for possível."""
        if isinstance(outro, ObjQuantico):
            return outro
        if sps.issparse(outro) or (isinstance(outro, np.ndarray) and outro.ndim > 0):
            return ObjQuantico(outro)
        return None

    def _identidade(self, escalar: Any) -> ObjQuantico:
        self._exigir_quadrada("somar um escalar (A + c significa A + c·I)")
        n = self.shape[0]
        if self.formato == "esparso":
            dados = sps.csr_array(sps.identity(n, format="csr") * escalar)
        else:
            dados = escalar * np.eye(n)
        return ObjQuantico(dados, dims=self._dims)

    def _somar(self, outro: Any, sinal: int, operacao: str) -> ObjQuantico:
        if _eh_escalar(outro):
            outro = self._identidade(_valor_escalar(outro))
        operando = self._operando(outro)
        if operando is None:
            raise TypeError(f"{operacao} não suportada entre ObjQuantico e {type(outro).__name__}")
        if self.shape != operando.shape:
            raise ValueError(
                f"{operacao} entre formas incompatíveis: {self.shape} e {operando.shape}"
            )
        a, b = self._dados, operando._dados
        if not (sps.issparse(a) and sps.issparse(b)):
            a, b = _como_denso(a), _como_denso(b)
        return self._novo(a + sinal * b, dims=self._dims)

    def __add__(self, outro: Any) -> ObjQuantico:
        return self._somar(outro, +1, "Soma")

    def __radd__(self, outro: Any) -> ObjQuantico:
        return self._somar(outro, +1, "Soma")

    def __sub__(self, outro: Any) -> ObjQuantico:
        return self._somar(outro, -1, "Subtração")

    def __rsub__(self, outro: Any) -> ObjQuantico:
        return (-self)._somar(outro, +1, "Subtração")

    def __neg__(self) -> ObjQuantico:
        return self._novo(-self._dados, dims=self._dims)

    def __pos__(self) -> ObjQuantico:
        return self

    def _produto(self, esquerda: ObjQuantico, direita: ObjQuantico) -> ObjQuantico:
        if esquerda.shape[1] != direita.shape[0]:
            raise ValueError(
                f"Produto entre formas incompatíveis: {esquerda.shape} e {direita.shape}"
            )
        a, b = esquerda._dados, direita._dados
        resultado = a @ b
        if sps.issparse(resultado) and not (sps.issparse(a) and sps.issparse(b)):
            resultado = resultado.toarray()
        return self._novo(resultado, dims=[esquerda._dims[0], direita._dims[1]])

    def __mul__(self, outro: Any) -> ObjQuantico:
        if _eh_escalar(outro):
            return self._novo(self._dados * _valor_escalar(outro), dims=self._dims)
        operando = self._operando(outro)
        if operando is None:
            raise TypeError(
                f"Multiplicação não suportada entre ObjQuantico e {type(outro).__name__}"
            )
        return self._produto(self, operando)

    def __rmul__(self, outro: Any) -> ObjQuantico:
        if _eh_escalar(outro):
            return self._novo(_valor_escalar(outro) * self._dados, dims=self._dims)
        operando = self._operando(outro)
        if operando is None:
            raise TypeError(
                f"Multiplicação não suportada entre {type(outro).__name__} e ObjQuantico"
            )
        return self._produto(operando, self)

    def __truediv__(self, outro: Any) -> ObjQuantico:
        if not _eh_escalar(outro):
            raise TypeError(f"Divisão não suportada entre ObjQuantico e {type(outro).__name__}")
        valor = _valor_escalar(outro)
        if valor == 0:
            raise ZeroDivisionError("divisão de um ObjQuantico por zero")
        return self._novo(self._dados / valor, dims=self._dims)

    def __rtruediv__(self, outro: Any) -> ObjQuantico:
        raise TypeError(
            "Divisão de um número por um ObjQuantico não é definida "
            "(para a inversa, use numpy.linalg.inv(A.full()))."
        )

    def __pow__(self, potencia: Any) -> ObjQuantico:
        if isinstance(potencia, bool) or not isinstance(potencia, numbers.Integral) or potencia < 0:
            raise ValueError("A potência deve ser um inteiro não negativo.")
        self._exigir_quadrada("potência")
        potencia = int(potencia)
        if self.formato == "denso":
            return self._novo(np.linalg.matrix_power(self._dados, potencia), dims=self._dims)
        # Exponenciação binária: log2(n) produtos esparsos.
        resultado = sps.csr_array(
            sps.identity(self.shape[0], format="csr", dtype=self._dados.dtype)
        )
        base = self._dados
        while potencia:
            if potencia & 1:
                resultado = resultado @ base
            potencia >>= 1
            if potencia:
                base = base @ base
        return self._novo(sps.csr_array(resultado), dims=self._dims)

    def __matmul__(self, outro: Any) -> ObjQuantico:
        """Produto tensorial ``A ⊗ B``."""
        if not isinstance(outro, ObjQuantico):
            raise TypeError(f"Operador @ não suportado entre ObjQuantico e {type(outro).__name__}")
        a, b = self._dados, outro._dados
        if sps.issparse(a) and sps.issparse(b):
            dados = sps.csr_array(sps.kron(a, b, format="csr"))
        else:
            dados = np.kron(_como_denso(a), _como_denso(b))
        dims = [self._dims[0] + outro._dims[0], self._dims[1] + outro._dims[1]]
        return self._novo(dados, dims=dims)

    # ---------------------------------------------------------- representação
    def __repr__(self) -> str:
        cabecalho = (
            f"ObjQuantico: tipo={self.tipo}, dim={self.dim()}, shape={self.shape}, "
            f"formato={self.formato}"
        )
        if self.dims != _dims_padrao(self.shape):
            cabecalho += f", dims={self.dims}"
        if self.formato == "esparso":
            cabecalho += f", nnz={self._dados.nnz}"
            if self.shape[0] * self.shape[1] > LIMITE_REPR_ESPARSO:
                return cabecalho
        corpo = np.array2string(self.full(), threshold=200, edgeitems=3, precision=4)
        return f"{cabecalho}\n{corpo}"

    def _repr_latex_(self) -> str:
        """Exibição em LaTeX no Jupyter."""
        if self.latex_representation:
            return f"$$ {_sem_cifrao(self.latex_representation)} $$"
        return f"$$ {latex_matriz(self._dados)} $$"

    # ------------------------------------------------- nomes antigos (obsoletos)
    def traço(self) -> float | complex:
        """Obsoleto: use :meth:`traco`."""
        avisar_obsoleto("ObjQuantico.traço()", "ObjQuantico.traco()")
        return self.traco()

    def Autovalores(self) -> np.ndarray:
        """Obsoleto: use :meth:`autovalores`."""
        avisar_obsoleto("ObjQuantico.Autovalores()", "ObjQuantico.autovalores()")
        return self.autovalores()

    def Autovetores(self) -> np.ndarray:
        """Obsoleto: use :meth:`autovetores`."""
        avisar_obsoleto("ObjQuantico.Autovetores()", "ObjQuantico.autovetores()")
        return self.autovetores()

    def AutoValor_Vetor(self) -> tuple[np.ndarray, np.ndarray]:
        """Obsoleto: use :meth:`autoestados`."""
        avisar_obsoleto("ObjQuantico.AutoValor_Vetor()", "ObjQuantico.autoestados()")
        return self.autoestados()

    def expM(self) -> ObjQuantico:
        """Obsoleto: use :meth:`expm`."""
        avisar_obsoleto("ObjQuantico.expM()", "ObjQuantico.expm()")
        return self.expm()


# ---------------------------------------------------------------------------
# Compatibilidade: ObjQuantico_esparso
# ---------------------------------------------------------------------------
class _MetaEsparso(type):
    """``ObjQuantico_esparso(...)`` cria um ObjQuantico esparso, e
    ``isinstance(obj, ObjQuantico_esparso)`` testa se ``obj`` está no formato esparso."""

    def __instancecheck__(cls, obj: Any) -> bool:
        return isinstance(obj, ObjQuantico) and obj.formato == "esparso"

    def __call__(cls, dados: Any, latex_representation: str | None = None, **kwargs: Any):
        return ObjQuantico(dados, latex_representation, formato="esparso", **kwargs)


class ObjQuantico_esparso(metaclass=_MetaEsparso):
    """Compatibilidade: ``ObjQuantico_esparso(dados)`` é ``ObjQuantico(dados, formato="esparso")``.

    Desde a versão 0.1.0 há uma única classe, :class:`ObjQuantico`, com os dois formatos.
    """
