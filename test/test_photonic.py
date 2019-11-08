from openvqe.simulator import QubitWaveFunction
from photonic import PhotonicPaths, PhotonicSetup, PhotonicStateVector
from numpy import pi, exp, sqrt
from openvqe.simulator.simulator_cirq import SimulatorCirq
from openvqe import BitString

import pytest


def test_notation(silent=True):
    qpm = 2
    S = 2

    # State |-201>_(abc) represented with 2 qubits per mode
    # in Qubits
    # |01 00 00 00 00 | 00 00 01 00 00 | 00 00 00 01 00 >
    test1 = BitString.from_binary(binary='010000000000000100000000000100')
    paths = PhotonicPaths(path_names=['a', 'b', 'c'], S=S, qpm=qpm)

    wfn1 = QubitWaveFunction.from_int(i=test1)
    test1x = PhotonicStateVector(paths=paths, state=wfn1)
    test1y = PhotonicStateVector.from_string(paths=paths, string='1.0|10000>_a|00100>_b|00010>_c')
    if not silent:
        print("got      = ", test1x)
        print("expected = ", test1y)
    assert (test1x == test1y)

    # Do a 332 State:
    # Photonic notation: (one photon in each mode and I added -2 and +2 modes)
    # |1-11>_a+|000>_b+|-111>_c
    # Qudit Notation: With modes -2 ... 2
    #   | 0 0 0 1 0 >_a | 0 1 0 0 0 >_b | 0 0 0 1 0 >_c
    # + | 0 0 1 0 0 >_a | 0 0 1 0 0 >_b | 0 0 1 0 0 >_c
    # + | 0 1 0 0 0 >_a | 0 0 0 1 0 >_b | 0 0 0 1 0 >_c
    # Qubit notation: (using 2 qubits for each mode)
    #   | 00 00 00 01 00 >_a | 00 01 00 00 00 >_b | 00 00 00 01 00 >_c
    # + | 00 00 01 00 00 >_a | 00 00 01 00 00 >_b | 00 00 01 00 00 >_c
    # + | 00 01 00 00 00 >_a | 00 00 00 01 00 >_b | 00 00 00 01 00 >_c

    string = '1.0|00010>_a|01000>b|00010>_c+1.0|00100>_a|00100>_b|00100>_c+1.0|01000>_a|00010>_b|00010>_c'
    test_332x = PhotonicStateVector.from_string(paths=paths, string=string)

    q1 = BitString.from_binary('000000010000010000000000000100')
    q2 = BitString.from_binary('000001000000000100000000010000')
    q3 = BitString.from_binary('000100000000000001000000000100')
    wfn = QubitWaveFunction()
    for q in [q1, q2, q3]:
        wfn += QubitWaveFunction.from_int(i=q)
    test_332y = PhotonicStateVector(paths=paths, state=wfn)
    if not silent:
        print("got      = ", test_332y)
        print("expected = ", test_332x)
    assert (test_332x == test_332y)


def test_hologram(silent=True):
    if not silent:
        print("\nTesting Hologram")

    S = 2
    qpm = 2
    setup = PhotonicSetup(pathnames=['a'], S=S, qpm=qpm)
    setup.add_hologram(path='a')

    states = [
        PhotonicStateVector.from_string(paths=setup.paths, string="1.0|20000>_a"),  # 2 photons in -2
        PhotonicStateVector.from_string(paths=setup.paths, string="1.0|02000>_a"),  # 2 photons in -1
        PhotonicStateVector.from_string(paths=setup.paths, string="1.0|00200>_a"),  # 2 photons in  0
        PhotonicStateVector.from_string(paths=setup.paths, string="1.0|00020>_a"),  # 2 photons in  1
        PhotonicStateVector.from_string(paths=setup.paths, string="1.0|00002>_a"),  # 2 photons in  2
    ]

    for i, start in enumerate(states):
        end = setup.simulate_wavefunction(initial_state=start)
        expected = states[(i + 1) % 5]
        if not silent:
            print("start   =", start)
            print("end     =", end)
            print("expected=", expected)
        assert (end == expected)


