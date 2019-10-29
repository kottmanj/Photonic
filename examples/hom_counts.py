"""
If you did not add the location of the code for OpenVQE and Photonic
to your PYTHONPATH you have to do it here
uncomment the line below and add the correct paths
You need to change the paths of course
"""
#import sys
#sys.path.append("/home/jsk/projects/OpenVQE/")
#sys.path.append("/home/jsk/projects/photonic-qc/code/")

from photonic import PhotonicSetup, PhotonicStateVector
from openvqe.simulator.simulator_cirq import SimulatorCirq
from openvqe.simulator.simulator_qiskit import SimulatorQiskit
from numpy import pi, sqrt

"""
Here we creating Hong-Ou-Mandel States with a single beam splitter
In this notebook the distribution of the wavefunction is simulated with discrete counts as result
You will need some trotter steps to get good fidelities

I assume that the Trotter decomposition can be improved to get better results (currently the two target states
are asymetric)

Count will differ from run to run and by how you set samples and trotter step
"""

if __name__ == "__main__":
    """
    Set The Parameters here:
    """
    S = 0                           # Modes will run from -S ... 0 ... +S
    qpm = 2                         # Qubits per mode
    initial_state="|1>_a|1>_b"      # Notation has to be consistent with your S
    trotter_steps = 2               # number of trotter steps for the BeamSplitter
    samples = 100                   # number of samples to simulate
    simulator = SimulatorQiskit()   # Pick the Simulator
    # Alternatives
    # SimulatorCirq: Googles simulator
    # SimulatorQiskit: IBM simulator
    # SimulatorPyquil: Rigettis simulator, the quantum virtual machine needs to run in the background
    # Pyquil is broken currently ... Sorry


    setup = PhotonicSetup(pathnames=['a', 'b'], S=S, qpm=qpm)

    # the beam splitter is parametrized as phi=i*pi*t
    setup.add_beamsplitter(path_a='a', path_b='b', t=0.25, steps=trotter_steps)

    # need explicit circuit for initial state
    counts = setup.run(samples=100, initial_state=initial_state, simulator=simulator)
    print("counts=", counts)
    counts.plot(title="HOM-Counts for initial state "+ initial_state)

