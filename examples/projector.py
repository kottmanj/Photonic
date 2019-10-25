from photonic import PhotonicSetup
import numpy

# {a: 48.6946861306418, b: 5.0522258898388115, c: 1.0471975511965979, d: 7.2104805251811985}
# {a: -1.5707963267948966, b: -1.2309594173407747}
if __name__ == "__main__":
    S = 1
    qpm = 2
    setup = PhotonicSetup(pathnames=['a'], S=S, qpm=qpm)
    setup.add_one_photon_projector(path='a', angles=[1.2309594173407747, 1.5707963267948966])
    wfn = setup.simulate_wavefunction()
    print("wfn=", wfn)
    setup.print_circuit()
