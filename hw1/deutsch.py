from qiskit import QuantumCircuit
from qiskit_aer import Aer

def oracle_constant(qc):
    qc.x(1)

def oracle_balanced(qc):
    qc.x(0)
    qc.cx(0,1)
    qc.x(0)

def deutsch(oracle, label):
    qc = QuantumCircuit(2,1)
    qc.x(1)
    qc.h([0,1])
    oracle(qc)
    qc.h(0)
    qc.measure(0,0)

    backend = Aer.get_backend('qasm_simulator')
    job = backend.run(qc, shots=1024)
    result = job.result()
    counts = result.get_counts()

    print(f"{label} measurement results: {counts}\n")
    return counts

def run_tests():
    print("\n--- Running Deutsch Algorithm Tests ---\n")

    counts_const = deutsch(oracle_constant, "Constant f(x)=1")
    if list(counts_const.keys()) == ['0']:
        print("Constant test passed: always measured 0\n")
    else:
        print("Constant test failed\n")

    counts_bal = deutsch(oracle_balanced, "Balanced f(0)=1, f(1)=0")
    if list(counts_bal.keys()) == ['1']:
        print("Balanced test passed: always measured 1\n")
    else:
        print("Balanced test failed\n")


run_tests()