from photonic import PhotonicStateVector, PhotonicSetup
from numpy import pi, sqrt

"""
Ignore this, was just for making the plots in the channel a bit faster
"""

class DoIt:
    def __init__(self, S, qpm):
        self.S = S
        self.qpm = qpm

    def __call__(self, steps):
        if steps == 0:
            steps = 1

        setup = PhotonicSetup(pathnames=['a', 'b'], S=self.S, qpm=self.qpm)
        setup.BeamSplitter(path_a='a', path_b='b', phi=pi / 4, steps=steps)
        start = PhotonicStateVector.from_string(paths=setup.paths, string="1.0|1>_a|1>_b")
        fac = str(1.0 / sqrt(2))
        expected = PhotonicStateVector.from_string(paths=setup.paths,
                                                   string=fac + "|2>_a|0>_b+-" + fac + "|0>_a|2>_b")
        end = setup.simulate_wavefunction(initial_state=start)
        return abs(end.inner(expected)) ** 2


if __name__ == "__main__":

    import multiprocessing as mp

    print("CPU Count is: ", mp.cpu_count())
    pool = mp.Pool(processes=max(1, mp.cpu_count() - 2))
    print(pool._processes, " processes in the pool\n")

    maxstep = 25
    stepsize = 5
    qpm = 2
    results = []
    for S in [0, 1, 2]:
        for qpm in [2, 3]:
            fidelities = pool.map(func=DoIt(S=S, qpm=qpm), iterable=range(0, maxstep, stepsize))
            result = {'S': S, 'qpm': qpm, 'F': fidelities}
            results.append(result)
            break
        break

    print("Results:\n")
    print("stepsize = ", stepsize)
    print("maxstep  = ", maxstep)
    for result in results:
        print("--------------------------------")
        print("S=", S, " qpm=", qpm)
        print("--------------------------------")
        print("\nsteps\t\tfidelity\n")
        for i, F in enumerate(result['F']):
            print(1 + i * stepsize, "\t\t", F)

    from matplotlib import pyplot as plt

    plt.title('Hong-Ou-Mandel Test')
    plt.ylabel("Fidelity")
    plt.xlabel("Trotter Steps")
    plt.xticks(range(maxstep, stepsize))
    for result in results:
        plt.plot(range(0, maxstep, stepsize), result['F'],
                 label="S=" + str(result['S']) + ", qpm=" + str(result['qpm']))
    plt.legend()
    plt.savefig("hhm.pdf", dpi=None, facecolor='w', edgecolor='w',
                orientation='landscape', papertype=None, format=None,
                transparent=False, bbox_inches='tight', pad_inches=0.1,
                metadata=None)
