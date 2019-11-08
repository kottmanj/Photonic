from typing import List, Dict
from photonic.mode import PhotonicMode, PhotonicPaths, PhotonicStateVector
from numpy import pi, sqrt
from openvqe.circuit import gates, QCircuit
from openvqe import BitNumbering, BitString
from openvqe.hamiltonian import QubitHamiltonian
from openvqe.hamiltonian.paulis import decompose_transfer_operator
from openvqe.circuit.exponential_gate import DecompositionFirstOrderTrotter
from openvqe.simulator.simulator_cirq import SimulatorCirq
from openvqe.simulator.heralding import HeraldingABC, HeraldingProjector
from openvqe.apps import UnaryStatePrep


class PhotonicHeralder(HeraldingABC):
    """
    Post-Processing assignment for OpenVQE
    Will only count states with one photon in each path
    """

    def __init__(self, paths: PhotonicPaths):
        self.paths = paths

    def is_valid(self, key: BitString) -> bool:
        # valid if every path has one photon (no matter in which mode)
        occs = self.paths.extract_occupation_numbers(i=key)
        for path, mode in occs.items():
            total = 0
            for occ in mode.values():
                total += occ.integer
            if total != 1:
                return False

        return True


class PhotonicHeraldingProjector(HeraldingProjector):

    def __init__(self, paths: PhotonicPaths, active_path: str, delete_active_path: bool = True):
        self.paths = paths
        subregister = []
        for mode in paths[active_path].values():
            subregister += mode.qubits
        projector_space = [BitString.from_int(integer=0, nbits=len(subregister)).binary]
        super().__init__(register=paths.qubits, subregister=subregister, projector_space=projector_space,
                         delete_subregister=delete_active_path)

        if delete_active_path:
            # make the reduced path
            pathnames = []
            for name in paths.keys():
                if name != active_path:
                    pathnames.append(name)

            self.reduced_paths = PhotonicPaths(path_names=pathnames, S=paths.S, qpm=paths.qpm)
        else:
            self.reduced_paths = paths


def QuditS(target: PhotonicMode, t):
    """
    :param target:
    :param t: the phase is phi=exp(-i*pi*t)
    :return:
    """
    iterator = target.qubits
    if target.numbering == BitNumbering.MSB:
        iterator = reversed(target.qubits)
    result = QCircuit()
    for i, q in enumerate(iterator):
        result += gates.Rz(target=q, angle=t * 2 ** i * pi)  # adds a global phase
    return result


def QuditSWAP(mode1: PhotonicMode, mode2: PhotonicMode) -> QCircuit:
    assert (mode1.n_qubits == mode2.n_qubits)
    assert (mode1.numbering == mode2.numbering)

    result = QCircuit()
    for i, q in enumerate(mode1.qubits):
        result += gates.SWAP(mode1.qubits[i], mode2.qubits[i])

    return result


def anihilation(qubits: List[int] = None) -> QubitHamiltonian:
    max_occ = 2 ** len(qubits) - 1
    result = QubitHamiltonian.init_zero()
    for occ in range(max_occ):
        c = sqrt(occ + 1)
        result += c * decompose_transfer_operator(ket=occ + 1, bra=occ, qubits=qubits)
    return result


def creation(qubits: List[int] = None) -> QubitHamiltonian:
    max_occ = 2 ** len(qubits) - 1
    result = QubitHamiltonian.init_zero()
    for occ in range(max_occ):
        c = sqrt(occ + 1)
        result += c * decompose_transfer_operator(ket=occ, bra=occ + 1, qubits=qubits)
    return result


