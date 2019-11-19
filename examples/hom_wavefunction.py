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
from openvqe.simulators.simulator_cirq import SimulatorCirq
from openvqe.simulators.simulator_pyquil import SimulatorPyquil
from openvqe.circuit.qpic import export_to_pdf
from numpy import pi, sqrt

"""
Here we creating Hong-Ou-Mandel States with a single beam splitter
In this notebook the full wavefunction is simulated
You will need some trotter steps to get good fidelities
"""

if __name__ == "__main__":
    """
    Set The Parameters here:
    """
    S = 0  # Modes will run from -S ... 0 ... +S
    qpm = 2  # Qubits per mode
    trotter_steps = 32  # number of trotter steps for the BeamSplitter
    simulator = SimulatorCirq()  # Pick the Simulator
    # Alternatives
    # SimulatorCirq: Googles simulator
    # SimulatorPyquil: Rigettis simulator, the quantum virtual machine needs to run in the background
    # Pyquil is broken right now. Made too many changes

    """
    Here comes the code:
    """

    setup = PhotonicSetup(pathnames=['a', 'b'], S=S, qpm=qpm)

    # the beam splitter is parametrized as phi=i*pi*t
    setup.add_beamsplitter(path_a='a', path_b='b', t=0.25, steps=trotter_steps)

    #setup.export_to_qpic(filename="hom_setup.qpic")
    #export_to_pdf(filename="hom_setup", circuit="hom_setup")

    # result of the simulation
    wfn = setup.simulate_wavefunction(initial_state="+1.0|1>_a|1>_b", simulator=simulator)

    # this is the state that we would expect
    expected_wfn = setup.initialize_state(state=str(1.0 / sqrt(2)) + "|2>_a|0>_b+" + str(-1.0 / sqrt(2)) + "|0>_a|2>_b")

    print("result  = ", wfn)
    print("ideal   = ", expected_wfn)

    # Compute and print the fidelity
    fidelity = abs(wfn.inner(expected_wfn)) ** 2
    print("fidelity= ", fidelity)
