# @me need git commit 54203a3f58517e90181cc234a6cc60075196ec8b at jax_objective branch

from photonic import PhotonicSetup, PhotonicStateVector
import tequila as tq

"""
Set The Parameters here:
"""
S = 1  # Can NOT be changed for this example, Hamiltonian will be wrong otherwise (or you change the string initialization of the target state below)
qpm = 1  # Qubits per mode
trotter_steps = 1  # number of trotter steps for the BeamSplitter (for S=1 and qpm=1, one trotter step is actually enough)
simulator = tq.simulators.SimulatorQulacs()  # Pick the Simulator
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

def one_photon_projector(setup: PhotonicSetup):
    """
    Path A is rotated to 000 so this is on purpose
    Currently that is the easiest way to initialize the Hamiltonian
    Terms could be reduced by far in exploiting structure and commuting cliques
    This is just the easiest way to get what I want
    """
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
    param_dove = 1.0# Variable(name="t", value=1.0) # 1.0 is the optimal value
    angle0 = tq.Variable(name="angle0", value=3.141287054029686/2)
    angle1 = tq.Variable(name="angle1", value=-3.141287054029686)
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
    H = -1.0*H*P # this operations takes a while
    print("len(H) = ", len(H.hamiltonian.terms.keys()))

    E0 = tq.Objective.ExpectationValue(U=U, H=H)
    E1 = tq.Objective.ExpectationValue(U=U, H=P)
    O = E0/E1
    print(O.extract_variables())

    O.update_variables(variables={'angle0': 3.141287054029686/2, 'angle1': -3.141287054029686})
    E = simulator.simulate_objective(objective=O) # this is the 'real' minimum which should have fidelity (energy) -1 with postselection
    print("E=", E)
    O.update_variables(variables={'angle0': 2.214276463967408}) # this is the 'fake' minimum which becomes global without post selection, here it should be above -1
    print(O.extract_variables())
    E = simulator.simulate_objective(objective=O)
    print("E=", E)

    # whatever starting conditions you want to have
    O.update_variables(variables={'angle0': 1.0, 'angle1': -1.0})
    result = tq.optimizer_scipy.minimize(simulator=simulator, tol=1.e-1, objective=O, samples=None, method="BFGS")

    result.history.plot()
    result.history.plot('angles')
    result.history.plot('gradients')
