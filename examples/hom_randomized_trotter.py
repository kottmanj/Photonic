"""
If you did not add the location of the code for OpenVQE and Photonic
to your PYTHONPATH you have to do it here
uncomment the line below and add the correct paths
You need to change the paths of course
"""
# import sys
# sys.path.append("/home/jsk/projects/OpenVQE/")
# sys.path.append("/home/jsk/projects/photonic-qc/code/")

from photonic import PhotonicSetup, PhotonicStateVector
from openvqe.simulator.simulator_qiskit import SimulatorQiskit
from openvqe.simulator import Simulator
# parallel env
import multiprocessing as mp

"""
Here we creating Hong-Ou-Mandel States with a single beam splitter
And compare Trotter decompositions where the order has been kept fixed vs randomized order

This is an old version which will not run anymore
keeping it for now

See OpenVQE/examples/randomized_trotter... for more or less the same example
for a single mode and a bit easier
"""

def read_dictionary(filename:str, d:dict=None):
    if d is None:
        d = {}
    with open(filename, 'r') as f:
        for line in f:
            (key, val) = line.split()
            d[str(key)] = int(val)
    return d


class DoIt:
    def __init__(self, S: int, qpm: int, trotter_steps: int, randomize: bool, samples: int, initial_state: str,
                 simulator: Simulator):
        self.S = S
        self.qpm = qpm
        self.trotter_steps = trotter_steps
        self.randomize = randomize
        self.samples = samples
        self.initial_state = initial_state
        self.simulator = simulator

    def __call__(self, *args) -> PhotonicStateVector:
        setup = PhotonicSetup(pathnames=['a', 'b'], S=self.S, qpm=self.qpm)

        order = 0
        if self.randomize is True:
            order = 'randomize'
        # the beam splitter is parametrized as phi=i*pi*t
        setup.add_beamsplitter(path_a='a', path_b='b', t=0.5, steps=self.trotter_steps, order=order)

        return setup.run(samples=self.samples, initial_state=self.initial_state, simulator=self.simulator)


if __name__ == "__main__":

    runs = 2
    nproc = 3

    print("CPU Count is: ", mp.cpu_count())
    if nproc is None:
        nproc = mp.cpu_count()
    pool = mp.Pool(processes=max(1, min(nproc, mp.cpu_count())))
    print(pool._processes, " processes in the pool\n")

    """
    Set The Parameters here:
    """
    parameters = {
        'S': 0,  # Modes will run from -S ... 0 ... +S
        'qpm': 2,  # Qubits per mode
        'initial_state': "|1>_a|1>_b",  # Notation has to be consistent with your S
        'trotter_steps': 1,  # number of trotter steps for the BeamSplitter
        'randomize': True,  # Do or do not randomize
        'samples': 1,  # number of samples to simulate
        'simulator': SimulatorQiskit()  # Pick the Simulator
        # Alternatives
        # SimulatorCirq: Googles simulator
        # SimulatorQiskit: IBM simulator
        # SimulatorPyquil: Rigettis simulator, the quantum virtual machine needs to run in the background
        # Pyquil is broken currently ... Sorry
    }

    counts = pool.map(func=DoIt(**parameters), iterable=range(0, runs))
    print(type(counts), "\n", counts)

    print("collected counts:\n", counts)

    accumulate = None
    for i,c in enumerate(counts):
        if accumulate is None:
            accumulate = c
        else:
            accumulate += c

    counts = accumulate
    print("counts after accumulation:\n", counts)

    counts.plot(title="HOM-Counts for initial state " + parameters['initial_state'],
                label="steps=" + str(parameters['trotter_steps']) + "\nrandomized=" + str(
                    parameters['randomize']) + "\nsamples=" + str(
                    parameters['samples']),
                filename="hom_steps_" + str(parameters['trotter_steps']) + "_randomized_" + str(
                    parameters['randomize']) + "_samples_" + str(
                    parameters['samples']) + ".pdf")
