from photonic import PhotonicSetup, PhotonicStateVector
import numpy

if __name__ == "__main__":
    S = 1
    qpm = 2
    setup = PhotonicSetup(pathnames=['a', 'b'], S=S, qpm=qpm)
    state = PhotonicStateVector.from_string(paths=setup.paths, string="0.5774|001>_a|111>_b+0.5774|010>_a|111>_b+0.5774|100>_a|111>_b")
    setup.prepare_unary_type_state(state=state)
    setup.add_one_photon_projector(path='a', angles=[1.2309594173407747, 1.5707963267948966])

    wfn = setup.simulate_wavefunction()
    print("wfn=", wfn)
    setup.print_circuit()

    counts = setup.run(samples=100)

    # should result in only the |111>_a state
    print("counts=", counts)
    counts.plot()
