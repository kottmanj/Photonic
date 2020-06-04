"""
Some illustrations on randomized Trotter Decompositions

Here we simulate the process

|0101> --> 1.0/sqrt(2)*(|1000> + |0010>)

through the unitary operator

U = exp(i(c_0*a_1 - c_1*a_0))
where c and a are creation/annihilation operator acting on modes
encoded into 2-qubits each

This means:
|0101> : mode a is occupied by one quanta as well as mode b -> |1>_a|1>_b
|1000> : mode a is occupied by two quanta, mode b is unoccupied
|0001> : mode b is occupied by two quanta, mode a is unoccupied

Using randomization the balance between the two states is significantly improved

Since for the randomization we need to take single samples each time, as we would on real hardware,
this example is especially slow. For that reason the evaluation of the circuits are parallelized here.


"""
import sys
from read_dict import read_dictionary

from openvqe.simulator.simulator_qiskit import SimulatorQiskit, QubitWaveFunction
from openvqe.circuit import gates
from openvqe.hamiltonian import QubitHamiltonian, paulis
from openvqe.circuit.exponential_gate import DecompositionFirstOrderTrotter
from openvqe.tools import plotters
from openvqe import typing
from openvqe import numpy
from openvqe import dataclass

import multiprocessing as mp


def anihilation(qubits: typing.List[int]) -> QubitHamiltonian:
    max_occ = 2 ** len(qubits) - 1
    result = QubitHamiltonian.init_zero()
    for occ in range(max_occ):
        c = numpy.sqrt(occ + 1)
        result += c * paulis.decompose_transfer_operator(ket=occ + 1, bra=occ, qubits=qubits)
    return result


def creation(qubits: typing.List[int]) -> QubitHamiltonian:
    max_occ = 2 ** len(qubits) - 1
    result = QubitHamiltonian.init_zero()
    for occ in range(max_occ):
        c = numpy.sqrt(occ + 1)
        result += c * paulis.decompose_transfer_operator(ket=occ, bra=occ + 1, qubits=qubits)
    return result


@dataclass
class DoIt:

    trotter_steps:int
    randomize:bool
    randomize_component_order:bool
    join_components:bool
    division:int

    def __call__(self, *args, **kwargs ) -> QubitWaveFunction:
        trotter = DecompositionFirstOrderTrotter(steps=self.trotter_steps, randomize=self.randomize,
                                                 randomize_component_order=self.randomize_component_order,
                                                 join_components=self.join_components)
        generators = generator_division[self.division]
        U = gates.X(1) + gates.X(3)
        U += trotter(generators=generators)
        U += gates.Measurement(target=qubits_a + qubits_b)
        result = SimulatorQiskit().sample(abstract_circuit=U, samples=1)
        return result.counts


if __name__ == "__main__":
    qubits_a = [0, 1]
    qubits_b = [2, 3]
    H_0 = 1.0j * numpy.pi / 2 * (
            creation(qubits=qubits_a) * anihilation(qubits=qubits_b) - anihilation(qubits=qubits_a) * creation(
        qubits=qubits_b))
    H_1 = -1.0j * numpy.pi / 2 * (
            creation(qubits=qubits_b) * anihilation(qubits=qubits_a) - anihilation(qubits=qubits_b) * creation(
        qubits=qubits_a))
    print("H_0       =", H_0)  # biases 0010
    print("H_1       =", H_1)  # biases 1000
    print("commutator=", H_0 * H_1 - H_1 * H_0)

    # different ways to initialize which generate formally the same operator
    # pick one by commenting out the rest
    generator_division = []
    generator_division.append([H_0])  # strong bias on 0010
    generator_division.append([H_1])  # strong bias on 1000
    generator_division.append([0.5 * H_0, 0.5 * H_1])  # bias on 1000
    generator_division.append([0.5 * H_0, 0.5 * H_1])  # bias on 0010

    # Parameters
    parameters = {
        'trotter_steps': 1,
        'randomize': False,
        'randomize_component_order': False,  # if there is more than one generator the order of the list is randomized
        'join_components': False,
        # if there is more than one generator this handles how the multiple generators are trotterized
        # joined means the trotterization goes as: Trotter(U(H_0+H_1)) while False results in Trotter(U(H_0))*Trotter(U(H_1))
        # Note that for a single Trotter step this has no effect
        'division':0
    }
    
    # read from the outside
    arr = sys.argv[1].split(',')
    filename=None
    for a in arr:
        if 'filename=' in a:
            filename=a.split('=')[1]
    if filename is not None:
        print("found filename=", filename)
        parameters = read_dictionary(filename, parameters)
    else:
        raise Exception("give a filename when you call as python ... filename=...")

    # set up parallel environment
    samples = 1000
    nproc = None  # set this to None to use all available processes (better not do it on a laptop)

    print("CPU Count is: ", mp.cpu_count())
    if nproc is None:
        nproc = mp.cpu_count()
    print("will use ", nproc, " processes")
    nproc = min(nproc, mp.cpu_count())
    pool = mp.Pool(processes=nproc)

    # run
    all_counts = pool.map(func=DoIt(**parameters), iterable=range(0, samples))

    # accumulate results
    counts = QubitWaveFunction()
    for c in all_counts:
        counts += c
    
    outfile = filename+".pdf"
    plotters.plot_counts(filename=outfile, counts=counts, label_with_integers=False)
