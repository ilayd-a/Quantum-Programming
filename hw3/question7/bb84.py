import random
import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

# Helper: Prepare a single qubit in Alice's state


def prepare_alice_qubit(bit, basis):
    qc = QuantumCircuit(1, 1)
    if bit == 1:
        qc.x(0)
    if basis == "X":
        qc.h(0)
    return qc

# Helper: Eve intercepts, measures, resends


def eve_intercept(qc, eve_basis, simulator):
    qc = qc.copy()
    measure_qc = QuantumCircuit(1, 1)
    measure_qc.compose(qc, inplace=True)
    if eve_basis == "X":
        measure_qc.h(0)
    measure_qc.measure(0, 0)

    result = simulator.run(transpile(measure_qc, simulator), shots=1).result()
    eve_bit = int(list(result.get_counts())[0])

    qc_new = QuantumCircuit(1, 1)
    if eve_bit == 1:
        qc_new.x(0)
    if eve_basis == "X":
        qc_new.h(0)

    return eve_bit, qc_new


# Helper: Bob measures received qubit

def bob_measure(qc, bob_basis, simulator):
    qc = qc.copy()
    measure_qc = QuantumCircuit(1, 1)
    measure_qc.compose(qc, inplace=True)
    if bob_basis == "X":
        measure_qc.h(0)
    measure_qc.measure(0, 0)

    result = simulator.run(transpile(measure_qc, simulator), shots=1).result()
    bob_bit = int(list(result.get_counts())[0])
    return bob_bit

# PART (c): Single BB84 Run


print("==============================================")
print("                 PART (c) OUTPUT              ")
print("==============================================")

simulator = Aer.get_backend("aer_simulator")
random.seed(42)

key_length = 10
p_int = 0.5

alice_bits  = [random.randint(0,1) for _ in range(key_length)]
alice_bases = [random.choice(["X","Z"]) for _ in range(key_length)]
bob_bases   = [random.choice(["X","Z"]) for _ in range(key_length)]
eve_intercepts = [random.random() < p_int for _ in range(key_length)]

eve_results = []
bob_results = []

for i in range(key_length):

    qc = prepare_alice_qubit(alice_bits[i], alice_bases[i])

    if eve_intercepts[i]:
        eve_basis = random.choice(["X","Z"])
        eve_bit, qc_to_bob = eve_intercept(qc, eve_basis, simulator)
        eve_results.append(eve_bit)
    else:
        eve_results.append(None)
        qc_to_bob = qc

    bob_bit = bob_measure(qc_to_bob, bob_bases[i], simulator)
    bob_results.append(bob_bit)

# Shared key
kept_indices = [i for i in range(key_length) if alice_bases[i] == bob_bases[i]]
shared_key = [alice_bits[i] for i in kept_indices if alice_bits[i] == bob_results[i]]

# Eve success rate
eve_hits = [
    int(eve_results[i] == alice_bits[i])
    for i in kept_indices
    if eve_results[i] is not None
]

eve_success_rate = (sum(eve_hits) / len(eve_hits)) if eve_hits else 0

print("Alice’s Bits:      ", alice_bits)
print("Alice’s Bases:     ", alice_bases)
print("Eve Intercepts:    ", eve_intercepts)
print("Eve’s Results:     ", eve_results)
print("Bob’s Bases:       ", bob_bases)
print("Bob’s Results:     ", bob_results)
print("Shared Key:        ", shared_key)
print(f"Eve’s Success Rate: {eve_success_rate*100:.2f}%")

# PART (d): Statistical Runs for QBER and Eve Success

print("\n==============================================")
print("                 PART (d) RESULTS             ")
print("==============================================")
# part (d) involves many Aer circuit executions and may take several minutes to run. This is expected due to repeated
# transpilation and measurement of quantum circuits inside Python loops.
key_length = 200  # enough for good statistics
p_int_values = [0, 0.25, 0.5, 0.75, 1]
num_trials = 30

qber_values = []
eve_success_values = []

for p_int in p_int_values:

    trial_qbers = []
    trial_eve_successes = []

    for _ in range(num_trials):
        alice_bits  = [random.randint(0,1) for _ in range(key_length)]
        alice_bases = [random.choice(["X","Z"]) for _ in range(key_length)]
        bob_bases   = [random.choice(["X","Z"]) for _ in range(key_length)]
        eve_flags   = [random.random() < p_int for _ in range(key_length)]

        bob_results = []
        eve_results = []

        for i in range(key_length):
            qc = prepare_alice_qubit(alice_bits[i], alice_bases[i])

            if eve_flags[i]:
                eve_basis = random.choice(["X","Z"])
                eve_bit, qc_to_bob = eve_intercept(qc, eve_basis, simulator)
                eve_results.append(eve_bit)
            else:
                eve_results.append(None)
                qc_to_bob = qc

            bob_bit = bob_measure(qc_to_bob, bob_bases[i], simulator)
            bob_results.append(bob_bit)

        kept = [i for i in range(key_length) if alice_bases[i] == bob_bases[i]]

        if kept:
            qber = sum(bob_results[i] != alice_bits[i] for i in kept) / len(kept)
        else:
            qber = 0

        eve_hits = [
            int(eve_results[i] == alice_bits[i])
            for i in kept
            if eve_flags[i] and eve_results[i] is not None
        ]

        eve_success = (sum(eve_hits) / len(eve_hits)) if eve_hits else 0

        trial_qbers.append(qber)
        trial_eve_successes.append(eve_success)

    qber_values.append(np.mean(trial_qbers))
    eve_success_values.append(np.mean(trial_eve_successes))

# Print results
print("p_int:", p_int_values)
print("QBER :", qber_values)
print("Eve success:", eve_success_values)

# Plot
plt.figure()
plt.plot(p_int_values, qber_values, "-o")
plt.xlabel("Interception Probability p_int")
plt.ylabel("QBER")
plt.title("QBER vs p_int (Qiskit)")
plt.grid(True)
plt.show()

plt.figure()
plt.plot(p_int_values, eve_success_values, "-o", color="orange")
plt.xlabel("Interception Probability p_int")
plt.ylabel("Eve Success Rate")
plt.title("Eve Success vs p_int (Qiskit)")
plt.grid(True)
plt.show()
