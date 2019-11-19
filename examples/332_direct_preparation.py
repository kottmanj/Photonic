from photonic import PhotonicSetup, PhotonicStateVector, PhotonicPaths
from openvqe.simulators.simulator_qiskit import SimulatorQiskit
from openvqe.simulators.simulator_cirq import SimulatorCirq
from photonic.elements import PhotonicHeralder
from openvqe import BitString
from openvqe.circuit import Variable
from openvqe.circuit.qpic import export_to_pdf

from openvqe.apps.unary_state_prep import UnaryStatePrep

from openvqe import gates

if __name__ == "__main__":
    S = 1  # Modes will run from -S ... 0 ... +S
    qpm = 2  # Qubits per mode

    setup = PhotonicSetup(pathnames=['a', 'b', 'c'], S=S, qpm=qpm)
    setup.prepare_332_state(path_a='a', path_b='b', path_c='c', daggered=False)
    wfn = setup.simulate_wavefunction()

    print("|332> = ", wfn)