def test_mirror(silent=True):
    if not silent:
        print("\nTesting Mirror")

    S = 2
    qpm = 2

    setup = PhotonicSetup(pathnames=['a'], S=S, qpm=qpm)
    paths = setup.paths
    setup.add_mirror(path='a')

    statesx = [
        PhotonicStateVector.from_string(paths=paths, string="1.0|20000>_a"),  # 2 photons in -2
        PhotonicStateVector.from_string(paths=paths, string="1.0|02000>_a"),  # 2 photons in -1
        PhotonicStateVector.from_string(paths=paths, string="1.0|00200>_a"),  # 2 photons in  0
        PhotonicStateVector.from_string(paths=paths, string="1.0|00020>_a"),  # 2 photons in  1
        PhotonicStateVector.from_string(paths=paths, string="1.0|00002>_a"),  # 2 photons in  2
    ]

    statesy = [
        PhotonicStateVector.from_string(paths=paths, string="1.0|21301>_a"),
        PhotonicStateVector.from_string(paths=paths, string="1.0|33000>_a"),  # 2 photons in -1
        PhotonicStateVector.from_string(paths=paths, string="1.0|21312>_a"),  # 2 photons in  0
        PhotonicStateVector.from_string(paths=paths, string="1.0|00033>_a"),  # 2 photons in  1
        PhotonicStateVector.from_string(paths=paths, string="1.0|10312>_a"),  # 2 photons in  2
    ]

    for states in [statesx, statesy]:
        for i, start in enumerate(states):
            end = setup.simulate_wavefunction(initial_state=start)
            expected = states[-(i + 1)]

            if not silent:
                print("Mirror Circuit:\n", SimulatorCirq().create_circuit(abstract_circuit=setup.setup))
                print("start   =", start)
                print("end     =", end)
                print("expected=", expected)
            assert (end == expected)

@pytest.mark.parametrize("inout", [
    ("1.0|100>_a", "-1.0|100>_a"),
    ("1.0|200>_a","1.0|200>_a"),
    ("1.0|101>_a","1.0|101>_a"),
    ("1.0|120>_a", "-1.0|120>_a"),
    ("1.0|122>_a", "-1.0|122>_a")
])
def test_dove_prism(inout, silent=False):
    # dove prism is implemented with a global phase
    # but for this tests this is one
    # stupid qubit intitalization, but it makes the test better
    S = 1
    qpm = 2
    t = 1.0

    setup = PhotonicSetup(pathnames=['a'], S=S, qpm=qpm)
    setup.add_doveprism(path='a', t=t)

    istate = setup.initialize_state(state=inout[0])
    ostate = setup.initialize_state(state=inout[1])

    end = setup.simulate_wavefunction(initial_state=istate)

    if not silent:
        print(SimulatorCirq().create_circuit(abstract_circuit=setup.setup))
        print("t       =", t)
        print("start   =", istate)
        print("end     =", end)
        print("expected=", ostate)
    assert (end == ostate)


def test_SPDC(silent=True):
    # Qubit Wavefunction for the expeced state:
    # here are the three basis functions for the -2,-1,0,1,2 mode representation
    # where each mode has 2 qubits
    # mp, minus plus, pm, plus minus, zz, zero zero

    def make_SPDC_state_vector(S, paths) -> PhotonicStateVector:
        """
        Normalized SPDC State vector
        :param S: Spin number ( Modes will be -S ... 0 ... +S)
        :return: SPDC State in 2S+1 modes
        """
        assert (len(paths.keys()) == 2)

        def one_photon_path(occ_mode: int) -> str:
            key = S + occ_mode
            tmp = ["0"] * (2 * S + 1)
            tmp[key] = "1"
            return "".join(tmp)

        def term(a: int, b: int, coeff: float = 1.0 / sqrt(3)) -> str:
            return "+" + str(coeff) + "|" + one_photon_path(occ_mode=a) + ">_a|" + one_photon_path(occ_mode=b) + ">_b"

        return PhotonicStateVector.from_string(paths=paths, string=term(1, -1) + term(0, 0) + term(-1, 1))

    S = 2
    qpm = 2
    setup = PhotonicSetup(pathnames=['a', 'b'], S=S, qpm=qpm)
    paths = setup.paths
    expected = make_SPDC_state_vector(S=S, paths=paths)

    setup.prepare_SPDC_state(path_a='a', path_b='b')
    end = setup.simulate_wavefunction()

    if not silent:
        print("SPDC Circuit:\n", SimulatorCirq().create_circuit(abstract_circuit=setup.setup))
        print("S       =", S)
        print("q per m =", qpm)
        print("end     =", end)
        print("expected=", expected)
    assert (end == expected)


