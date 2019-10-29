from photonic import PhotonicSetup, PhotonicStateVector, PhotonicPaths
from openvqe.simulator.simulator_qiskit import SimulatorQiskit
from openvqe.simulator.simulator_cirq import SimulatorCirq
from photonic.elements import PhotonicHeralder
from openvqe import BitString

if __name__ == "__main__":
    """
    Set The Parameters here:
    """
    S = 1  # Modes will run from -S ... 0 ... +S
    qpm = 1  # Qubits per mode
    trotter_steps = 100  # number of trotter steps for the BeamSplitter
    samples = 10000  # number of samples to simulate
    simulator = SimulatorQiskit()  # Pick the Simulator
    # Alternatives
    # SimulatorCirq: Googles simulator
    # SimulatorQiskit: IBM simulator

    # Trotterization setup
    randomize = False
    randomize_component_order = False
    join_components = False

    """
    Here comes the actual code
    """

    setup = PhotonicSetup(pathnames=['a', 'b', 'c', 'd'], S=S, qpm=qpm)
    setup.prepare_SPDC_state(path_a='a', path_b='b')
    setup.prepare_SPDC_state(path_a='c', path_b='d')
    setup.add_beamsplitter(path_a='b', path_b='c', t=0.25, steps=trotter_steps, randomize=randomize, join_components=join_components, randomize_component_order=randomize_component_order)
    setup.add_doveprism(path='c', mode=0, t=1.0)
    setup.add_beamsplitter(path_a='b', path_b='c', t=0.25, steps=trotter_steps, randomize=randomize, join_components=join_components, randomize_component_order=randomize_component_order)
    #setup.prepare_332_state(path_a='b', path_b='c', path_c='d', daggered=True)
    #setup.add_one_photon_projector(path='a', daggered=True)


    counts = setup.run(samples=samples, simulator=simulator)

    bcd = PhotonicPaths(path_names=['a', 'b', 'c', 'd'], S=S, qpm=qpm)
    heralder = PhotonicHeralder(paths=bcd)
    healded = PhotonicStateVector(state=heralder(counts.state), paths=bcd)

    healded.plot()

    all_zero = BitString.from_int(integer=0, nbits=setup.n_qubits)
    c = counts.state[all_zero]
    print("c=",c)
