import random
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector


def print_state(qc, label):
    try:
        state = Statevector.from_instruction(qc)
        print(f"\n{label}:")
        for i, amp in enumerate(state):
            if abs(amp) > 1e-4:
                print(f"{amp.real:+.4f}{amp.imag:+.4f}j |{format(i, '05b')[::-1]}>")
    except Exception:
        print(f"(Skipped state print for '{label}' due to classical conditions)")


def bitFlipPhase(error_type="bit"):
    qr = QuantumRegister(5, name="q")
    cr_result = ClassicalRegister(1, name="result")
    cr_syndrome = ClassicalRegister(2, name="syndrome")
    qc = QuantumCircuit(qr, cr_result, cr_syndrome)

    error_qubit = random.randint(0, 2)
    print(f"Error type: {error_type}, qubit: {error_qubit}")

    qc.h(0)
    qc.cx(0, 1)
    qc.cx(0, 2)
    if error_type == "phase":
        qc.h([0, 1, 2])
    print_state(qc, "Initial encoded state")

    if error_type == "bit":
        qc.x(error_qubit)
    else:
        qc.z(error_qubit)
    print_state(qc, f"After Introducing {error_type.capitalize()} Flip on Qubit {error_qubit}")

    if error_type == "bit":
        qc.cx(0, 3)
        qc.cx(1, 3)
        qc.cx(0, 4)
        qc.cx(2, 4)
        qc.measure([3, 4], cr_syndrome)

        with qc.if_test((cr_syndrome, 1)):
            qc.x(1)
        with qc.if_test((cr_syndrome, 2)):
            qc.x(2)
        with qc.if_test((cr_syndrome, 3)):
            qc.x(0)

    else:
        qc.h([0, 1, 2])
        qc.cx(0, 3)
        qc.cx(1, 3)
        qc.cx(0, 4)
        qc.cx(2, 4)
        qc.measure([3, 4], cr_syndrome)

        with qc.if_test((cr_syndrome, 1)):
            qc.x(1)
        with qc.if_test((cr_syndrome, 2)):
            qc.x(2)
        with qc.if_test((cr_syndrome, 3)):
            qc.x(0)

        qc.h([0, 1, 2])

    if error_type == "phase":
        qc.h([0, 1, 2])

    qc.cx(0, 2)
    qc.cx(0, 1)
    qc.h(0)
    qc.barrier()
    qc.measure(0, cr_result)

    sim = AerSimulator()
    t_qc = transpile(qc, sim)
    result = sim.run(t_qc, shots=1024).result()
    counts = result.get_counts()
    print("Final measurement counts:", counts)
    print("Initial state was |+>, which becomes |0> after decoding.")
    print("A successful run should measure '0' almost exclusively in the 'result' bit.")
    return qc


def test_bitFlipPhase(trials):
    """Run repeated trials for both bit-flip and phase-flip codes."""
    sim = AerSimulator()
    print(f"\n--- Running {trials} trials for each error type ---")

    for error_type in ["bit", "phase"]:
        print(f"\n--- Testing {error_type}-flip code ---")
        success = 0
        for _ in range(trials):
            qc = bitFlipPhase(error_type)
            t_qc = transpile(qc, sim)
            result = sim.run(t_qc, shots=256).result()
            counts = result.get_counts()
            correct = sum(v for k, v in counts.items() if k.endswith('0'))
            wrong = sum(v for k, v in counts.items() if k.endswith('1'))
            if correct > wrong:
                success += 1
        print(f"✓ {error_type.capitalize()}-flip success rate: {success}/{trials} "
              f"({success/trials*100:.1f}%)")


qc = test_bitFlipPhase(trials=5)
