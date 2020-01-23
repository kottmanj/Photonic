"""
This is the GHZ setup with optimized parameters
"""
import photonic  # works with 9e2199848d2f1757ae3f78892e0912787aadf5dd
import tequila as tq  # and corresponding acca734d6a6dcf70c19bc2711dc4ce23f91ef242
import numpy

# parameters
S = 1
qpm = 1  # 2
steps = 10  # 10

# convenience
a = "a"
b = "b"
c = "c"
d = "d"


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
    setup = photonic.PhotonicSetup(pathnames=['a', 'b', 'c'], S=S, qpm=qpm)
    setup.prepare_332_state(path_a='a', path_b='b', path_c='c', daggered=False)
    wfn_332 = setup.simulate_wavefunction()

    setup = photonic.PhotonicSetup(pathnames=[a, b, c, d], qpm=qpm, S=S)

    setup.prepare_SPDC_state(path_a=a, path_b=b)
    setup.prepare_SPDC_state(path_a=c, path_b=d)

    setup.add_beamsplitter(path_a=b, path_b=c, t=0.25, steps=steps)
    setup.add_doveprism(path=c, t=1.0)
    setup.add_beamsplitter(path_a=b, path_b=c, t=0.25, steps=steps)

    # setup.add_mirror(path=b) # add this for the ++- 000 +-+ 332 state
    # setup.prepare_332_state(path_a=b, path_b=c, path_c=d, daggered=True)
    # 2.214269984020705 -> fake minimum (minimum without post-selection)
    # 3.141287054029686 / 2 -> real post-selected minimum
    # setup.add_parametrized_one_photon_projector(path=a, angles=[3.141287054029686 / 2, -3.141287054029686])
    setup.add_parametrized_one_photon_projector(path=a, angles=[0.0, -numpy.pi / 2])
    # setup.add_one_photon_projector(path=a, daggered=True, delete_active_path=True)

    setup.export_to_qpic(filename="332_setup")

    wfn = setup.simulate_wavefunction()
    print("photnic-wfn=", wfn)
    # projected = photonic.PhotonicStateVector(state=setup.heralding(wfn.state), paths=setup.heralding.reduced_paths)
    P = construct_projector(path=setup.paths["a"])
    print("P  =", P)
    print("P^2=", P * P)
    print("|wfn> =", wfn.state)
    Pwfn = wfn.state.apply_qubitoperator(operator=P)
    print("P|wfn>=", Pwfn)
    projected = photonic.PhotonicStateVector(state=Pwfn, paths=setup.paths)
    projected = photonic.PhotonicStateVector(state=setup.heralding(projected.state),
                                             paths=setup.heralding.reduced_paths)
    heralder = photonic.elements.PhotonicHeralder(paths=projected.paths)
    heralded = photonic.PhotonicStateVector(state=heralder(projected.state), paths=projected.paths)

    print("full-wfn   \n", wfn, "\nS^2=", wfn_332.inner(wfn) ** 2)
    print("projected  \n", projected, "\nS^2=", wfn_332.inner(projected) ** 2)
    print("normalized \n", projected.normalize(),"\nS^2=", wfn_332.inner(projected.normalize()) **2 )
    print("heralded   \n", heralded)
    print("normalized \n", heralded.normalize())
