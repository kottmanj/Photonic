from photonic import PhotonicSetup
from openvqe import dataclass
from openvqe.circuit import Variable, gates
from openvqe.simulator.simulator_cirq import SimulatorCirq
from matplotlib import pyplot as plt

import multiprocessing as mp


def read_dictionary(filename: str, d: dict = None):
    if d is None:
        d = {}
    with open(filename, 'r') as f:
        for line in f:
            (key, val) = line.strip().split(':')
            d[str(key).strip()] = int(val.strip())
    return d


@dataclass
class ExecuteWrapper:
    trotter_steps: int = 1
    randomize: bool = True
    randomize_component_order: bool = True  # no effect for S=0
    join_components: bool = True  # no effect for S=0
    samples: int = 1
    runs: int = 100
    value: float = 0.0
    steps: int = 25
    nproc: int = None

    @classmethod
    def from_file(cls, filename):
        data = read_dictionary(filename=filename)
        return cls(**data)

    def __call__(self, *args, **kwargs):
        """
        :param value: beam-splitter parameter -> defines the angle as phi = i*pi*value
        :return:
        """

        t = Variable(name="t", value=self.value)  # beam splitter angle, phi = i*pi*t

        setup = PhotonicSetup(pathnames=['a', 'b'], S=0, qpm=2)

        # the beam splitter is parametrized as phi=i*pi*t
        setup.add_beamsplitter(path_a='a', path_b='b', t=t,
                               steps=self.trotter_steps,
                               randomize_component_order=self.randomize_component_order,
                               join_components=self.join_components,
                               randomize=self.randomize)
        # will be automatized soon
        # currently: You will need to adapt this to S and qpm
        disentangler = gates.X(0) + gates.H(0) + gates.X(2) + gates.X(target=2, control=0)
        setup.add_circuit(disentangler.dagger())

        initial_state = "|1>_a|1>_b"
        counts = setup.run(samples=self.samples, initial_state=initial_state)
        try:
            return counts.state[0]
        except:
            return 0


def landscape_plotter(landscape, values, filename, label="HOM Parameter Landscape"):
    with open(filename + "_data", "a+") as file:
        file.write("landscape:\n")
        file.write(str(landscape))
        file.write("values:\n")
        file.write(str(values))

    plt.plot(values, landscape, label=label)
    plt.legend()
    plt.savefig(filename + ".pdf")


import sys

if __name__ == "__main__":

    arr = sys.argv[1].split(',')
    filename = None
    for a in arr:
        if 'filename=' in a:
            filename = a.split('=')[1]
    if filename is not None:
        print("found filename=", filename)
        # initialize parameters
        param = ExecuteWrapper.from_file(filename=filename)
        print("parameters are\n", param)
    else:
        raise Exception("give a filename when you call as python ... filename=...")

    nproc = param.nproc

    print("CPU Count is: ", mp.cpu_count())
    if nproc is None:
        nproc = mp.cpu_count()
    pool = mp.Pool(processes=max(1, min(nproc, mp.cpu_count())))
    print(pool._processes, " processes in the pool\n")

    landscape = []
    values = []
    for step in range(param.steps):
        value = 0.0 + step / param.steps * 1.0
        param.value = value
        overlap = sum(pool.map(func=param, iterable=range(0, param.runs)))
        landscape.append(overlap)
        values.append(value)

    output="hom_ts_"+str(param.trotter_steps)+"_rand_"+str(param.randomize)
    label="trotter steps: " + str(param.trotter_steps) + "\n" + "randomized: " + str(bool(param.randomize))
    landscape_plotter(landscape=landscape, values=values, filename=output, label=label)
