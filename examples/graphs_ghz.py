import tequila as tq
from photonic import PhotonicSetup, PhotonicStateVector
from dataclasses import dataclass
import numpy

@dataclass
class Edge:
    path_a:str = None
    path_b:str = None
    mode_a:int = None
    mode_b:int = None

    @property
    def name(self):
        return "{}{}_({})({})".format(str(self.path_a), str(self.path_b), str(self.mode_a), str(self.mode_b))

setup = PhotonicSetup(pathnames=['a', 'b', 'c', 'd'], S=1, qpm=1)

edges = []
modes = [-1,1]
vertices = ["a", "b", "c", "d"]
for i,v1 in enumerate(vertices[:-1]):
    for v2 in vertices[i+1:]:
        for m1 in modes:
            for m2 in modes:
                #if m1 != m2: continue
                edges.append(Edge(path_a=v1, path_b=v2, mode_a=m1, mode_b=m2))

print(len(edges), " edges")

for edge in edges:
    setup.add_edge(path_a=edge.path_a, path_b=edge.path_b, i=edge.mode_a, j=edge.mode_b, omega=edge.name)

print(setup)

U = setup.setup

Utarget = tq.gates.H(0)
Utarget += tq.gates.CNOT(0, 3)
Utarget += tq.gates.CNOT(3, 6)
Utarget += tq.gates.CNOT(6, 9)

Utarget += tq.gates.X(0)
Utarget += tq.gates.CNOT(0, 2)
Utarget += tq.gates.X(0)
Utarget += tq.gates.CNOT(2, 5)
Utarget += tq.gates.CNOT(5, 8)
Utarget += tq.gates.CNOT(8, 11)

Ups = tq.gates.CNOT(0, 12)
Ups+= tq.gates.CNOT(2, 12)
Ups+= tq.gates.CNOT(3, 13)
Ups+= tq.gates.CNOT(5, 13)
Ups+= tq.gates.CNOT(6, 14)
Ups+= tq.gates.CNOT(8, 14)
Ups+= tq.gates.CNOT(9, 15)
Ups+= tq.gates.CNOT(11, 15)
Hps = tq.paulis.Qm([12,13,14,15])

wfn = tq.simulate(Utarget)
pwfn = PhotonicStateVector(state=wfn, paths=setup.paths)
print(wfn)
print(pwfn)

P = tq.paulis.Qp([0,1,2,3,4,5,6,7,8,9,10,11])*tq.paulis.Qm([12,13,14,15])
Fidelity = tq.ExpectationValue(H=P, U=U+Ups+Utarget.dagger())
Ps = tq.ExpectationValue(H=Hps, U=U+Ups)

initial_weights = {w:0.0 for w in Fidelity.extract_variables()}

print(tq.simulate(Fidelity, variables=initial_weights))
print(tq.simulate(Ps, variables=initial_weights))

initial_weights["ab_(-1)(-1)"]=numpy.pi
initial_weights["cd_(-1)(-1)"]=numpy.pi
result = tq.minimize(method="cobyla", objective=-Fidelity/Ps, maxiter=5000, initial_values=initial_weights)
print(result.angles)
result = tq.minimize(method="bfgs", gradient="2-point", method_options={"eps":1.e-3}, objective=-Fidelity/Ps, maxiter=5000, initial_values=result.angles)

wfn = tq.simulate(U, result.angles)
pwfn = PhotonicStateVector(state=wfn, paths=setup.paths)
print(wfn)
print(pwfn)