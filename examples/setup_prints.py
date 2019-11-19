from photonic import PhotonicSetup
from openvqe.circuit import Variable, gates
from openvqe.circuit.qpic import export_to_pdf

if __name__ == "__main__":
    S = 1  # Modes will run from -S ... 0 ... +S
    qpm = 1  # Qubits per mode

    t = Variable(name="\\theta", value=1.0)
    setup = PhotonicSetup(pathnames=['a', 'b'], S=S, qpm=qpm)
    setup.add_beamsplitter(path_a='a', path_b='b', t=t)
    setup.export_to_qpic(filename="bs")
    export_to_pdf(filename="bs", circuit="bs")
    export_to_pdf(circuit=setup.setup, filename="bs_full")

    S = 1  # Modes will run from -S ... 0 ... +S
    qpm = 2  # Qubits per mode

    setup = PhotonicSetup(pathnames=['a', 'b'], S=S, qpm=qpm)
    setup.prepare_SPDC_state(path_a='a', path_b='b')
    setup.export_to_qpic(filename="spdc")
    export_to_pdf(filename="spdc", circuit="spdc")
    export_to_pdf(circuit=setup.setup, filename="spdc_full")

    t = Variable(name="\\phi", value=1.0)
    setup = PhotonicSetup(pathnames=['a'], S=S, qpm=qpm)
    setup.add_doveprism(path='a', t=t)
    setup.export_to_qpic(filename="dove")
    export_to_pdf(filename="dove", circuit="dove")
    export_to_pdf(circuit=setup.setup, filename="dove_full")

    t0 = Variable(name="\\phi_0", value=1.0)
    t1 = Variable(name="\\phi_1", value=1.0)
    setup = PhotonicSetup(pathnames=['a'], S=S, qpm=qpm)
    setup.add_parametrized_one_photon_projector(path='a', angles=[t0,t1])
    setup.export_to_qpic(filename="projector")
    export_to_pdf(filename="projector", circuit="projector")
    export_to_pdf(circuit=setup.setup, filename="projector_full")

    setup = PhotonicSetup(pathnames=['a'], S=S, qpm=qpm)
    setup.add_hologram(path='a')
    setup.export_to_qpic(filename="hologram")
    export_to_pdf(filename="hologram", circuit="hologram")
    export_to_pdf(circuit=setup.setup, filename="hologram_full")


    t = Variable(name="t", value=0.25)  # beam splitter angle, phi = i*pi*t
    setup = PhotonicSetup(pathnames=['a', 'b'], S=0, qpm=2)
    # the beam splitter is parametrized as phi=i*pi*t
    setup.add_beamsplitter(path_a='a', path_b='b', t=t)
    # will be automatized soon
    # currently: You will need to adapt this to S and qpm
    disentangler = gates.X(0) + gates.H(0) + gates.X(2) + gates.X(target=2, control=0)
    setup.add_circuit(disentangler.dagger())
    name="optimization_strategy_overlap_example"
    setup.export_to_qpic(filename=name)
    export_to_pdf(filename=name, circuit=name)
    setup = PhotonicSetup(pathnames=['a', 'b'], S=0, qpm=2)
    setup.add_circuit(disentangler.dagger())
    setup.export_to_qpic(filename="disentangler")
    export_to_pdf(filename=name, circuit="disentangler")
    export_to_pdf(circuit=setup.setup, filename="disentangler_full")

    setup = PhotonicSetup(pathnames=['a', 'b'], S=0, qpm=2)
    setup.add_beamsplitter(path_a='a', path_b='b', t=Variable(name="\\theta", value=1.0))
    name = "hom_setup"
    setup.export_to_qpic(filename=name)
    export_to_pdf(filename=name, circuit=name)
    export_to_pdf(filename=name+"_full", circuit=setup.setup)

    setup = PhotonicSetup(pathnames=['a', 'b'], S=S, qpm=qpm)
    setup.add_beamsplitter(path_a='a', path_b='b', t=0.25)
    setup.add_doveprism(path='a', t=1.0)
    setup.add_beamsplitter(path_a='a', path_b='b', t=0.25)
    name = "parity_sorter"
    setup.export_to_qpic(filename=name)
    export_to_pdf(filename=name, circuit=name)

    setup = PhotonicSetup(pathnames=['a', 'b', 'c', 'd'], S=S, qpm=qpm)
    setup.prepare_SPDC_state(path_a='a', path_b='b')
    setup.prepare_SPDC_state(path_a='c', path_b='d')
    setup.add_beamsplitter(path_a='b', path_b='c', t=0.25)
    setup.add_doveprism(path='c', t=1.0)
    setup.add_beamsplitter(path_a='b', path_b='c', t=0.25)
    setup.add_one_photon_projector(path='a', daggered=True, delete_active_path=True)
    parameters = setup.extract_parameters()
    print("parameters:\n", parameters)
    setup.export_to_qpic(filename="332_setup")
    export_to_pdf(filename="332_setup", circuit="332_setup")





