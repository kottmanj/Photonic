"""
This is the GHZ setup with optimized parameters
"""
import photonic

# parameters
S = 1
qpm = 1
steps = 10

# convenience
a = "a"
b = "b"
c = "c"
d = "d"

def filter_projected(state: photonic.PhotonicStateVector):
    result = dict()

    for k,v in state.state.items():
        string = state.interpret_bitstring(i=k)
        if "|000>_a" in string:
            result[k] = v

    return photonic.PhotonicStateVector(paths=state.paths, state=result)

if __name__ == "__main__":
    setup = photonic.PhotonicSetup(pathnames=[a, b, c, d], qpm=qpm, S=S)

    setup.prepare_SPDC_state(path_a=a, path_b=b)
    setup.prepare_SPDC_state(path_a=c, path_b=d)

    setup.add_beamsplitter(path_a=b, path_b=c, t=0.25, steps=steps)
    setup.add_doveprism(path=c, t=1.0)
    # setup.add_phase_shifter(path=b, t=1.0)
    setup.add_beamsplitter(path_a=b, path_b=c, t=-0.25, steps=steps)
    # setup.add_hologram(path=a)
    # setup.add_hologram(path=a)
    # setup.add_beamsplitter(path_a=a, path_b=b, t=0.25, steps=steps)

    setup.add_one_photon_projector(path=a)

    setup.export_to_qpic(filename="ghz_setup")

    wfn = setup.simulate_wavefunction()
    print("full-wfn\n", wfn)
    print("projected:\n", filter_projected(state=wfn))
