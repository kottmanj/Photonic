"""
Wrappers to represent photonic modes by multiple qubits
"""
from typing import Dict, List
from copy import deepcopy
from openvqe.simulator import QubitWaveFunction
from openvqe.tools.convenience import number_to_string
from openvqe import BitString, BitNumbering
from numpy import isclose


class PhotonicMode:

    @property
    def numbering(self):
        return BitNumbering.MSB

    def __repr__(self):
        return self.name + " " + str(self.n_qubits) + " qubits: " + str(self.qubits) + " "

    @property
    def n_qubits(self):
        return len(self.qubits)

    @property
    def name(self):
        if self._name is None:
            return "M"
        else:
            return self._name

    @name.setter
    def name(self, other):
        self._name = other

    def qubit_names(self):
        return [self.name + "_" + str(k) for k, v in enumerate(self.qubits)]

    def __init__(self, qubits, name=None):
        self.qubits = sorted(qubits)  # qubit map
        self._name = name


class PhotonicPaths:

    @property
    def n_qubits(self):
        return self._n_qubits

    @property
    def qubits(self):
        return self._qubits

    @property
    def paths(self):
        return self._paths

    def __getitem__(self, item):
        return self.paths[item]

    def values(self):
        return self.paths.values()

    def keys(self):
        return self.paths.keys()

    def items(self):
        return self.paths.items()

    def get_path(self, path):
        return self._paths[path]

    def get_mode(self, path, mode):
        return self.get_path(path=path)[mode]

    def __init__(self, path_names: List[str], S: int, qpm: int, qubits: List[int] = None):
        """
        :param path_names: Name your paths, for example: path_names=['a','b','c']
        :param S: The spin number for each mode, the modes in each path will be: [-S, -(S-1) ..., 0, 1, ..., S]
        :param qpm: qubits_per_mode, 2 qubits allow for photonic occupation numbers of 0,1,2,3 etc
        :return:
        """

        self.S = S
        self.qpm = qpm

        if qpm <= 0:
            raise Exception("qpm: qubits_per_mode, has to be a positive non-zero integer, you gave %" % qpm)
        if S < 0:
            raise Exception(
                "S: the spin number of the photonic modes, has to be a positive integer, you gave %" % S)

        self._n_qubits = len(path_names) * (2 * S + 1) * qpm

        if qubits is None:
            qubits = range(self.n_qubits)  # will not run out

        self._qubits = qubits

        qubit_key = 0
        self._paths = dict()
        for path_name in path_names:
            path = dict()
            for mode_name in range(-S, S + 1, 1):
                path[mode_name] = PhotonicMode(qubits=[self.qubits[q] for q in range(qubit_key, qubit_key + qpm)],
                                               name=str(mode_name))
                qubit_key += qpm
            self._paths[path_name] = path

    def __repr__(self):
        result = "PhotonicPath with " + str(self.n_qubits) + " Qubits\n"
        for name, p in self.items():
            result += str(name) + " --> " + str(p) + "\n"
        return result

    def __eq__(self, other):
        if self.S != other.S:
            return False
        elif self.qpm != other.qpm:
            return False
        elif self.qubits != other.qubits:
            return False
        return True


