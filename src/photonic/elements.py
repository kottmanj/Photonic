import typing
from photonic.mode import PhotonicMode, PhotonicPaths, PhotonicStateVector
from numpy import pi, sqrt, exp

import tequila as tq
from tequila.apps import UnaryStatePrep

from dataclasses import dataclass


@dataclass
class AbstractElement:
    """
    DataClass which keeps track of the photonic setup
    --> More elegant solutions possible
    Currently only implemented for qpic output
    """
    name: str
    paths: typing.List[str]


class PhotonicHeralder:
    """
    Post-Processing assignment for OpenVQE
    Will only count states with one photon in each path
    """

    def __init__(self, paths: PhotonicPaths):
        self.paths = paths

    def is_valid(self, key: tq.BitString) -> bool:
        # valid if every path has one photon (no matter in which mode)
        occs = self.paths.extract_occupation_numbers(i=key)
        for path, mode in occs.items():
            total = 0
            for occ in mode.values():
                total += occ.integer
            if total != 1:
                return False

        return True


class PhotonicHeraldingProjector:

    def __init__(self, paths: PhotonicPaths, active_path: str, delete_active_path: bool = True):
        self.paths = paths
        subregister = []
        for mode in paths[active_path].values():
            subregister += mode.qubits
        projector_space = [tq.BitString.from_int(integer=0, nbits=len(subregister)).binary]
        #super().__init__(register=paths.qubits, subregister=subregister, projector_space=projector_space,
        #                 delete_subregister=delete_active_path)

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
    if target.numbering == tq.BitNumbering.MSB:
        iterator = reversed(target.qubits)
    result = tq.gates.QCircuit()
    for i, q in enumerate(iterator):
        result += tq.gates.Rz(target=q, angle=t * 2 ** i * pi)
    return result


def QuditSWAP(mode1: PhotonicMode, mode2: PhotonicMode) -> tq.gates.QCircuit:
    assert (mode1.n_qubits == mode2.n_qubits)
    assert (mode1.numbering == mode2.numbering)

    result = tq.gates.QCircuit()
    for i, q in enumerate(mode1.qubits):
        result += tq.gates.SWAP(mode1.qubits[i], mode2.qubits[i])

    return result


def anihilation(qubits: typing.List[int] = None) -> tq.hamiltonian.QubitHamiltonian:
    max_occ = 2 ** len(qubits) - 1
    result = tq.hamiltonian.QubitHamiltonian.zero()
    for occ in range(max_occ):
        c = sqrt(occ + 1)
        result += c * tq.paulis.decompose_transfer_operator(ket=occ + 1, bra=occ, qubits=qubits)
    return result.simplify()


