# @me need git commit 54203a3f58517e90181cc234a6cc60075196ec8b at jax_objective branch

from photonic import PhotonicSetup, PhotonicStateVector
import tequila as tq
import pickle, numpy

"""
Set The Parameters here:
"""
S = 1  # Can NOT be changed for this example, Hamiltonian will be wrong otherwise (or you change the string initialization of the target state below)
qpm = 1  # Qubits per mode
trotter_steps = 1  # number of trotter steps for the BeamSplitter (for S=1 and qpm=1, one trotter step is actually enough)
# Trotterization setup
randomize = False
randomize_component_order = False
join_components = False
factor = 1.0


def construct_hamiltonian(state: PhotonicStateVector):
    H = tq.paulis.QubitHamiltonian.init_zero()
    qubit_state = state.state.normalize()
    for k1, v1 in qubit_state.items():
        for k2, v2 in qubit_state.items():
            H += v1.conjugate() * v2 * tq.paulis.decompose_transfer_operator(bra=k1, ket=k2)
    return H


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


def one_photon_projector(path_qubits):
    def plus(i): return 0.5 * (tq.paulis.I(path_qubits[i]) + tq.paulis.Z(path_qubits[i]))

    def minus(i): return 0.5 * (tq.paulis.I(path_qubits[i]) - tq.paulis.Z(path_qubits[i]))

    return minus(0) * plus(1) * plus(2) + plus(0) * minus(1) * plus(2) + plus(0) * plus(1) * minus(2)


if __name__ == "__main__":

    Ptest = one_photon_projector([0, 1, 2])
    print(Ptest, "\n", Ptest * Ptest, "\n", Ptest * Ptest - Ptest)
    Ptest *= one_photon_projector([3, 4, 5])
    print("\n", Ptest, "\n", Ptest * Ptest, "\n", Ptest * Ptest - Ptest)

    param_dove = 1.0  # Variable(name="t", value=1.0) # 1.0 is the optimal value
    angle0 = tq.Variable(name="angle0")
    angle1 = tq.Variable(name="angle1")
    setup = PhotonicSetup(pathnames=['a', 'b', 'c', 'd'], S=S, qpm=qpm)
    setup.prepare_SPDC_state(path_a='a', path_b='b')
    setup.prepare_SPDC_state(path_a='c', path_b='d')
    setup.add_beamsplitter(path_a='b', path_b='c', t=0.25, steps=trotter_steps)
    setup.add_doveprism(path='c', t=param_dove)
    setup.add_beamsplitter(path_a='b', path_b='c', t=0.25, steps=trotter_steps)
    setup.add_parametrized_one_photon_projector(path='a', angles=[angle0, angle1])
    # setup.add_one_photon_projector(path='a', daggered=True, delete_active_path=True)
    # setup.prepare_332_state(path_a='b', path_b='c', path_c='d', daggered=True)

    target_state = setup.initialize_state(
        "1.0|100>_b|001>_c|100>_d+1.0|010>_b|010>_c|010>_d+1.0|100>_b|100>_c|001>_d")
    U = setup.setup
    print("Setup size (not compiled)=", len(U.gates))
    H = construct_hamiltonian(state=target_state)
    print("len(H) = ", len(H.hamiltonian.terms.keys()), " hermitian: ", H.is_hermitian())
    P1 = tq.gates.QubitHamiltonian.init_unit()
    for qubits in [[3, 4, 5], [6, 7, 8], [9, 10, 11]]:
        P1 *= one_photon_projector(path_qubits=qubits)  # this takes a while
    print("len(P1) = ", len(P1.hamiltonian.terms.keys()), " hermitian: ", P1.is_hermitian())  # , " PP - P ", P1*P1-P1)
    P = construct_projector(setup.paths['a'])
    print("len(P) = ", len(P.hamiltonian.terms.keys()), " hermitian: ", P.is_hermitian())  # , " PP - P ", P*P-P)
    P = P * P1
    print("len(P*P1) = ", len(P.hamiltonian.terms.keys()), " hermitian: ", P.is_hermitian())  # , " PP - P ", P*P-P)
    print("len(P*P1) = ", len(P.simplify(threshold=1.e-6)), " hermitian: ", P.is_hermitian())  # , " PP - P ", P*P-P)
    H = -1.0 * H * P  # this operations takes a while
    print("len(H) = ", len(H.hamiltonian.terms.keys()), " hermitian: ", H.is_hermitian())
    print("len(H) = ", len(H.hamiltonian.terms.keys()))

    E0 = tq.Objective.ExpectationValue(U=U, H=H)
    E1 = tq.Objective.ExpectationValue(U=U, H=P)
    O = E0 / E1
    print(O.extract_variables())

    variables = {'angle0': 3.141287054029686 / 2, 'angle1': -3.141287054029686}
    # this is the 'real' minimum which should have fidelity (energy) -1 with postselection
    E = tq.simulate(O, variables)
    print("E=", E)
    # this is the 'fake' minimum which becomes global without post selection, here it should be above -1
    variables['angle0'] = 2.214276463967408
    E = tq.simulate(O, variables)
    print("E=", E)

    # whatever starting conditions you want to have
    O.update_variables(variables={'angle0': 0.01, 'angle1': 0.01})
    method_bounds = {"angle0", (0, 2.1 * numpy.pi), "angle1", (0, 2.1 * numpy.pi)}
    result = tq.optimizer_scipy.minimize(tol=1.e-4, objective=O, method="L-BFGS-B", silent=False)

    with open("332_optimize_direct.pickle", "wb") as f:
        pickle.dump(result.history, f, pickle.HIGHEST_PROTOCOL)

    result.history.plot()
    result.history.plot('angles')
    result.history.plot('gradients')
