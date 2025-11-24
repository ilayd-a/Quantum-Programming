import pennylane as qml
from pennylane import numpy as np
from collections import Counter

# Part (c): Define Hamiltonian from part (b)

coeffs = [
    1.0,          # Z1
    0.5,          # Z2
    1.0,          # Z3
    0.5,          # Z4
    -0.5,         # Z1 Z2
    -1.0,         # Z1 Z4
    -1.0,         # Z2 Z3
    -0.5          # Z3 Z4
]

ops = [
    qml.PauliZ(0),
    qml.PauliZ(1),
    qml.PauliZ(2),
    qml.PauliZ(3),
    qml.PauliZ(0) @ qml.PauliZ(1),
    qml.PauliZ(0) @ qml.PauliZ(3),
    qml.PauliZ(1) @ qml.PauliZ(2),
    qml.PauliZ(2) @ qml.PauliZ(3)
]

H = qml.Hamiltonian(coeffs, ops)


# Ansatz: RY on each qubit + full CNOT entangling chain


n_qubits = 4
dev = qml.device("default.qubit", wires=n_qubits)

def ansatz(theta):
    # RY rotations
    for i in range(n_qubits):
        qml.RY(theta[i], wires=i)
    # CNOT chain (0→1→2→3)
    for i in range(n_qubits - 1):
        qml.CNOT(wires=[i, i+1])

@qml.qnode(dev)
def cost(theta):
    ansatz(theta)
    return qml.expval(H)

# Run VQE optimization

theta = np.random.uniform(0, 2*np.pi, n_qubits, requires_grad=True)
opt = qml.GradientDescentOptimizer(stepsize=0.1)

print("Starting VQE Optimization...\n")

for step in range(100):
    theta, energy = opt.step_and_cost(cost, theta)
    if step % 10 == 0:
        print(f"Step {step}: Energy = {energy:.6f}")

print("\nEstimated ground-state energy (VQE) =", energy)


# Part (d): Sample optimized circuit to get bitstring


shots = 1000
dev_sample = qml.device("default.qubit", wires=n_qubits, shots=shots)

@qml.qnode(dev_sample)
def sample_circuit(theta):
    ansatz(theta)
    return qml.sample(wires=range(n_qubits))

# Sample 1000 shots
samples = sample_circuit(theta)

# Convert samples to tuples
bitstrings = [tuple(int(b) for b in sample) for sample in samples]

# Count frequencies
counts = Counter(bitstrings)

print("\nSampled bitstring counts:")
for bstring, count in counts.most_common():
    print(f"{bstring}: {count}")

# Most frequent bitstring — candidate solution
best_quantum = max(counts, key=counts.get)
print("\nMost frequent sampled bitstring (quantum):", best_quantum)
