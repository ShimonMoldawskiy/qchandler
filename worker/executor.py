from qiskit.qasm3 import loads as qasm3_loads
from qiskit_aer import AerSimulator

from shared.exceptions import UnrecoverableTaskError

NUM_SHOTS = 1024

class QuantumCircuitExecutor:
    def __init__(self, payload: dict):
        try:
            self._qc = qasm3_loads(payload["qasm"])
        except KeyError:
            raise UnrecoverableTaskError("Payload must contain a 'qasm' key.")
        except Exception as e:
            raise UnrecoverableTaskError(f"Failed to load QASM: {e}")

    def execute(self) -> dict[str, int]:
        simulator = AerSimulator()
        result = simulator.run(self._qc, shots=NUM_SHOTS).result()
        return result.get_counts(self._qc)

