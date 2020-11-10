from photonic import PhotonicSetup

# Directly prepare the 332 state in the digital encoding using quantum gates
# This is used in the the last part of the optimization
# Note that this is not the optical setup

if __name__ == "__main__":
    S = 1  # Modes will run from -S ... 0 ... +S (orbital angular momentum)
    qpm = 2  # Qubits per mode

    setup = PhotonicSetup(pathnames=['a', 'b', 'c'], S=S, qpm=qpm)
    setup.prepare_332_state(path_a='a', path_b='b', path_c='c', daggered=False)

    print("preparation circuti:\n", setup.setup)

    wfn = setup.simulate_wavefunction()

    print("Photonic Wavefunction = ", wfn)
    print("Qubit Wavefunction = ", wfn.state)

