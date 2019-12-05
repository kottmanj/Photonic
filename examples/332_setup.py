"""
This is the GHZ setup with optimized parameters
"""
import photonic # works with 9e2199848d2f1757ae3f78892e0912787aadf5dd
import tequila as tq # and corresponding acca734d6a6dcf70c19bc2711dc4ce23f91ef242

# parameters
S = 1
qpm = 1 # 2
steps = 1 # 10

# convenience
a = "a"
b = "b"
c = "c"
d = "d"

if __name__ == "__main__":
    setup = photonic.PhotonicSetup(pathnames=[a, b, c, d], qpm=qpm, S=S)

    setup.prepare_SPDC_state(path_a=a, path_b=b)
    setup.prepare_SPDC_state(path_a=c, path_b=d)

    setup.add_beamsplitter(path_a=b, path_b=c, t=0.25, steps=steps)
    setup.add_doveprism(path=b, t=1.0)
    setup.add_beamsplitter(path_a=b, path_b=c, t=0.25, steps=steps)

    #setup.add_mirror(path=b) # add this for the ++- 000 +-+ 332 state
    #setup.prepare_332_state(path_a=b, path_b=c, path_c=d, daggered=True)

    setup.add_one_photon_projector(path=a, daggered=True, delete_active_path=True)

    setup.export_to_qpic(filename="332_setup")

    wfn = setup.simulate_wavefunction(simulator=tq.simulators.SimulatorCirq())

    projected = photonic.PhotonicStateVector(state=setup.heralding(wfn.state), paths=setup.heralding.reduced_paths)
    heralder = photonic.elements.PhotonicHeralder(paths=projected.paths)
    heralded = photonic.PhotonicStateVector(state=heralder(projected.state), paths=projected.paths)

    print("full-wfn\n", wfn)
    print("projected\n", projected)
    print("heralded \n", heralded)