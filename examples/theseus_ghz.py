import photonic
import numpy
import tequila as tq

setup = photonic.PhotonicSetup(pathnames=['a', 'b', 'c', 'd'], S=1, qpm=1)

setup.add_edge('a', 'b', -1, -1, ('a','b',-1,-1))
setup.add_edge('c', 'd', -1, -1, ('c','d',-1,-1))
setup.add_edge('a', 'c', 0, 0, ('a','c',0,0))
setup.add_edge('b', 'd', 0, 0, ('b','d',0,0))

U = setup.setup

variables = {k:numpy.pi/2 for k in U.extract_variables()}
wfn = tq.simulate(U, variables=variables)
ph_wfn = photonic.PhotonicStateVector(setup.paths, wfn)
print(ph_wfn)
asd=str(ph_wfn)
dsa=asd.split("+")
for i in dsa:
    print(i)

def prepare_ghz_state(phase=None):
    U = tq.gates.H(0)
    U+= tq.gates.CNOT(0,3)
    U+= tq.gates.CNOT(3,6)
    U+= tq.gates.CNOT(6,9)
    U+= tq.gates.X(0)
    U+= tq.gates.CNOT(0,1)
    U+= tq.gates.CNOT(1,4)
    U+= tq.gates.CNOT(4,7)
    U+= tq.gates.CNOT(7,10)
    U+= tq.gates.X(0)
    if phase is not None:
        U+= tq.gates.Rz(angle=phase,target=0)
    return U

U = prepare_ghz_state()

# Just to test
U.n_qubits=12
wfn = tq.simulate(U)
print(wfn)
print("U|0> = ", photonic.PhotonicStateVector(setup.paths,wfn))

# Construct the enocer for the simulated post-selection over anciallries
# Will recycle the unused qubit in the setup
# you can also change that to others, the tq simulation will
# detect unused qubits and rename everything
# acillaries are qubits 2,5,8,11
ancillaries=[2,5,8,11]
def make_encoder(ancillaries=[2,5,8,11]):
    U = tq.gates.CNOT(0,1)
    U += tq.gates.CNOT(1,ancillaries[0])
    U += tq.gates.CNOT(0,1)
    
    U += tq.gates.CNOT(3,4)
    U += tq.gates.CNOT(4,ancillaries[1])
    U += tq.gates.CNOT(3,4)

    U += tq.gates.CNOT(6,7)
    U += tq.gates.CNOT(7,ancillaries[2])
    U += tq.gates.CNOT(6,7)

    U += tq.gates.CNOT(9,10)
    U += tq.gates.CNOT(10,ancillaries[3])
    U += tq.gates.CNOT(9,10)

    U += tq.gates.X(ancillaries)

    return U

# make the setup with the encoding
U0 = setup.setup
U1 = make_encoder(ancillaries)
U2 = prepare_ghz_state().dagger()

# print the circuits to pdfs (qpic needs to be installed and might be problematic on macs and windows)
# just comment out if it makes trouble
tq.circuit.export_to(U0, "theseus_ghz_setup_0.pdf")
tq.circuit.export_to(U1, "theseus_ghz_setup_1.pdf")
tq.circuit.export_to(U2, "theseus_ghz_setup_2.pdf")
tq.circuit.export_to(U0+U1+U2, "theseus_ghz_setup.pdf")
# make a nicer representation by mapping the ancillas to the last qubits
qm = {0:0, 1:1, 2:8 , 3:2, 4:3, 5:9, 6:4 , 7:5, 8:10, 9:6, 10:7, 11:11  } 
tq.circuit.export_to((U0+U1+U2).map_qubits(qm), "theseus_ghz_setup_rearranged.pdf")


H = tq.paulis.Projector("1.0*|000000000000>")
P1 = tq.paulis.Qp(ancillaries)

# Normalized Fidelity
E1 = tq.ExpectationValue(U=U0+U1+U2, H=H)
# CountRate
E2 = tq.ExpectationValue(U=U0+U1,H=P1) 
1
# print out the circuit
# abstract tequila
# compile level on trotterization to ExpPaulis (qulacs)
# compile level up to primitive gates (cirq)
print(U0+U1+U2)
U = tq.compile(U0+U1+U2, backend="cirq").abstract_circuit
tq.circuit.export_to(U,"full_circuit_compiled_to_cirq.pdf")
U = tq.compile(U0+U1+U2, backend="qulacs").abstract_circuit
tq.circuit.export_to(U,"full_circuit_compiled_to_qulacs.pdf")

# Simulate with optimized variables
# testing
print("Simulate with variables ", variables)
print("non-normalized Fidelity: ", tq.simulate(E1, variables=variables))
print("count rate             : ", tq.simulate(E2, variables=variables))
print("normalized Fidelity    :", tq.simulate(E1/E2, variables=variables))

# Demonstration what happens without post selection
# i.e. no encoder used
Ex = tq.ExpectationValue(U=setup.setup+U2, H=H)
print("Fidelity without post-selection:", tq.simulate(Ex, variables=variables))

# This is some demonstration that we need to balance countrate and 
# fidelity optimization (did this also in the Theseus paper)
# There are some special features in this graph, i.e. it seems all valid states under post-selection are already only the two basis-states we need (but thats not guaranteed, in the old 332 example neglecting post-selection will for example not work, but we could ignore it here)
steps=25
F = E1/E2
C = E2
print("Some Testing:\n")
print("Parameter region where all parameters are the same value")
print("{:15} | {:25} | {:15} | {:25}".format("Parameter" ,"Normalized Fidelity", "Count Rate","Fidelity without PS"))
for x in [i/steps*2.0*numpy.pi for i in range(steps)]:
    variables={k:x for k in E1.extract_variables()}
    print("{:15} | {:25} | {:15} | {:25}".format(x, tq.simulate(F, variables=variables),tq.simulate(C, variables=variables), tq.simulate(Ex, variables=variables)))

# if the parameters vary the non-normalized fidelity is not the same as the count rate
# meaning now we have also valid states (one photon each path) that are not basis states of the state we are looking for
print("Some Testing:\n")
print("random parameters")
print("Parameter | Normalized Fidelity | Count Rate | Fidelity without PS\n")
for x in [i/steps*2.0*numpy.pi for i in range(steps)]:
    variables={k:numpy.random.uniform(0.0, 2.0*numpy.pi,1)[0] for k in E1.extract_variables()}
    print(x, " ", tq.simulate(F, variables=variables), " ", tq.simulate(C, variables=variables), tq.simulate(Ex, variables=variables))

# This is the actual optimization
print("lets optimize")
initial_values={k:0.4*numpy.pi for k in E1.extract_variables()}
result = tq.minimize(objective=1-F + (1-C), method="bfgs", initial_values=initial_values)

variables=result.angles
print("Optimization Result")
print("non-normalized Fidelity: ", tq.simulate(E1, variables=variables))
print("count rate             : ", tq.simulate(E2, variables=variables))
print("normalized Fidelity    : ", tq.simulate(E1/E2, variables=variables))



