"""
Boson sampling as described in the paper
We have 3 Photons in 6 paths
Photons will start in paths a,c,e
"""

import tequila as tq
import photonic
import numpy
from itertools import combinations, permutations
from matplotlib import pyplot as plt
import pickle

S = 0
qpm = 2
trotter_steps = 2

bs_parameters = [
    0.19,
    0.55,
    0.4,
    0.76,
    0.54,
    0.95,
    0.48,
    0.99,
    0.51,
    0.44
]

phases = [
    2.21,
    0.64,
    1.08,
    1.02,
    1.37,
    2.58,
    2.93,
    1.1
]

# convenience
a = 'a'
b = 'b'
c = 'c'
d = 'd'
e = 'e'


def filter_single_photon_counts(state: photonic.PhotonicStateVector, n_photons=3):
    result = dict()
    pathnames = [k for k in state.paths.keys()]

    for comb in combinations(pathnames, n_photons):
        key = ""
        label = ""
        for i in comb:
            key += "|1>_" + str(i)
            label += str(i)
        result[label] = state.get_basis_state(string=key)

    return result


def filter_three_photon_counts(state: photonic.PhotonicStateVector):
    pathnames = [k for k in state.paths.keys()]

    # all states with 3 photons in differnt paths '111'
    result = filter_single_photon_counts(state=state, n_photons=3)

    # all states with 2 photons in one path and 1 photon in another '21'
    for comb in permutations(pathnames, 2):
        key = "|2>_" + str(comb[0]) + "|1>_" + str(comb[1])
        result[key] = state.get_basis_state(string=key)

    # all states with 3 photons in one path
    for path in pathnames:
        key = "|3>_" + str(path)
        result[key] = state.get_basis_state(string=key)

    return result


if __name__ == "__main__":

    # transform phases to pi*t form
    phase_parameters = [phase / numpy.pi for phase in phases]

    # transform beam-splitter parameters to pi*t
    bs_parameters = [numpy.arcsin(p)/numpy.pi for p in bs_parameters]

    checksums = []
    data= []
    for trotter_steps in [10]: # [1, 5, 10, 20, 40, 80, 160, 320]:

        setup = photonic.PhotonicSetup(pathnames=[a, b, c, d, e], S=S, qpm=qpm)

        initial_state = setup.initialize_state("1.0|1>_a|1>_c|1>_e")
        print(initial_state)
        U = tq.circuit.QCircuit()
        assert (len(initial_state.state.keys()) == 1)
        for k, v in initial_state.state.items():
            for i, v in enumerate(k.array):
                if v == 1:
                    U += tq.gates.X(target=i)

        setup.add_circuit(U=U)

        setup.add_beamsplitter(path_a=a, path_b=b, t=bs_parameters[0], phi=0, steps=trotter_steps)
        setup.add_phase_shifter(path=a, t=-1)
        setup.add_phase_shifter(path=b, t=-1)

        setup.add_phase_shifter(path=b, t=-phase_parameters[0])
        setup.add_beamsplitter(path_a=b, path_b=c, t=bs_parameters[1], phi=0, steps=trotter_steps)

        setup.add_phase_shifter(path=a, t=-phase_parameters[1])
        setup.add_beamsplitter(path_a=a, path_b=b, t=bs_parameters[2], phi=0, steps=trotter_steps)

        setup.add_phase_shifter(path=c, t=-phase_parameters[2])
        setup.add_beamsplitter(path_a=c, path_b=d, t=bs_parameters[3], phi=0, steps=trotter_steps)

        setup.add_phase_shifter(path=c, t=-phase_parameters[3])
        setup.add_beamsplitter(path_a=b, path_b=c, t=bs_parameters[4], phi=0, steps=trotter_steps)

        setup.add_beamsplitter(path_a=d, path_b=e, t=bs_parameters[5], phi=0, steps=trotter_steps)

        setup.add_phase_shifter(path=b, t=-phase_parameters[4])
        setup.add_beamsplitter(path_a=a, path_b=b, t=bs_parameters[6], phi=0, steps=trotter_steps)

        setup.add_phase_shifter(path=c, t=-phase_parameters[5])
        setup.add_beamsplitter(path_a=c, path_b=d, t=bs_parameters[7], phi=0, steps=trotter_steps)

        setup.add_phase_shifter(path=b, t=-phase_parameters[6])
        setup.add_beamsplitter(path_a=b, path_b=c, t=bs_parameters[8], phi=0, steps=trotter_steps)

        setup.add_phase_shifter(path=b, t=-phase_parameters[7])
        setup.add_beamsplitter(path_a=a, path_b=b, t=bs_parameters[9], phi=0, steps=trotter_steps)

        result = setup.simulate_wavefunction()

        print("simulated wavefunction is:\n", result)

        all_three_photon_states = filter_three_photon_counts(result)
        # add up probabilities
        p = 0.0
        for k, v in all_three_photon_states.items():
            p += numpy.abs(v) ** 2
        print("|norm|^2=", p)

        filtered = filter_single_photon_counts(result)
        print("filtered:", filtered)

        labels = [k for k in filtered.keys()]
        values = [numpy.abs(v) ** 2 for v in filtered.values()]
        print(labels)
        print(values)

        title = "qpm=" + str(qpm) + "\nsteps=" + str(trotter_steps) + "\nchecksum=" + tq.tools.number_to_string(p)

        print(values[4]/values[7])
        print(values[7]/values[4])

        plt.figure()
        plt.bar(labels, values, label=title)
        plt.legend()
        filename = "boson_sampler_steps_" + str(trotter_steps)
        with open(filename + ".pickle", 'wb') as handle:
            pickle.dump(result, handle, protocol=pickle.HIGHEST_PROTOCOL)
        plt.savefig(filename + ".pdf")
        # will print to terminal, add filename=... to plot to file
        plt.show()

        print(result)
        ace_phase = result.get_basis_state("|1>_a|0>_b|1>_c|0>_d|1>_e")
        print("abe=",result.get_basis_state("|1>_a|1>_b|0>_c|0>_d|1>_e"))
        print("ace=",result.get_basis_state("|1>_a|0>_b|1>_c|0>_d|1>_e"))
        print("bce=",result.get_basis_state("|0>_a|1>_b|1>_c|0>_d|1>_e"))
        checksums.append(p)
        data.append(values)

    # checksums indicate how serious the trotter error is ("unphysical photon loss")
    print("checksums:\n", checksums)



