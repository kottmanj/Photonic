from photonic import PhotonicSetup, PhotonicStateVector, PhotonicPaths
from openvqe.simulator.simulator_qiskit import SimulatorQiskit
from openvqe.simulator.simulator_cirq import SimulatorCirq
from photonic.elements import PhotonicHeralder
from openvqe import BitString
from openvqe.circuit import Variable

if __name__ == "__main__":

    for t in [0.0, 0.25, 0.5, 0.75, 1.0]:

        """
        Set The Parameters here:
        """
        S = 1  # Modes will run from -S ... 0 ... +S
        qpm = 1  # Qubits per mode
        trotter_steps = 50  # number of trotter steps for the BeamSplitter
        samples = 100000  # number of samples to simulate
        simulator = SimulatorCirq()  # Pick the Simulator
        # Alternatives
        # SimulatorCirq: Googles simulator
        # SimulatorQiskit: IBM simulator

        param_dove = Variable(name="t", value=t)

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
        setup.add_beamsplitter(path_a='b', path_b='c', t=0.25, steps=trotter_steps, randomize=randomize,
                                join_components=join_components, randomize_component_order=randomize_component_order)
        setup.add_doveprism(path='c', t=param_dove)
        setup.add_beamsplitter(path_a='b', path_b='c', t=0.25, steps=trotter_steps, randomize=randomize,
                                join_components=join_components, randomize_component_order=randomize_component_order)
        setup.add_one_photon_projector(path='a', daggered=True, delete_active_path=True)

        # this is not exactly the same state as this setup prepares
        # check conventions!
        #setup.prepare_332_state(path_a='b', path_b='c', path_c='d', daggered=True)

        parameters = setup.extract_parameters()
        print("parameters:\n", parameters)

        counts = setup.run(samples=samples, simulator=simulator)

        counts.plot()
        F = 0.0
        valid = ['|000>_a|000>_b|000>_c|000>_d']
        for k, v in counts._state.items():
            if counts.interpret_bitstring(i=k) in valid:
                F += v

        print("F=", F)

        # print(counts.state[BitString.from_int(integer=0)])
        # bcd = PhotonicPaths(path_names=['b', 'c', 'd'], S=S, qpm=qpm)
        # heralder = PhotonicHeralder(paths=bcd)
        # heralded = PhotonicStateVector(state=heralder(counts.state), paths=bcd)
        # heralded.plot()

        F = 0.0
        # valid = ['|010>_b|010>_c|010>_d', '|100>_b|001>_c|100>_d', '|100>_b|100>_c|001>_d']
        # valid = ['|000>_a|000>_b|000>_c|000>_d']
        # for k, v in heralded._state.items():
        #     if heralded.interpret_bitstring(i=k) in valid:
        #         F += v
        #
        # print("F=", F)