def creation(qubits: typing.List[int] = None) -> tq.hamiltonian.QubitHamiltonian:
    max_occ = 2 ** len(qubits) - 1
    result = tq.hamiltonian.QubitHamiltonian.zero()
    for occ in range(max_occ):
        c = sqrt(occ + 1)
        result += c * tq.paulis.decompose_transfer_operator(ket=occ, bra=occ + 1, qubits=qubits)
    return result.simplify()


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
        print(self.setup)

    def initialize_state(self, state: str) -> PhotonicStateVector:
        return PhotonicStateVector.from_string(paths=self.paths, string=state)

    def __init__(self, pathnames: typing.List[str], S: int, qpm: int, qubits: typing.List[int] = None,
                 setup: tq.gates.QCircuit = None):
        """
        :param pathnames: The names of the paths in the setups
        :param S: The Spin number which defines the number of simulated modes which ranges from -S to S
        :param qpm: qubits per mode
        """

        self._paths = PhotonicPaths(path_names=pathnames, S=S, qpm=qpm, qubits=qubits)
        if setup is None:
            self._setup = tq.gates.QCircuit()
        else:
            self._setup = setup

        self.setup.n_qubits = self._paths.n_qubits

        self._abstract_setup = []

        self.heralding = None

    def extract_parameters(self):
        return self._setup.extract_parameters()

    def __repr__(self):
        result = "PhotonicSetup:\n"
        result += str(self.paths)
        return result

    def _add_measurements(self):
        self._setup += tq.gates.Measurement(target=self.paths.qubits)

    def simulate_wavefunction(self, initial_state: [str, PhotonicStateVector] = None,
                              simulator=None) -> PhotonicStateVector:

        if isinstance(initial_state, str):
            initial_state = PhotonicStateVector.from_string(paths=self.paths, string=initial_state)

        if initial_state is None:
            initial_state = 0
        else:
            initial_state = initial_state.state

        simresult = tq.simulate(self.setup, backend=simulator, initial_state=initial_state)
        return PhotonicStateVector(paths=self.paths, state=simresult)

    def sample(self, samples: int = 1, initial_state: str = None, simulator=None):
        iprep = tq.gates.QCircuit()
        if initial_state is not None:
            state = self.initialize_state(state=initial_state)
            # can only do product states right now, alltough more general ones are possible
            assert (len(state.state) == 1)
            key = [k for k in state.state.keys()][0]
            for i, q in enumerate(key.array):
                if q == 1:
                    iprep += tq.gates.X(target=i)

        self._add_measurements()

        # those are the qubit counts given back by tequila
        qcounts = tq.simulate(iprep + self.setup, samples=samples)
        # those are the qubit counts re-interpreted as photonic counts
        pcounts = PhotonicStateVector(paths=self.paths, state=qcounts)

        return pcounts

    @classmethod
    def from_paths(cls, paths: PhotonicPaths, setup: tq.gates.QCircuit = None):
        return cls(pathnames=[k for k in paths.keys()], S=paths.S, qpm=paths.qpm, setup=setup)

    def __add__(self, other):
        assert (self.paths == other.paths)
        return self.from_paths(paths=self.paths, setup=self.setup + other.setup)

    def __iadd__(self, other):
        self._setup += other.setup
        return self

    def prepare_332_state(self, path_a: str, path_b: str, path_c: str, daggered=False):
        """
        332 as '-+- 000 --+'
        :return: A circuit which prepares the photonic 332 state in qubit representation
        """

        pa = self.paths[path_a]
        pb = self.paths[path_b]
        pc = self.paths[path_c]

        qubits = []  # qubits onto which the circuit will act
        max_qubit = 0  # maxmimal number of qubits in the whole path setup, the circuit should know that in order for the simulator to give back the states in correct formats
        for path in [pa, pb, pc]:
            for mode in [-1, 0, 1]:
                if path[mode].numbering == tq.BitNumbering.LSB:
                    qubits.append(path[mode].qubits[0])
                else:
                    qubits.append(path[mode].qubits[-1])
            for mode in path.values():
                max_qubit = max(max_qubit, max(mode.qubits))
        assert (len(qubits) == 9)

        circuit = tq.gates.QCircuit()
        circuit.n_qubits = max_qubit + 1

        triple_angle = 0.9553166181245093
        circuit += tq.gates.Ry(target=qubits[7], angle=2 * triple_angle)  # 1.2309594173407747)

        # circuit += tq.gates.X(target=qubits[7])
        circuit += tq.gates.X(target=qubits[6], control=qubits[7])
        # Quacircuit += tq.gates.X(target=qubits[7])

        circuit += tq.gates.X(target=qubits[4], control=qubits[6])
        circuit += tq.gates.X(target=qubits[3], control=qubits[4])

        circuit += tq.gates.X(target=qubits[4])
        circuit += tq.gates.X(target=qubits[1], control=qubits[3])

        circuit += tq.gates.X(target=qubits[0], control=qubits[1])
        circuit += tq.gates.X(target=qubits[1])

        # circuit += tq.gates.X(target=qubits[7])
        circuit += tq.gates.Ry(target=qubits[8], control=qubits[7], angle=1.5707963267948966)
        circuit += tq.gates.X(target=qubits[7])
        circuit += tq.gates.X(target=qubits[6], control=qubits[8])
        circuit += tq.gates.X(target=qubits[5], control=qubits[6])
        circuit += tq.gates.X(target=qubits[3], control=qubits[5])

        if daggered:
            self._setup += circuit.dagger()
            self._abstract_setup += [AbstractElement(name="332^\\dagger", paths=[path_a, path_b, path_c])]
        else:
            self._setup += circuit
            self._abstract_setup += [AbstractElement(name="332", paths=[path_a, path_b, path_c])]
        return self

    def add_mirror(self, path: str):
        p = self.paths[path]
        result = tq.gates.QCircuit()
        passed_keys = [0]
        for k, v in p.items():
            si1 = int(k)
            si2 = -int(k)
            if k in passed_keys:
                continue
            else:
                passed_keys += [si1, si2]

            if si1 in p and si2 in p:
                result += QuditSWAP(mode1=p[si1], mode2=p[si2])
            else:
                print("Mode si1=", si1, " si2=", si2)
                raise Exception("No Partner for Mode %" % si1)

        self._setup += result
        self._abstract_setup += [AbstractElement(name="M", paths=[path])]
        return self

    def add_doveprism(self, path: str, t):
        """
        :param t: The phase is parametrized by t: phase=exp(-i*pi*t)
        :return: DovePrism circuit
        """
        for k, v in self.paths[path].items():
            self._setup += QuditS(target=v, t=t * k)

        self._abstract_setup += [AbstractElement(name="DP(\\phi)", paths=[path])]
        return self

    def add_phase_shifter(self, t, path: str, mode: int = None):
        """
        Add a phase shift to specific mode in given path
        :param t : The phase is parametrized by t: phase=exp(-i*pi*t)
        :param path: the given path
        :param mode: the mode, if None then the phase shifter will act on all modes
        """
        modes = [mode]
        if mode is None:
            modes = self.paths[path].keys()

        for key in modes:
            self._setup += QuditS(target=self.paths[path][key], t=t)
            self._abstract_setup += [AbstractElement(name="PS(\\phi)", paths=[path])]
        return self

    def add_hologram(self, path: str):
        p = self.paths[path]
        sorted_keys = [k for k in p.keys()]
        sorted_keys.sort(reverse=True)
        result = tq.gates.QCircuit()
        for k in sorted_keys:
            if k - 1 not in sorted_keys:
                break
            result += QuditSWAP(mode1=p[k], mode2=p[k - 1])

        self._setup += result
        self._abstract_setup += [AbstractElement(name="H", paths=[path])]
        return self

    def add_parametrized_one_photon_projector(self, path: str, angles: typing.List[float], daggered=True):
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

        result = tq.gates.QCircuit()
        result += tq.gates.Ry(target=qubits[-1], angle=angles[0])
        result += tq.gates.X(target=qubits[-1])
        result += tq.gates.X(target=qubits[0], control=qubits[-1])
        result += tq.gates.X(target=qubits[-1])

        for i, q in enumerate(reversed(qubits)):
            if q == qubits[-1]: continue
            if q == qubits[0]: break
            result += tq.gates.Ry(target=q, control=qubits[0], angle=angles[i])
            result += tq.gates.X(target=qubits[0], control=q)

        if daggered:
            self._setup += result.dagger()
            self._abstract_setup += [AbstractElement(name="R(\\theta)", paths=[path])]
        else:
            self._setup += result
            self._abstract_setup += [AbstractElement(name="R(\\theta)", paths=[path])]

        # add heralder
        self.heralding = PhotonicHeraldingProjector(paths=self.paths, active_path=path)

        return self

    def add_one_photon_projector(self, path: str, daggered: bool = True, delete_active_path: bool = True):
        """
        same as parametrized_one_photon_projector but hard-wired to the state: |0> - |1>
        meaning one photon in mode 0 and one photon in mode 1
        for S=1 this looks like: |010>_path - |001>_path
        for S=2 |00100>_path - |00010>_path
        :param path: the path where the projector adds
        :param daggered: other way, for testing
        :return: adds the element to the setup and returns self for chaining
        """
        assert self.S > 0

        # identify the significant qubits encoding occs 0 and 1 in modes 0 and 1
        qubits = [mode.qubits[-1] for mode in [self.paths[path][0], self.paths[path][1]]]

        result = tq.gates.X(target=qubits[1])
        result += tq.gates.H(target=qubits[1])
        result += tq.gates.X(target=qubits[0], control=qubits[1])
        result += tq.gates.X(target=qubits[1])

        if daggered:
            self._setup += result.dagger()
        else:
            self._setup += result

        self.heralding = PhotonicHeraldingProjector(paths=self.paths, active_path=path,
                                                    delete_active_path=delete_active_path)

        self._abstract_setup += [AbstractElement(name="R", paths=[path])]
        return self

    def add_one_photon_projector_plus(self, path: str, daggered: bool = True, delete_active_path: bool = True):
        """
        same as parametrized_one_photon_projector but hard-wired to the state: |0> + |1>
        meaning one photon in mode 0 and one photon in mode 1
        for S=1 this looks like: |010>_path + |001>_path
        for S=2 |00100>_path - |00010>_path
        :param path: the path where the projector adds
        :param daggered: other way, for testing
        :return: adds the element to the setup and returns self for chaining
        """
        assert self.S > 0

        # identify the significant qubits encoding occs 0 and 1 in modes 0 and 1
        qubits = [mode.qubits[-1] for mode in [self.paths[path][0], self.paths[path][1]]]

        result = tq.gates.H(target=qubits[1])
        result += tq.gates.X(target=qubits[0], control=qubits[1])
        result += tq.gates.X(target=qubits[1])

        if daggered:
            self._setup += result.dagger()
        else:
            self._setup += result

        self.heralding = PhotonicHeraldingProjector(paths=self.paths, active_path=path,
                                                    delete_active_path=delete_active_path)

        self._abstract_setup += [AbstractElement(name="R", paths=[path])]
        return self

    def prepare_SPDC_state(self, path_a: str, path_b: str):
        triple_angle = 0.9553166181245093
        qubits = []
        max_qubit = 0
        a = self.paths[path_a]
        b = self.paths[path_b]
        for path in [a, b]:
            for mode in [-1, 0, 1]:
                if path[mode].numbering == tq.BitNumbering.LSB:
                    qubits.append(path[mode].qubits[0])
                else:
                    qubits.append(path[mode].qubits[-1])
            for mode in path.values():
                max_qubit = max(max_qubit, max(mode.qubits))
        assert (len(qubits) == 6)

        result = tq.gates.QCircuit()
        result.n_qubits = max_qubit + 1
        result += tq.gates.X(target=qubits[0])
        result += tq.gates.X(target=qubits[5])
        result += tq.gates.Ry(target=qubits[1], angle=2 * triple_angle)
        result += tq.gates.X(target=qubits[0], control=qubits[1])
        result += tq.gates.X(target=qubits[4], control=qubits[1])
        result += tq.gates.X(target=qubits[5], control=qubits[4])
        result += tq.gates.Ry(target=qubits[2], control=qubits[1], angle=pi / 2)
        result += tq.gates.X(target=qubits[1], control=qubits[2])
        result += tq.gates.X(target=qubits[3], control=qubits[2])
        result += tq.gates.X(target=qubits[4], control=qubits[3])

        self._setup += result
        self._abstract_setup += [AbstractElement(name="SPDC", paths=[path_a, path_b])]
        return self

    def add_beamsplitter(self, path_a: str, path_b: str, t=0.25, phi=-pi / 2, steps: int = 1,
                         join_components: bool = True,
                         randomize_component_order: bool = False, randomize: bool = False):
        """
        Beamsplitter is defined here as:
        exp(i*pi*t*(exp(i*phi)*a^\dagger b + exp(-i*phi)*b^\dagger a))
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

        # convenience
        a = self.paths[path_a]
        b = self.paths[path_b]

        # Tequila uses the same angle convention for Trotterization as for QubitRotations, therefore the -2 here
        # the t parameter is added as angles to the TrotterizedGate
        omega = pi * -2.0
        phase = exp(1j * phi)

        modes = [k for k in a.keys()]
        generators = []
        for mode in modes:
            hamiltonian = tq.hamiltonian.QubitHamiltonian.zero()
            hamiltonian += creation(qubits=a[mode].qubits) * anihilation(qubits=b[mode].qubits)
            generators.append(omega * (phase * hamiltonian + phase.conj() * hamiltonian.dagger()))

        parameters = tq.gates.TrotterParameters(join_components=join_components,
                                                randomize_component_order=randomize_component_order,
                                                randomize=randomize)

        result = tq.gates.Trotterized(generators=generators, steps=steps, parameters=parameters, angles=[t]*len(generators))
        self._setup += result
        self._abstract_setup += [AbstractElement(name="BS(\\theta)", paths=[path_a, path_b])]

        # return self for chaining
        return self


    def add_edge(self, path_a: str, path_b: str, i:int, j:int, omega, steps: int = 1, *args, **kwargs):
        """
        Add an edge between path a and path b
        creating photons in |i>_a (x) |j>_b where i,j are the internal degrees of freedom (modes)
        """
        assert (len(self.paths[path_a]) == len(self.paths[path_b]))
        assert (self.paths[path_a].keys() == self.paths[path_b].keys())

        # convenience
        a = self.paths[path_a]
        b = self.paths[path_b]

        generator = creation(qubits=a[i].qubits) * creation(qubits=b[j].qubits)
        generator -= anihilation(qubits=a[i].qubits) * anihilation(qubits=b[j].qubits)

        result = tq.gates.Trotterized(generators=[1.0j*generator], steps=steps, angles=[omega])
        self._setup += result
        self._abstract_setup += [AbstractElement(name="Edge(\\omega)", paths=[path_a, path_b])]

        # return self for chaining
        return self


    def prepare_unary_type_state(self, state: PhotonicStateVector, daggered: bool = False):
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
            self._abstract_setup += [AbstractElement(name="U^\dagger(\\theta)", paths=[k for k in state.paths.keys()])]
        else:
            self._setup += U
            self._abstract_setup += [AbstractElement(name="U(\\theta)", paths=[k for k in state.paths.keys()])]
        return self

    def add_circuit(self, U):
        """
        Use with care, no checks are performed
        :param U: add this unitary to the setup
        :return: self for chaining
        """
        self._setup += U
        self._abstract_setup += [AbstractElement(name="U(\\theta)", paths=[k for k in self.paths.keys()])]
        return self

    def export_to_qpic(self, filename=None) -> str:
        result = ""

        # define wires
        for p in self.paths.keys():
            result += "style=thick " + p + " W " + p + "\n"

        for p in self.paths.keys():
            result += p + " / \n"

        for element in self._abstract_setup:
            for p in element.paths:
                result += str(p) + " "
            result += " G $" + element.name + "$ width=" + str(
                30 + len(element.name)) + " \n"

        if filename is not None:
            with open(filename, "w") as file:
                file.write(result)

        return result
