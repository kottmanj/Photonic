"""
Here we creating Hong-Ou-Mandel States with a single beam splitter
In this example the distribution of the wavefunction is simulated with discrete counts as result
You will need some trotter steps to get good fidelities

I assume that the Trotter decomposition can be improved to get better results (currently the two target states
are asymetric)

Count will differ from run to run and by how you set samples and trotter step
"""

from photonic import PhotonicSetup, PhotonicStateVector
import tequila as tq

if __name__ == "__main__":
    """
    Set The Parameters here:
    """
    S = 0                           # Modes will run from -S ... 0 ... +S
    qpm = 2                         # Qubits per mode
    initial_state="|1>_a|1>_b"      # Notation has to be consistent with your S
    trotter_steps = 20              # number of trotter steps for the BeamSplitter
    samples = 1000                  # number of samples to simulate
    simulator = None                # Pick the Simulator (None -> let tequila do it)
    t = 0.25                        # beam-splitter parameter

    setup = PhotonicSetup(pathnames=['a', 'b'], S=S, qpm=qpm)

    # the beam splitter is parametrized as phi=i*pi*t
    setup.add_beamsplitter(path_a='a', path_b='b', t=t, steps=trotter_steps)

    # need explicit circuit for initial state
    state = setup.initialize_state(state=initial_state)
    # can only do product states right now, alltough more general ones are possible
    # with code adaption
    Ui = tq.QCircuit()
    assert (len(state.state) == 1)
    key = [k for k in state.state.keys()][0]
    for i, q in enumerate(key.array):
        if q == 1:
            Ui += tq.gates.X(target=i)

    # full circuit (initial state plus mapped HOM setup)
    U = Ui + setup.setup + tq.gates.Measurement(target=[0,1,2,3])

    print(U)

    # those are the qubit counts given back by tequila
    qcounts = tq.simulate(U, samples=samples)
    # those are the qubit counts re-interpreted as photonic counts
    pcounts = PhotonicStateVector(paths=setup.paths, state=qcounts)

    print("qubit counts:\n", qcounts)
    print("photon counts:\n", pcounts)

    pcounts.plot(title="HOM-Counts for initial state "+ initial_state)



