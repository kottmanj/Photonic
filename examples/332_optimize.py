# @me need git commit 54203a3f58517e90181cc234a6cc60075196ec8b at jax_objective branch

from photonic import PhotonicSetup
import tequila as tq

"""
Set The Parameters here:
"""
S = 1  # Modes will run from -S ... 0 ... +S
qpm = 1  # Qubits per mode
trotter_steps = 1  # number of trotter steps for the BeamSplitter (for S=1, qpm=1 trotter_steps=1 is enough)
simulator = tq.simulators.SimulatorQulacs()  # Pick the Simulator
# Trotterization setup
randomize = False
randomize_component_order = False
join_components = False
factor = 1.0


def construct_hamiltonian(n_qubits):
    """
    results in a lot of terms but is actually just one (just not yet supported in that way)
    """
    H = tq.paulis.QubitHamiltonian()
    for i in range(n_qubits):
        H *= (tq.paulis.I(i) + tq.paulis.Z(i))
    return -(1.0 / 2.0) ** n_qubits * H


def construct_projector(path):
    """
    The projector only on path a which projects onto |000...0><000...0|
    """
    H = tq.paulis.QubitHamiltonian()
    qubits = []
    for m in path.values():
        qubits += m.qubits
    for i in qubits:
        H *= (tq.paulis.I(i) + tq.paulis.Z(i))
    return (1.0 / 2.0) ** len(qubits) * H


if __name__ == "__main__":
    param_dove = 1.0
    param_bs = 0.25
    angle0 = tq.Variable(name="angle0", value=2.214276463967408)#3.141287054029686 / 2)  # this is the optimum
    angle1 = tq.Variable(name="angle1", value=-3.141287054029686)  # this is the optimum

    setup = PhotonicSetup(pathnames=['a', 'b', 'c', 'd'], S=S, qpm=qpm)
    setup.prepare_SPDC_state(path_a='a', path_b='b')
    setup.prepare_SPDC_state(path_a='c', path_b='d')
    setup.add_beamsplitter(path_a='b', path_b='c', t=param_bs, steps=trotter_steps)
    setup.add_doveprism(path='c', t=param_dove)
    setup.add_beamsplitter(path_a='b', path_b='c', t=param_bs, steps=trotter_steps)
    setup.add_parametrized_one_photon_projector(path='a', angles=[angle0, angle1])
    setup.prepare_332_state(path_a='b', path_b='c', path_c='d', daggered=True)

    U = setup.setup
    H = construct_hamiltonian(n_qubits=U.n_qubits)
    P = construct_projector(path=setup.paths['a'])
    E0 = tq.Objective.ExpectationValue(U=U, H=factor * H)
    E1 = tq.Objective.ExpectationValue(U=U, H=P)
    O = E0 / E1

    print(O.extract_variables())
    vE0 = simulator.simulate_objective(E0)
    vE1 = simulator.simulate_objective(E1)
    print("E0=", vE0)
    print("E1=", vE1)
    print("E0/E1", vE0/vE1)

    #O.update_variables(variables={"angle0": 1.0, "angle1": -1.0})
    result = tq.optimizer_scipy.minimize(simulator=simulator, tol=1.e-4, objective=O, samples=None, method="BFGS", silent=False)

    # @me
    # don't do this on clusters
    # save the results!
    result.history.plot()
    result.history.plot('angles')
    result.history.plot('gradients')