class PhotonicSetup:

    @property
    def paths(self) -> PhotonicPaths:
        return self._paths

    @property
    def S(self) -> int:
        return self.paths.S

    @property
    def qpm(self) -> int:
        return self.paths.qpm

    @property
    def n_qubits(self) -> int:
        return self.paths.n_qubits

    @property
    def qubits(self) -> int:
        return self.paths.qubits

    @property
    def setup(self):
        return self._setup

    def print_circuit(self, simulator=None):
        if simulator is None:
            simulator = SimulatorCirq()
        print(simulator.create_circuit(abstract_circuit=self.setup))

    def initialize_state(self, state: str) -> PhotonicStateVector:
        return PhotonicStateVector.from_string(paths=self.paths, string=state)

    def __init__(self, pathnames: List[str], S: int, qpm: int, qubits: List[int] = None, setup: QCircuit = None):
        """
        :param pathnames: The names of the paths in the setups
        :param S: The Spin number which defines the number of simulated modes which ranges from -S to S
        :param qpm: qubits per mode
        """

        self._paths = PhotonicPaths(path_names=pathnames, S=S, qpm=qpm, qubits=qubits)
        if setup is None:
            self._setup = QCircuit()
        else:
            self._setup = setup

        self.heralding = None

    def extract_parameters(self):
        return self._setup.extract_parameters()

    def __repr__(self):
        result = "PhotonicSetup:\n"
        result += str(self.paths)
        return result

    def _add_measurements(self):
        self._setup += gates.Measurement(target=self.paths.qubits)

    def simulate_wavefunction(self, initial_state: [str, PhotonicStateVector] = None,
                              simulator=None) -> PhotonicStateVector:

        if isinstance(initial_state, str):
            initial_state = PhotonicStateVector.from_string(paths=self.paths, string=initial_state)

        if simulator is None:
            simulator = SimulatorCirq()
        if initial_state is None:
            initial_state = 0
        else:
            initial_state = initial_state.state

        simresult = simulator.simulate_wavefunction(abstract_circuit=self.setup, initial_state=initial_state)
        print("wfn=", simresult.wavefunction)
        return PhotonicStateVector(paths=self.paths, state=simresult.wavefunction)

    def run(self, samples: int = 1, initial_state: str = None, simulator=None):
        iprep = QCircuit()
        if initial_state is not None:
            state = self.initialize_state(state=initial_state)
            # can only do product states right now, alltough more general ones are possible
            assert (len(state.state) == 1)
            key = [k for k in state.state.keys()][0]
            for i, q in enumerate(key.array):
                if q == 1:
                    iprep += gates.X(target=i)
        if simulator is None:
            simulator = SimulatorCirq()

        self._add_measurements()

        if self.heralding is not None:
            simulator._heralding = self.heralding
            if samples is None:
                simresult = simulator.simulate_wavefunction(abstract_circuit=iprep + self.setup)
            else:
                simresult = simulator.run(abstract_circuit=iprep + self.setup, samples=samples)
            return PhotonicStateVector(paths=self.heralding.reduced_paths, state=simresult.measurements[''])
        else:
            if samples is None:
                simresult = simulator.simulate_wavefunction(abstract_circuit=iprep + self.setup)
            else:
                simresult = simulator.run(abstract_circuit=iprep + self.setup, samples=samples)
            return PhotonicStateVector(paths=self.paths, state=simresult.measurements[''])

    @classmethod
    def from_paths(cls, paths: PhotonicPaths, setup: QCircuit = None):
        return cls(pathnames=[k for k in paths.keys()], S=paths.S, qpm=paths.qpm, setup=setup)

    def __add__(self, other):
        assert (self.paths == other.paths)
        return self.from_paths(paths=self.paths, setup=self.setup + other.setup)

    def __iadd__(self, other):
        self._setup += other.setup
        return self

    def prepare_332_state(self, path_a: str, path_b: str, path_c: str, daggered=False):
        """
        :return: A circuit which prepares the photonic 332 state in qubit representation
        """

        pa = self.paths[path_a]
        pb = self.paths[path_b]
        pc = self.paths[path_c]

        triple_angle = 0.9553166181245093

        qubits = []  # qubits onto which the circuit will act
        max_qubit = 0  # maxmimal number of qubits in the whole path setup, the circuit should know that in order for the simulator to give back the states in correct formats
        for path in [pa, pb, pc]:
            for mode in [-1, 0, 1]:
                if path[mode].numbering == BitNumbering.LSB:
                    qubits.append(path[mode].qubits[0])
                else:
                    qubits.append(path[mode].qubits[-1])
            for mode in path.values():
                max_qubit = max(max_qubit, max(mode.qubits))
        assert (len(qubits) == 9)

        pa = pi / 2
        path_b = triple_angle * 2
        circuit = QCircuit()
        circuit.n_qubits = max_qubit + 1

        circuit *= gates.X(target=qubits[7])
        circuit *= gates.X(target=qubits[4])
        circuit *= gates.X(target=qubits[1])
        circuit *= gates.X(target=qubits[0])
        circuit *= gates.Ry(target=qubits[8], control=qubits[0], angle=path_b)
        circuit *= gates.X(target=qubits[0])
        circuit *= gates.X(target=qubits[7], control=qubits[8])
        circuit *= gates.X(target=qubits[7])
        circuit *= gates.X(target=qubits[4], control=qubits[7])
        circuit *= gates.X(target=qubits[7])
        circuit *= gates.X(target=qubits[4])
        circuit *= gates.X(target=qubits[3], control=qubits[4])
        circuit *= gates.X(target=qubits[4])
        circuit *= gates.X(target=qubits[1], control=qubits[3])
        circuit *= gates.X(target=qubits[1])
        circuit *= gates.X(target=qubits[0], control=qubits[1])
        circuit *= gates.X(target=qubits[1])
        circuit *= gates.Ry(target=qubits[5], control=qubits[0], angle=pa)
        circuit *= gates.X(target=qubits[3], control=qubits[5])
        circuit *= gates.X(target=qubits[2], control=qubits[3])
        circuit *= gates.X(target=qubits[0], control=qubits[2])

        if daggered:
            self._setup += circuit.dagger()
        else:
            self._setup += circuit
        return self

    def add_mirror(self, path: str):
        p = self.paths[path]
        result = QCircuit()
        passed_keys = [0]
        for k, v in p.items():
            si1 = int(k)
            si2 = -int(k)
            if k in passed_keys:
                continue
            else:
                passed_keys += [si1, si2]

            if si1 in p and si2 in p:
                result *= QuditSWAP(mode1=p[si1], mode2=p[si2])
            else:
                print("Mode si1=", si1, " si2=", si2)
                raise Exception("No Partner for Mode %" % si1)

        self._setup += result
        return self

    def add_doveprism(self, path: str, t):
        """
        :param t: The phase is parametrized by t: phase=exp(i*pi*t)
        :return: DovePrism circuit
        """
        for k, v in self.paths[path].items():
            self._setup += QuditS(target=v, t=t * k)
        return self

    def add_hologram(self, path: str):
        p = self.paths[path]
        sorted_keys = [k for k in p.keys()]
        sorted_keys.sort(reverse=True)
        result = QCircuit()
        for k in sorted_keys:
            if k - 1 not in sorted_keys:
                break
            result *= QuditSWAP(mode1=p[k], mode2=p[k - 1])

        self._setup += result
        return self

    def add_parametrized_one_photon_projector(self, path: str, angles: List[float], daggered=True):
        """
        Name might be confusing
        Addes an element which can disentangle all possible LKs of
        one-photon states in a specific path
        The function prepares a circuit which can generate an arbitrary
        one-photon state in the path form the zero start
        its inverse is added to the setup
        heralding is also added
        this should be the last element acting on this path! (will not be checked)
        :param path: the path where the element acts
        :param angles: the angles which parametrize this element
        :return: self for chaining
        """

        # get the qubits which encode the 0 and 1 occupation numbers (the last of each mode, since we're in MSB numbering)
        qubits = [mode.qubits[-1] for mode in self.paths[path].values()]

        result = QCircuit()
        result += gates.Ry(target=qubits[-1], angle=angles[0])
        result += gates.X(target=qubits[-1])
        result += gates.X(target=qubits[0], control=qubits[-1])
        result += gates.X(target=qubits[-1])

        for i, q in enumerate(reversed(qubits)):
            if q == qubits[-1]: continue
            if q == qubits[0]: break
            result += gates.Ry(target=q, control=qubits[0], angle=angles[i])
            result += gates.X(target=qubits[0], control=q)

        if daggered:
            self._setup += result.dagger()
        else:
            self._setup += result

        # add heralder
        self.heralding = PhotonicHeraldingProjector(paths=self.paths, active_path=path)

        return self

    def add_one_photon_projector(self, path: str, daggered: bool = True, delete_active_path: bool = True):
        """
        same as parametrized_one_photon_projector but hard-wired to the state: |0> + |1>
        meaning one photon in mode 0 and one photon in mode 1
        for S=1 this looks like: |010>_path + |001>_path
        for S=2 |00100>_path + |00010>_path
        :param path: the path where the projector adds
        :param daggered: other way, for testing
        :return: adds the element to the setup and returns self for chaining
        """
        assert self.S > 0

        # identify the significant qubits encoding occs 0 and 1 in modes 0 and 1
        qubits = [mode.qubits[-1] for mode in [self.paths[path][0], self.paths[path][1]]]

        result = gates.H(target=qubits[1])
        result += gates.X(target=qubits[1])
        result += gates.X(target=qubits[0], control=qubits[1])
        result += gates.X(target=qubits[1])

        if daggered:
            self._setup += result.dagger()
        else:
            self._setup += result

        self.heralding = PhotonicHeraldingProjector(paths=self.paths, active_path=path,
                                                    delete_active_path=delete_active_path)

        return self

    def prepare_SPDC_state(self, path_a: str, path_b: str):
        triple_angle = 0.9553166181245093
        qubits = []
        max_qubit = 0
        path_a = self.paths[path_a]
        path_b = self.paths[path_b]
        for path in [path_a, path_b]:
            for mode in [-1, 0, 1]:
                if path[mode].numbering == BitNumbering.LSB:
                    qubits.append(path[mode].qubits[0])
                else:
                    qubits.append(path[mode].qubits[-1])
            for mode in path.values():
                max_qubit = max(max_qubit, max(mode.qubits))
        assert (len(qubits) == 6)

        result = QCircuit()
        result.n_qubits = max_qubit + 1
        result *= gates.X(target=qubits[0])
        result *= gates.X(target=qubits[5])
        result *= gates.Ry(target=qubits[1], angle=2 * triple_angle)
        result *= gates.X(target=qubits[0], control=qubits[1])
        result *= gates.X(target=qubits[4], control=qubits[1])
        result *= gates.X(target=qubits[5], control=qubits[4])
        result *= gates.H(target=qubits[2], control=qubits[1])
        result *= gates.X(target=qubits[1], control=qubits[2])
        result *= gates.X(target=qubits[3], control=qubits[2])
        result *= gates.X(target=qubits[4], control=qubits[3])

        self._setup += result
        return self

    def add_beamsplitter(self, path_a: str, path_b: str, t=0.25, steps: int = 1, join_components: bool = True,
                         randomize_component_order: bool = False, randomize: bool = False):
        """
        :param path_a: name of path a
        :param path_b: name of path b
        :param t: parametrizes the angle: phi = i*pi*t
        :param steps:
        :param join_components: convenience to play around with Trotterization, see DecomposeFirstOrderTrotter doc of OpenVQE
        :param randomize_component_order: see before
        :param randomize: see before
        :return:
        """
        assert (len(self.paths[path_a]) == len(self.paths[path_b]))
        assert (self.paths[path_a].keys() == self.paths[path_b].keys())

        phi = 1.0j * pi * -2.0  # OpenVQE uses the same angle convention for Trotterization as for QubitRotations, therefore the -2 here

        # convenience
        a = self.paths[path_a]
        b = self.paths[path_b]

        modes = [k for k in a.keys()]

        trotter = DecompositionFirstOrderTrotter(steps=steps, join_components=join_components,
                                                 randomize_component_order=randomize_component_order,
                                                 randomize=randomize)

        generators = []
        for mode in modes:
            hamiltonian = QubitHamiltonian.init_zero()
            hamiltonian += creation(qubits=a[mode].qubits) * anihilation(qubits=b[mode].qubits)
            hamiltonian -= creation(qubits=b[mode].qubits) * anihilation(qubits=a[mode].qubits)
            generators.append(phi * hamiltonian)

        result = trotter(generators=generators, coeffs=[t] * len(generators))
        self._setup += result

        # return self for chaining
        return self

    def prepare_unary_type_state(self, state: PhotonicStateVector, daggered:bool=False):
        """
        This will do some calculations, so only use it to debug
        :return: adds the preparation of the state to the setup, returns self for chaining
        """
        if isinstance(state, str):
            state = PhotonicStateVector.from_string(paths=self.paths, string=state)
            print("state=", state.state)
        USP = UnaryStatePrep(target_space=state.state)
        U = USP(wfn=state.state)
        if daggered:
            self._setup += U.dagger()
        else:
            self._setup += U
        return self

    def add_circuit(self, U):
        """
        Use with care, no checks are performed
        :param U: add this unitary to the setup
        :return: self for chaining
        """
        self._setup += U
        return self
