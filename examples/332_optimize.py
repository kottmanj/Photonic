from photonic import PhotonicSetup
import tequila as tq
import pickle

"""
Set The Parameters for the encoding here:
"""
# If you want to change S and qpm you need to think about new encodings for the P1 projector
S = 1  # Can not be changed for this example. Hamiltonians are wrong otherwise
qpm = 1  # Can not be changed for this example. Hamiltonians are wrong otherwise
trotter_steps = 1  # number of trotter steps for the BeamSplitter (for S=1 and qpm=1, one trotter step is fine)

if __name__ == "__main__":

    param_dove = tq.Variable(name="t")  # the dove prism is already defined in units of pi within PhotonicSetup
    angle0 = tq.numpy.pi*tq.Variable(name="angle0") # angles in units of pi
    angle1 = tq.numpy.pi*tq.Variable(name="angle1") # angles in units of pi

    # Use the PhotonicSetup helper class to initialize the mapped parametrized photonic setup
    setup = PhotonicSetup(pathnames=['a', 'b', 'c', 'd'], S=S, qpm=qpm)
    setup.prepare_SPDC_state(path_a='a', path_b='b')
    setup.prepare_SPDC_state(path_a='c', path_b='d')
    setup.add_beamsplitter(path_a='b', path_b='c', t=0.25, steps=trotter_steps)
    setup.add_doveprism(path='c', t=param_dove)
    setup.add_beamsplitter(path_a='b', path_b='c', t=0.25, steps=trotter_steps)
    setup.add_parametrized_one_photon_projector(path='a', angles=[angle0, angle1])

    # this is the mapped photonic setup
    U_pre = setup.setup

    # now we will add the optimization parts which are only done on the digital quantum computer
    setup = PhotonicSetup(pathnames=['a', 'b', 'c', 'd'], S=S, qpm=qpm)
    # we have included the 332 state preparation on the digital machine into the PhotonicSetup class
    # for convenience
    setup.prepare_332_state(path_a='b', path_b='c', path_c='d', daggered=False)
    # this is the circuit which would prepare the 332 state directly on the digital machine
    # we will use its inverse for the optimization
    U_post = setup.setup

    # This is the measurement efficient implementation of the compressed
    # one photon projector
    U_p = tq.gates.QCircuit()
    path_qubits = [[3,4,5],[6,7,8],[9,10,11]]
    i = 12
    p_qubits = []
    for qubits in path_qubits:
        t = qubits[-1]
        encode = tq.gates.QCircuit()
        for q in qubits:
            if q == t:
                continue
            else:
                encode += tq.gates.X(target=t,control=q)
        U_p += encode
        U_p += tq.gates.X(target=i, control=t)
        U_p += tq.gates.X(target=i)
        U_p += encode.dagger()
        p_qubits.append(i)
        i+=1
    
    p0_qubits = [0,1,2]
    h_qubits = [3,4,5,6,7,8,9,10,11]
    p1_qubits = [12,13,14]

    # this is the full circuit
    U = U_pre + U_p + U_post.dagger()

    # here we construct the hamiltonians/measurement instructions for the
    # abstract expectation values
    # Qp is the tequila shortcut for 0.5(1 + Z)
    P0 = tq.paulis.Qp(qubit=p0_qubits)

    # this minus sign will take the fidelity form [0,1] to [0,-1]
    # so that we can do minimization in order to maximize it
    H = -tq.paulis.Qp(qubit=h_qubits)

    P1 = tq.paulis.Qp(qubit=p1_qubits)

    # form the abstract expectation values
    E0 = tq.ExpectationValue(H=P0*H*P1, U=U)
    E1 = tq.ExpectationValue(H=P0*P1, U=U)
    # form the objective to optimize
    O = E0/E1
    print(O)

    # (in case you do not want to do the optimization)
    # Since we already know the real minimum we can test it here
    # In case you're beeing curious: E0 gives you information about the countrate of your setup
    # So in prinicple that can be optimized as well
    variables = {'t':1.0, 'angle0': 0.5, 'angle1': -1.0}
    F = tq.simulate(O, variables)
    print("Optimimal Angles: ", variables)
    print("E0=", tq.simulate(E0, variables))
    print("E1=", tq.simulate(E1, variables))
    print("F=-E0/E1=", -F)

    # initialize starting conditions you want to have
    # this one here is not unrealistic and will lead to convergence
    # starting conditions are better than in the paper in order to speed up the demo here
    # We recommend having qulacs installed for this optimization
    # you can pass: backend="qulacs" to minimize in order to make sure qulacs is used
    # if it is installed tequila should pick it automatically
    # see the tequila tutorials for more
    values={'t':0.5, 'angle0':0.5 , 'angle1': -0.5}
    result = tq.minimize(tol=1.e-3, initial_values=values, objective=O, method="BFGS", silent=False)

    # lets keep the history
    with open("optimize.pickle", "wb") as f:
        pickle.dump(result.history, f, pickle.HIGHEST_PROTOCOL)

    # some illustration how to get data from the tequila history object
    print("energies\n",result.history.extract_energies())
    print("angle0\n",result.history.extract_angles(angle0))
    print("angle1\n",result.history.extract_angles(angle1))
    print("t\n",result.history.extract_angles(param_dove))
    print("grad_0\n",result.history.extract_gradients(angle0))
    print("grad_1\n",result.history.extract_gradients(angle1))
    print("grad_t\n",result.history.extract_gradients(param_dove))

    # convenience plots
    result.history.plot("energies", filename="history_energies.pdf")
    result.history.plot("angles", filename="history_angles.pdf")
