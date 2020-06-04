
from photonic import creation, anihilation
import tequila as tq

"""
Demonstrating how to generate the Pauli Operators for bosonic creation and annihilation operators
"""

if __name__ == "__main__":

    """
    Get the creation/annihilation operator on qubits labeled by 0 and 1
    """
    qubits = [0,1]
    cop = creation(qubits=qubits)
    aop = anihilation(qubits=qubits)

    print("creation operator for ", qubits)
    print(cop)

    print("annihilation operator for ", qubits)
    print(aop)

    """
    Decompose a general |ket><bra| binary operator
    """

    ket = tq.QubitWaveFunction.from_string("1.0*|001>")
    bra = tq.QubitWaveFunction.from_string("1.0*|100>")

    operator = tq.paulis.KetBra(ket=ket, bra=bra).simplify()

    print("Operator |", ket, "><", bra, "| in binary on ", ket.n_qubits, " qubits:" )
    print(operator)

    """
    Similar but initialized by integers
    """
    ket = tq.QubitWaveFunction.from_int(i=1, n_qubits=3)
    bra = tq.QubitWaveFunction.from_int(i=4, n_qubits=3)

    operator = tq.paulis.KetBra(ket=ket, bra=bra).simplify()

    print("Operator |", ket, "><", bra, "| in binary on ", ket.n_qubits, " qubits:" )
    print(operator)




