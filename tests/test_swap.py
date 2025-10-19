import qiskit
from qiskit_aer import Aer

A = qiskit.QuantumRegister(4)
B = qiskit.QuantumRegister(4)


def prob_full_swap(qc, A, B, c, bit_indices=(0, 1, 2, 3)):
    qc.h(c)

    for i in bit_indices:
        qc.cswap(c, A[i], B[i])


anc = qiskit.AncillaRegister(1, "anc")


qc = qiskit.QuantumCircuit(A, B, anc)

qc.x(A[1])  # 0010
qc.x(B[2])  # 0100

prob_full_swap(qc, A, B, anc[0], bit_indices=(0, 1, 2, 3))

qc.measure_all()
backend = Aer.get_backend("qasm_simulator")
job = backend.run(qc, shots=1024)
result = job.result()
counts = result.get_counts(qc)

print(qc.draw())

for outcome in counts:
    a_bits = outcome[5:9]
    b_bits = outcome[1:5]
    a_decimal = int(a_bits[::-1], 2)
    b_decimal = int(b_bits[::-1], 2)
    print(f"A: {a_decimal}, B: {b_decimal}, Counts: {counts[outcome]}")
