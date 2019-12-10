from photonic import PhotonicSetup, PhotonicStateVector, PhotonicPaths
from tequila.simulators.simulator_cirq import SimulatorCirq
from tequila.circuit import Variable
from tequila import optimizer_scipy
from tequila import Objective
from tequila import paulis
from tequila import simulators

import typing
import pickle

"""
Set The Parameters here:
"""
S = 1  # Can NOT be changed for this example, Hamiltonian will be wrong otherwise
qpm = 1  # Qubits per mode
trotter_steps = 1  # number of trotter steps for the BeamSplitter
simulator = SimulatorCirq()  # Pick the Simulator
# Trotterization setup
randomize = False
randomize_component_order = False
join_components = False
factor = 1.0


def construct_hamiltonian(state: PhotonicStateVector):
    H = paulis.QubitHamiltonian.init_zero()
    qubit_state = state.state.normalize()
    for k1, v1 in qubit_state.items():
        for k2, v2 in qubit_state.items():
            H += v1.conjugate() * v2 * paulis.decompose_transfer_operator(bra=k1, ket=k2)
    return H

def one_photon_projector(setup: PhotonicSetup):
    #manual for now
    a  = construct_hamiltonian(setup.initialize_state("|000>_a|001>_b|001>_c|001>_d"))
    a += construct_hamiltonian(setup.initialize_state("|000>_a|001>_b|001>_c|010>_d"))
    a += construct_hamiltonian(setup.initialize_state("|000>_a|001>_b|001>_c|100>_d"))

    a += construct_hamiltonian(setup.initialize_state("|000>_a|001>_b|010>_c|001>_d"))
    a += construct_hamiltonian(setup.initialize_state("|000>_a|001>_b|010>_c|010>_d"))
    a += construct_hamiltonian(setup.initialize_state("|000>_a|001>_b|010>_c|100>_d"))

    a += construct_hamiltonian(setup.initialize_state("|000>_a|001>_b|100>_c|001>_d"))
    a += construct_hamiltonian(setup.initialize_state("|000>_a|001>_b|100>_c|010>_d"))
    a += construct_hamiltonian(setup.initialize_state("|000>_a|001>_b|100>_c|100>_d"))

    a  = construct_hamiltonian(setup.initialize_state("|000>_a|010>_b|001>_c|001>_d"))
    a += construct_hamiltonian(setup.initialize_state("|000>_a|010>_b|001>_c|010>_d"))
    a += construct_hamiltonian(setup.initialize_state("|000>_a|010>_b|001>_c|100>_d"))

    a += construct_hamiltonian(setup.initialize_state("|000>_a|010>_b|010>_c|001>_d"))
    a += construct_hamiltonian(setup.initialize_state("|000>_a|010>_b|010>_c|010>_d"))
    a += construct_hamiltonian(setup.initialize_state("|000>_a|010>_b|010>_c|100>_d"))

    a += construct_hamiltonian(setup.initialize_state("|000>_a|010>_b|100>_c|001>_d"))
    a += construct_hamiltonian(setup.initialize_state("|000>_a|010>_b|100>_c|010>_d"))
    a += construct_hamiltonian(setup.initialize_state("|000>_a|010>_b|100>_c|100>_d"))

    a  = construct_hamiltonian(setup.initialize_state("|000>_a|100>_b|001>_c|001>_d"))
    a += construct_hamiltonian(setup.initialize_state("|000>_a|100>_b|001>_c|010>_d"))
    a += construct_hamiltonian(setup.initialize_state("|000>_a|100>_b|001>_c|100>_d"))

    a += construct_hamiltonian(setup.initialize_state("|000>_a|100>_b|010>_c|001>_d"))
    a += construct_hamiltonian(setup.initialize_state("|000>_a|100>_b|010>_c|010>_d"))
    a += construct_hamiltonian(setup.initialize_state("|000>_a|100>_b|010>_c|100>_d"))

    a += construct_hamiltonian(setup.initialize_state("|000>_a|100>_b|100>_c|001>_d"))
    a += construct_hamiltonian(setup.initialize_state("|000>_a|100>_b|100>_c|010>_d"))
    a += construct_hamiltonian(setup.initialize_state("|000>_a|100>_b|100>_c|100>_d"))
    return a
    b  = construct_hamiltonian(setup.initialize_state("|001>_b"))
    b += construct_hamiltonian(setup.initialize_state("|010>_b"))
    b += construct_hamiltonian(setup.initialize_state("|100>_b"))
    c  = construct_hamiltonian(setup.initialize_state("|001>_c"))
    c += construct_hamiltonian(setup.initialize_state("|010>_c"))
    c += construct_hamiltonian(setup.initialize_state("|100>_c"))
    d  = construct_hamiltonian(setup.initialize_state("|001>_d"))
    d += construct_hamiltonian(setup.initialize_state("|010>_d"))
    d += construct_hamiltonian(setup.initialize_state("|100>_d"))
    return a*b*c*d




if __name__ == "__main__":
    param_dove = Variable(name="t", value=1.0)
    angle0 = Variable(name="angle0", value=3.141287054029686/2)
    angle1 = Variable(name="angle1", value=-3.141287054029686)
    setup = PhotonicSetup(pathnames=['a', 'b', 'c', 'd'], S=S, qpm=qpm)
    setup.prepare_SPDC_state(path_a='a', path_b='b')
    setup.prepare_SPDC_state(path_a='c', path_b='d')
    setup.add_beamsplitter(path_a='b', path_b='c', t=0.25, steps=trotter_steps)
    setup.add_doveprism(path='c', t=param_dove)
    setup.add_beamsplitter(path_a='b', path_b='c', t=0.25, steps=trotter_steps)
    setup.add_parametrized_one_photon_projector(path='a', angles=[angle0, angle1])
    #setup.add_one_photon_projector(path='a', daggered=True, delete_active_path=True)
    #setup.prepare_332_state(path_a='b', path_b='c', path_c='d', daggered=True)

    target_state = setup.initialize_state(
        "1.0|100>_b|001>_c|100>_d+1.0|010>_b|010>_c|010>_d+1.0|100>_b|100>_c|001>_d")
    U = setup.setup
    print("Setup size (not compiled)=", len(U.gates))
    H = construct_hamiltonian(state=target_state)
    print("len(H) = ", len(H.hamiltonian.terms.keys()))
    P = one_photon_projector(setup=setup)
    print("len(P) = ", len(P.hamiltonian.terms.keys()))
    H = -1.0*H*P
    print("len(H) = ", len(H.hamiltonian.terms.keys()))
    O = Objective(unitaries=U, observable=factor * H)
    print(O.extract_variables())

    E = simulators.SimulatorQulacs().simulate_objective(objective=O)
    print("E=", E)
    O.update_variables(variables={'angle0':2.214276463967408})
    print(O.extract_variables())
    E = simulators.SimulatorQulacs().simulate_objective(objective=O)
    print("E=", E)

    result = optimizer_scipy.minimize(simulator=simulator, tol=1.e-1, objective=O, samples=None, method="BFGS")

    result.history.plot()
    result.history.plot('angles')
    result.history.plot('gradients')
