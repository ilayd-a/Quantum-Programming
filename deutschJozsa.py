from qiskit import QuantumCircuit
from qiskit_aer import Aer

def oracle_constant(qc):
    return qc

def oracle_balanced(qc):
    qc.cx(0,3)

def deutsch_jozsa(oracle, label):
    qc = QuantumCircuit(4,3)
    qc.x(3)
    qc.h([0,1,2,3])
    oracle(qc)
    qc.h([0,1,2])
    qc.measure([0,1,2],[0,1,2])

    backend = Aer.get_backend('qasm_simulator')
    job = backend.run(qc, shots=1024)
    result = job.result()
    counts = result.get_counts()

    print(f"{label} measurement results: {counts}\n")
    return counts


def run_tests():
    print("\n--- Running Deutsch–Jozsa Tests ---")

    counts_const = deutsch_jozsa(oracle_constant, "Constant Oracle")
    if list(counts_const.keys()) == ['000']:
        print("Constant test passed: always measured 000\n")
    else:
        print("Constant test failed\n")

    counts_bal = deutsch_jozsa(oracle_balanced, "Balanced Oracle")
    if '000' not in counts_bal:
        print("Balanced test passed: never measured 000\n")
    else:
        print("Balanced test failed\n")


run_tests()
