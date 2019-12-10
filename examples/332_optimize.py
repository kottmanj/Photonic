from photonic import PhotonicSetup
from tequila.simulators.simulator_cirq import SimulatorCirq
from tequila.circuit import Variable
from tequila import optimizer_scipy
from tequila import Objective
from tequila import paulis
from tequila import simulators

import pickle


"""
Set The Parameters here:
"""
S = 1  # Modes will run from -S ... 0 ... +S
qpm = 1  # Qubits per mode
trotter_steps = 3  # number of trotter steps for the BeamSplitter
simulator = simulators.SimulatorQulacs()  # Pick the Simulator
# Trotterization setup
randomize = False
randomize_component_order = False
join_components = False
factor = 1.0


def construct_hamiltonian(n_qubits):
    H = paulis.QubitHamiltonian()
    for i in range(n_qubits):
        H *= (paulis.I(i) + paulis.Z(i))
    return -(1.0 / 2.0) ** n_qubits * H

def construct_projector(path):
    """
    The projector on path a which projects onto |000...0><000...0|
    """
    H = paulis.QubitHamiltonian()
    qubits = []
    for m in path.values():
        qubits += m.qubits
    for i in qubits:
        H *= (paulis.I(i) + paulis.Z(i))
    return  (1.0 / 2.0) ** len(qubits) * H

if __name__ == "__main__":
    param_dove = Variable(name="t", value=1.0)

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
    P = construct_projector(path=setup.paths['a'])
    E0 = Objective.ExpectationValue(U=U, H=factor*H)
    E1 = Objective.ExpectationValue(U=U, H=P)
    O = E0/E1
    print(O.extract_variables())

    E = simulators.SimulatorQulacs().simulate_objective(objective=E0)
    print("E0=", E)
    E = simulators.SimulatorQulacs().simulate_objective(objective=E1)
    print("E1=", E)
    E = simulators.SimulatorQulacs().simulate_objective(objective=O)
    print("O=", E)

    result = optimizer_scipy.minimize(simulator=simulator, tol=1.e-3, objective=O, samples=None, method="BFGS", silent=False)

    result.history.plot()
    result.history.plot('angles')
    result.history.plot('gradients')