def test_332(silent=False):
    # Qubit Wavefunction for the expeced state:
    # In 3 Paths with -1 0 +1 mode, each mode with 2 qubits
    # Paths are constructed as
    # A(-1 0 1) B(-1 0 1) C(-1 0 1)
    # |XXXXXX|XXXXXX|XXXXXX>
    # The 332 State in Photonic Notation (one photon in each mode noted as |abc> where a = occupied mode in path a)
    # |state> = |1 -1 1> + |0 0 0> + |-1 1 1>
    # 332 State in Qudit notation
    # |state> = |0 0 1>_a|1 0 0>_b|0 0 1>_c
    #          +|0 1 0>_a|0 1 0>_b|0 1 0>_c
    #          +|1 0 0>_a|0 0 1>_b|0 0 1>_c
    # The 332 State for 2-Qubits per mode is
    #        |state>= | 00 00 01 | 01 00 00 | 00 00 01 >
    #                +| 00 01 00 | 00 01 00 | 00 01 00 >
    #                +| 01 00 00 | 00 00 01 | 00 00 01 >

    def make_332_state_vector(S, paths) -> PhotonicStateVector:
        """
        Normalized 332 State vector
        :param S: Spin number ( Modes will be -S ... 0 ... +S)
        :return: 332 State in 2S+1 modes
        """

        def one_photon_path(occ_mode: int) -> str:
            key = S + occ_mode
            tmp = ["0"] * (2 * S + 1)
            tmp[key] = "1"
            return "".join(tmp)

        def term(a: int, b: int, c: int, coeff: float = 1.0 / sqrt(3)) -> str:
            return "+" + str(coeff) + "|" + one_photon_path(occ_mode=a) + ">_a|" + one_photon_path(
                occ_mode=b) + ">_b|" + one_photon_path(occ_mode=c) + ">_c"

        return PhotonicStateVector.from_string(paths=paths, string=term(1, -1, 1) + term(0, 0, 0) + term(-1, 1, 1))

    for S in [1, 2]:
        for qpm in [1, 2]:

            # path_a = dict()
            # path_b = dict()
            # path_c = dict()
            # qubit_counter = 0
            #
            # for path in [path_a, path_b, path_c]:
            #     for m in range(-S, S+1, 1):
            #         path[m] = PhotonicMode(qubits=[q for q in range(qubit_counter, qubit_counter + n_qubits_per_mode)],
            #                                name=str(m))
            #         qubit_counter = qubit_counter + n_qubits_per_mode

            setup = PhotonicSetup(pathnames=['a', 'b', 'c'], S=S, qpm=qpm)
            paths = setup.paths

            expected = make_332_state_vector(S=S, paths=paths)
            setup.prepare_332_state(path_a='a', path_b='b', path_c='c')

            if not silent:
                print("332 Circuit:\n", SimulatorCirq().create_circuit(abstract_circuit=setup.setup))
                print("Paths:\n", paths)

            end = setup.simulate_wavefunction()

            if not silent:
                print("S       =", S)
                print("q per m =", qpm)
                print("end     =", end)
                print("expected=", expected)
            assert (end == expected)


@pytest.mark.parametrize("qpm", [1, 2, 3])
def test_projector_prep(qpm, silent=True):
    S = 1
    angles = [1.2309594173407747, 1.5707963267948966]

    setup = PhotonicSetup(pathnames=['a'], S=S, qpm=qpm)
    setup.add_parametrized_one_photon_projector(path='a', angles=angles, daggered=False)
    wfn = setup.simulate_wavefunction()

    result = PhotonicStateVector.from_string(paths=setup.paths,
                                             string="+ 0.5774|001>_a + 0.5774|010>_a + 0.5774|100>_a")

    if not silent:
        setup.print_circuit()
        print("wfn     = ", wfn)
        print("expected= ", result)

    assert (str(result) == str(wfn))


@pytest.mark.parametrize("qpm", [1, 2, 3])
def test_parametrized_projector(qpm):
    S = 1
    setup = PhotonicSetup(pathnames=['a', 'b'], S=S, qpm=qpm)
    state = PhotonicStateVector.from_string(paths=setup.paths,
                                            string="0.5774|001>_a|111>_b+0.5774|010>_a|111>_b+0.5774|100>_a|111>_b")
    setup.prepare_unary_type_state(state=state)
    setup.add_parametrized_one_photon_projector(path='a', angles=[1.2309594173407747, 1.5707963267948966])

    wfn = setup.simulate_wavefunction()
    assert (str(PhotonicStateVector.from_string(paths=setup.paths, string="1.0|000>_a|111>_b")) == str(wfn))

    counts = setup.run(samples=100)
    reduced_paths = PhotonicPaths(path_names=['b'], S=S, qpm=qpm)
    assert (str(PhotonicStateVector.from_string(paths=reduced_paths, string="100|111>_b")) == str(counts))

@pytest.mark.parametrize("qpm", [1, 2, 3])
def test_projector(qpm):
    S = 1
    setup = PhotonicSetup(pathnames=['a', 'b'], S=S, qpm=qpm)
    state = PhotonicStateVector.from_string(paths=setup.paths,
                                            string="0.7071|001>_a|111>_b+0.7071|010>_a|111>_b")
    setup.prepare_unary_type_state(state=state)
    setup.add_one_photon_projector(path='a')

    wfn = setup.simulate_wavefunction()
    assert (str(PhotonicStateVector.from_string(paths=setup.paths, string="1.0|000>_a|111>_b")) == str(wfn))

    counts = setup.run(samples=100)
    reduced_paths = PhotonicPaths(path_names=['b'], S=S, qpm=qpm)
    assert (str(PhotonicStateVector.from_string(paths=reduced_paths, string="100|111>_b")) == str(counts))

if __name__ == "__main__":
    test_notation(silent=False)

    test_332(silent=False)

    test_SPDC(silent=False)

    test_dove_prism(silent=False)

    test_mirror(silent=False)

    test_hologram(silent=False)

    test_parametrized_projector(silent=False)
