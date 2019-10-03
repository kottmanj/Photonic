"""
If you did not add the location of the code for OpenVQE and Photonic
to your PYTHONPATH you have to do it here
uncomment the line below and add the correct paths
You need to change the paths of course
"""
#import sys
#sys.path.append("/home/jsk/projects/OpenVQE/")
#sys.path.append("/home/jsk/projects/photonic-qc/code/")

from photonic import creation, anihilation, decompose_transfer_operator
from openvqe import BitString

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

    ket = BitString.from_binary(binary="001")
    bra = BitString.from_binary(binary="100")

    operator = decompose_transfer_operator(ket=ket, bra=bra)

    print("Operator |", ket, "><", bra, "| in binary on ", ket.nbits, " qubits:" )
    print(operator)

    """
    Similar but initialized by integers
    """
    ket = BitString.from_int(integer=1, nbits=3)
    bra = BitString.from_int(integer=4, nbits=3)

    operator = decompose_transfer_operator(ket=ket, bra=bra)

    print("Operator |", ket, "><", bra, "| in binary on ", ket.nbits, " qubits:" )
    print(operator)




