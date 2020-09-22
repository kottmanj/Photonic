# Orquestra usable example of a boson sampling simulation
import tequila as tq
import photonic
import numpy
import json

def simulate_crespi_setup(trotter_steps=5, initial_state=None, samples=None, bs_parameters=None, phases=None):
   
    # Default is the same as in the Paper
    if bs_parameters is None:
        bs_parameters = [0.19,0.55,0.4,0.76,0.54,0.95,0.48,0.99,0.51,0.44]
    if phases is None:
        phases = [2.21,0.64,1.08,1.02,1.37,2.58,2.93,1.1]
    if initial_state is None:
        initial_state = "1.0|1>_a|1>_c|1>_e"
    
    setup = photonic.PhotonicSetup(pathnames=["a", "b", "c", "d", "e"], S=0, qpm=2)
    a = "a"
    b = "b"
    c = "c"
    d = "d"
    e = "e"

    # transform phases to pi*t form
    phase_parameters = [phase / numpy.pi for phase in phases]

    initial_state = setup.initialize_state(initial_state)
    U = tq.circuit.QCircuit()
    assert (len(initial_state.state.keys()) == 1)
    for k, v in initial_state.state.items():
        for i, v in enumerate(k.array):
            if v == 1:
                U += tq.gates.X(target=i)


    setup.add_circuit(U=U)
    
    setup.add_beamsplitter(path_a=a, path_b=b, t=bs_parameters[0], phi=0, steps=trotter_steps)
    setup.add_phase_shifter(path=a, t=-1)
    setup.add_phase_shifter(path=b, t=-1)
    
    setup.add_phase_shifter(path=b, t=-phase_parameters[0])
    setup.add_beamsplitter(path_a=b, path_b=c, t=bs_parameters[1], phi=0, steps=trotter_steps)
    
    setup.add_phase_shifter(path=a, t=-phase_parameters[1])
    setup.add_beamsplitter(path_a=a, path_b=b, t=bs_parameters[2], phi=0, steps=trotter_steps)
    
    setup.add_phase_shifter(path=c, t=-phase_parameters[2])
    setup.add_beamsplitter(path_a=c, path_b=d, t=bs_parameters[3], phi=0, steps=trotter_steps)
    
    setup.add_phase_shifter(path=c, t=-phase_parameters[3])
    setup.add_beamsplitter(path_a=b, path_b=c, t=bs_parameters[4], phi=0, steps=trotter_steps)
    
    setup.add_beamsplitter(path_a=d, path_b=e, t=bs_parameters[5], phi=0, steps=trotter_steps)
    
    setup.add_phase_shifter(path=b, t=-phase_parameters[4])
    setup.add_beamsplitter(path_a=a, path_b=b, t=bs_parameters[6], phi=0, steps=trotter_steps)
    
    setup.add_phase_shifter(path=c, t=-phase_parameters[5])
    setup.add_beamsplitter(path_a=c, path_b=d, t=bs_parameters[7], phi=0, steps=trotter_steps)
    
    setup.add_phase_shifter(path=b, t=-phase_parameters[6])
    setup.add_beamsplitter(path_a=b, path_b=c, t=bs_parameters[8], phi=0, steps=trotter_steps)
    
    setup.add_phase_shifter(path=b, t=-phase_parameters[7])
    setup.add_beamsplitter(path_a=a, path_b=b, t=bs_parameters[9], phi=0, steps=trotter_steps)
    
    U = setup.setup
    wfn = tq.simulate(U, samples=samples)
    
    if samples is None:
        distribution = {k.integer:numpy.abs(v)**2 for k,v in wfn.state.items() }
    else:
        distribution = {k.integer:numpy.abs(v) for k,v in wfn.state.items() }
    
    message = "Boson Sampling Simulation"
    
    message_dict = {}
    message_dict["message"] = message
    message_dict["schema"] = "message"
    message_dict["distribution"] = distribution
    message_dict["parameters"] = {"trotter_steps":trotter_steps, "samples":samples, "initial_state":str(initial_state)}
    
    with open("bs_distribution.json",'w') as f:
        f.write(json.dumps(message_dict, indent=2))