class PhotonicStateVector:
    """
    Take the simulator result and keep track of the photonic modes
    """

    @classmethod
    def from_string(cls, paths: PhotonicPaths, string: str):
        """
        Terms are splitted by '+' so complex values like (x+iy)|...> will not work, you need to add Real and imaginary separately
        Or improve this consructor :-)
        :param paths:
        :param string:
        :return:
        """
        string = string.lstrip('+')
        result = cls(paths)
        terms = string.split('+')
        for term in terms:
            basis_state = dict()
            tmp = term.split("|")
            coeff = None
            if tmp[0] == '':
                coeff = 1.0
            else:
                coeff = complex(tmp[0])
            for i in range(1, len(tmp)):
                bs = tmp[i].rstrip().lstrip()
                path = bs[-1]
                occs = bs.split(">")[0]
                M = len(occs)
                S = (M - 1) // 2
                modes = dict()
                for j, m in enumerate(range(-S, S + 1)):
                    modes[m] = int(occs[j])
                basis_state[path] = modes
            result.add_basis_state(state=basis_state, coeff=coeff)
        return result

    def add_basis_state(self, state: Dict[str, Dict[int, int]], coeff=1):
        qubit_string = BitString.from_int(integer=0, nbits=self.n_qubits)
        for p, v in state.items():
            for m, occ in v.items():
                mode = self.get_mode(p, m)
                occ = BitString.from_int(integer=occ, nbits=mode.n_qubits)
                for i, q in enumerate(mode.qubits):
                    qubit_string[q] = occ[i]
        self._state += QubitWaveFunction.from_int(i=qubit_string, coeff=coeff)

    @property
    def endianness(self):
        return BitNumbering.MSB

    @property
    def n_modes(self):
        if self._paths is None:
            return 0
        for k, v in self._paths.items():
            return len(v)

    @property
    def n_paths(self):
        return len(self._paths)

    @property
    def n_qubits(self):
        result = 0
        for p in self._paths.values():
            for m in p.values():
                result += m.n_qubits
        return result

    @property
    def state(self):
        return self._state

    @property
    def paths(self):
        return self._paths

    def get_mode(self, path, mode):
        """
        :param path: Name of the path
        :param mode: Name of the mode
        :return: indices of qubits which represent the corresponding mode in the corresponding path
        """
        return self._paths[path][mode]

    def __init__(self, paths: PhotonicPaths, state: QubitWaveFunction = None):
        """
        :param paths: A dictionary containing all photonic paths, where each path contains dictionaries with modes
        :param qubit_state: A State in qubit representation -> A dictionary with integers (BitStrings) as keys
        """
        self._paths = paths
        self._state = state
        if state is None:
            self._state = QubitWaveFunction()

    def __repr__(self):
        threshold = 1.e-3
        result = ""
        nqubits = self.n_qubits
        for i, s in self._state.items():
            i.bits = nqubits
            if isclose(s, 0.0, atol=threshold):
                continue
            result += number_to_string(number=s)
            result += self.interpret_bitstring(i=i)
        return result

    def interpret_bitstring(self, i: BitString) -> str:
        result = ""
        for pname, p in self._paths.items():
            result += "|"
            for mname, m in p.items():
                nocc = BitString.from_array(array=[i[k] for k in m.qubits], nbits=self.n_qubits)
                result += str(nocc.integer)
            result += ">_" + str(pname)
        return result

    def __eq__(self, other):
        return self._paths == other._paths and self._state == other._state

    def __rmul__(self, other):
        return PhotonicStateVector(paths=self._paths, state=other * deepcopy(self._state))

    def __iadd__(self, other):
        assert (self.paths == other.paths)
        self._state += other.state
        return self

    def inner(self, other):
        return self._state.inner(other._state)

    def plot(self, title: str = None, label: str=None, filename: str = None):
        from matplotlib import pyplot as plt

        if title is not None:
            plt.title(title)
        plt.ylabel("counts")
        plt.xlabel("state")
        values = []
        names = []
        for k, v in self._state.items():
            values.append(v)
            names.append(self.interpret_bitstring(i=k))
        plt.bar(names, values, label=label)
        if label is not None:
            plt.legend()
        if filename is not None:
            plt.savefig(filename, dpi=None, facecolor='w', edgecolor='w',
                        orientation='landscape', papertype=None, format=None,
                        transparent=False, bbox_inches='tight', pad_inches=0.1,
                        metadata=None)
            with open(filename+"_data", 'a+') as f:
                f.write("names \t\t values\n")
                for i,v in enumerate(values):
                    f.write(str(names[i]) + "\t\t"+ str(values[i])+"\n")
                f.write("end\n")
        else:
            plt.show


if __name__ == "__main__":
    pass
