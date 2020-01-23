from photonic import PhotonicSetup

if __name__ == "__main__":
    S = 1  # Modes will run from -S ... 0 ... +S
    qpm = 2  # Qubits per mode

    setup = PhotonicSetup(pathnames=['a', 'b', 'c'], S=S, qpm=qpm)
    setup.prepare_332_state(path_a='a', path_b='b', path_c='c', daggered=False)
    wfn = setup.simulate_wavefunction()

    print("|332> = ", wfn)

