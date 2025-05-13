from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

NUM_SHOTS = 1024

def create_basic_quantum_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc

def execute_circuit(qc: QuantumCircuit) -> dict[str, int]:
    simulator = AerSimulator()
    result = simulator.run(qc, shots=NUM_SHOTS).result()
    return result.get_counts(qc)

def main():
    qc = create_basic_quantum_circuit()
    counts = execute_circuit(qc)
    print(counts)

if __name__ == "__main__":
    main()