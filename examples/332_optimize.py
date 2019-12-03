from photonic import PhotonicSetup
from tequila.simulators.simulator_cirq import SimulatorCirq
from tequila.circuit import Variable
from tequila import optimizer_scipy
from tequila import Objective
from tequila import paulis


"""
Set The Parameters here:
"""
S = 1  # Modes will run from -S ... 0 ... +S
qpm = 1  # Qubits per mode
trotter_steps = 1  # number of trotter steps for the BeamSplitter
simulator = SimulatorCirq()  # Pick the Simulator
# Trotterization setup
randomize = False
randomize_component_order = False
join_components = False
factor = 1000.0


def construct_hamiltonian(n_qubits):
    H = paulis.QubitHamiltonian()
    for i in range(n_qubits):
        H *= (paulis.I(i) + paulis.Z(i))
    return -(1.0 / 2.0) ** n_qubits * H


if __name__ == "__main__":
    param_dove = Variable(name="t", value=0.25)

    setup = PhotonicSetup(pathnames=['a', 'b', 'c', 'd'], S=S, qpm=qpm)
    setup.prepare_SPDC_state(path_a='a', path_b='b')
    setup.prepare_SPDC_state(path_a='c', path_b='d')
    setup.add_beamsplitter(path_a='b', path_b='c', t=0.25, steps=trotter_steps)
    setup.add_doveprism(path='c', t=param_dove)
    setup.add_beamsplitter(path_a='b', path_b='c', t=0.25, steps=trotter_steps)
    setup.add_one_photon_projector(path='a', daggered=True, delete_active_path=True)
    setup.prepare_332_state(path_a='b', path_b='c', path_c='d', daggered=True)

    U = setup.setup
    H = construct_hamiltonian(n_qubits=U.n_qubits)
    O = Objective(unitaries=U, observable=factor * H)

    print(O.extract_variables())

    result = optimizer_scipy.minimize(simulator=simulator, tol=1.e-1, objective=O, samples=None, method="TNC")

    result.history.plot()
    result.history.plot('angles')
    result.history.plot('gradients')
